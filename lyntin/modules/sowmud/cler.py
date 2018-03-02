# -*- coding: utf-8 -*-
from lyntin import exported, utils, ansi, settings
from lyntin.modules import modutils
from threading import Timer
import time
import cmds

class ClerBot():
  unmute_spell = u"освободить.разум"
  mass_heal_spell = u"массовое.исцеление"
  undrain_spell = u"слово.силы"
  unstone_spell = u"живое.прикосновение"
  summon_spell = u"призыв"

  myself = u"Дарсу"
  group_headers = [(utils.compile_regexp(u"r[^\s*?Имя\s+?Рядом$]"), "NEAR"),
                   (utils.compile_regexp(u"r[^\s*?Имя\s+?H\s+?Позиция\s+?Рядом\s+?Укр$]"), "HEALTH"),
                   (utils.compile_regexp(u"r[^\\s+?Имя\\s+?$]"), "INIT")]

  def __init__(self, cmd_engine):
    self.group_member_regexp = {
          "HEALTH": (utils.compile_regexp("r[^\s*(?P<num>\d+)\s*(?P<name>\S+)\s*(?P<hp>o+)\s*(?P<pos>(Стоит|Сражается|Сидит|Отдыхает))\s*(?P<near>Д|Н)\s*(?P<drain_level>Д|Н)\s*$]".decode("utf-8"), 1),
                     ClerBot.group_member_health),
          "INIT": (utils.compile_regexp("r[^\s*(?P<num>\d+)\s*(?P<name>\S+)\s*$]".decode("utf-8"), 1),
                   ClerBot.group_new_member),
          "NEAR": (utils.compile_regexp("r[^\s*(?P<num>\d+)\s*(?P<name>\S+)\s*(?P<near>Д|Н)\s*$]".decode("utf-8"), 1),
                   ClerBot.group_member_near),
          }

    self._palads = {u"Дальсен": False, u"Эжни": False}
    self._group_list = {}
    self._mode = None
    self._auto_summon = True
    self._cmd_engine = cmd_engine

  def get_mode(self):
    return self._mode

  def palad_mute(self, name, flag):
    try:
      self._palads[name] = flag
    except KeyError:
      exported.write_message(u"ClerBot: WARN: {0} is unknown palad".format(name))

    if flag:
      self.action()

  def group_reset(self):
    #self._group_list = {}
    pass

  def mode(self, mode):
    self._mode = mode
    if mode == "INIT":
      self._group_list = {}

  def group_member_near(self, match, colorline):
    num = match.group("num")
    name = match.group("name")
    near = (match.group("near") == u'Д')
    try:
      self._group_list[name].set_near(near)
    except KeyError:
      exported.write_message(u"ClerBot: WARN: {0} is unknown group member".format(name))
      self.group_new_member(match, colorline)
      self.group_member_near(match, colorline)

  def toggle_auto_summon(self):
    self._auto_summon = not self._auto_summon
    exported.write_message("Auto summon: {0}".format(self._auto_summon))

  def do_auto_summon(self):
    for name, char in self._group_list.items():
      if not char.is_near():
        #print "Summoning " + name + " {0}".format(flag)
        cmd = cmds.CastCmd(ClerBot.summon_spell, name)
        char.set_near(True)
        self._cmd_engine.put(cmd)
        return
    self._mode = None

  def on_appear(self, name):
    try:
      self._group_list[name].set_near(True)
    except KeyError:
      pass

  def group_member_health(self, match, colorline):
    num = match.group("num")
    name = match.group("name")
    hp = match.group("hp")
    position = match.group("pos")
    near = (match.group("near") == u'Д')
    drain = (match.group("drain_level") == u'Д')

    name = name.strip()

    try:
      self._group_list[name].update(len(hp), position, near, drain)
    except KeyError:
      exported.write_message(u"ClerBot: WARN: could not find group member {0}".format(name))

    # Detect stone curse
    tokens = ansi.split_ansi_from_text(colorline)
    tokens = map(unicode.strip, tokens)
    try:
      pos_index = tokens.index(position)
      pos_color = tokens[pos_index - 1]
    except ValueError:
      pos_color = ""

    #print u"At {0} the color is {1}, tokens being: {2}, position {3}.".format(name, pos_color.replace(chr(27), "^["), tokens, position)
    if ansi.is_color_token(pos_color):
      fg = pos_color
      if ((ansi.STYLEMAP["light yellow"] == fg[2:-1]) or
          (ansi.STYLEMAP["yellow"] == fg[2:-1])):
        self._group_list[name].set_stone_curse(True)

    if (len(hp) > 2):
      return ""
    else:
      return u"{0} is in danger, {1}\n".format(name, position)

  def group_new_member(self, match, colorline):
    num = match.group("num")
    name = match.group("name")
    self._group_list[name] = GroupMember(num, name)
    return ""

  def do_auto_heal(self):
    self.action()
    self._mode = None

  # This is the main AI of the cleric
  def action(self):
    cmd = ""

    for name, mute in self._palads.items():
      if mute:
        cmd = cmds.CastCmd(ClerBot.unmute_spell, name)
        self._palads[name] = False

    if cmd == "":
      heal_need_cnt_near = 0
      for name, char in self._group_list.items():
        if (char.hp() < 5) and char.is_near():
          heal_need_cnt_near = heal_need_cnt_near + 1

      if heal_need_cnt_near > 0:
        cmd = cmds.CastCmd(ClerBot.mass_heal_spell)

    try:
      if self._group_list[ClerBot.myself].position() == "SIT":
        self._cmd_engine.put(cmds.Cmd("stand"), True)
    except KeyError:
      exported.write_message("ClerBot: WARN: could not find myself in group")

    if cmd != "":
      self._cmd_engine.put(cmd)
      return

    # The least prioriry is to clean drain level and stone curse
    drained_cnt = 0
    drained_name = ""
    stone_cursed_cnt = 0
    stone_cursed_name = 0
    for name, char in self._group_list.items():
      if char.is_drained():
        drained_cnt = drained_cnt + 1
        drained_name = name
      if char.is_stone_cursed():
        stone_cursed_cnt = stone_cursed_cnt + 1
        stone_cursed_name = name

    if (drained_cnt < 3) and (drained_cnt > 0):
      self._cmd_engine.put(cmds.CastCmd(ClerBot.undrain_spell, drained_name))
    elif (stone_cursed_cnt < 3) and (stone_cursed_cnt > 0):
      self._cmd_engine.put(cmds.CastCmd(ClerBot.unstone_spell, stone_cursed_name))

  def on_prompt(self):
    if self._mode == "NEAR":
      self.do_auto_summon()
    if self._mode == "HEALTH":
      self.do_auto_heal()
    if self._mode == "INIT":
      members = u"Group: " + u", ".join(self._group_list.keys())
      exported.write_message(members)

      self._mode = None

  def mudfilter(self, text):
    colorline = utils.filter_cm(text)
    nocolorline = ansi.filter_ansi(colorline)

    if self._mode is not None:
      try:
        match = self.group_member_regexp[self._mode][0].search(nocolorline)
        if match:
          return self.group_member_regexp[self._mode][1](self, match, colorline)
      except KeyError:
        exported.write_message("ClerBot: WARN: the mode {0} is unknown".format(self._mode))

    if self._mode is None:
      for s, mode in ClerBot.group_headers:
        match = s.search(nocolorline)
        if match:
          self.mode(mode)
          return ""

    return text

  def status(self):
    print ""
    return "\n".join(self._group_list.keys())

  def group_list(self):
    return self._group_list

  def check(self):
    self._cmd_engine.put(cmds.GroupCheckHealthCmd())
    self.tick()

  def start(self):
    self.tick()

  def stop(self):
    self._timer.cancel()

  def tick(self):
    self._timer = Timer(2.5, ClerBot.check, [self])
    self._timer.start()

class GroupMember():
  positions = {u"Стоит": "STAND", u"Сражается": "FIGHT", u"Сидит": "SIT", u"Отдыхает": "REST"}

  def __init__(self, num, name):
    self._name = name
    self._near = True
    self._health = 5
    self._num = num
    self._position = "STAND"
    self._drain_level = False
    self._stone_curse = False

  def set_near(self, near):
    self._near = near

  def is_near(self):
    return self._near

  def is_drained(self):
    return self._drain_level

  def set_stone_curse(self, stone_curse):
    self._stone_curse = stone_curse

  def is_stone_cursed(self):
    return self._stone_curse

  def name(self):
    return self._name

  def position(self):
    return self._position

  def hp(self):
    return self._health

  def set_num(self, num):
    self._num = num

  def update(self, hp, position, near, drain_level):
    self._health = hp
    self._near = near
    self._drain_level = drain_level
    self._stone_curse = False
    try:
      self._position = GroupMember.positions[position]
    except KeyError:
      exported.write_message(u"ClerBot: WARN: {0} is unknown positionn".format(position))
