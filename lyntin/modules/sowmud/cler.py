# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from builtins import map
from builtins import object
from lyntin import exported, utils, ansi, settings
from lyntin.modules import modutils
from threading import Timer
import time
from . import cmds
from . import bot
from . import group
from . import events
import gc

def namestr(obj, namespace):
  return [name for name in namespace if namespace[name] is obj]

class ClerBot(bot.Bot):
  unmute_spell = u"освободить.разум"
  mass_heal_spell = u"массовое.исцеление"
  undrain_spell = u"слово.силы"
  unstone_spell = u"живое.прикосновение"

  group_headers = [(utils.compile_regexp(u"r[^\s*?Имя\s+?Рядом$]"), "NEAR"),
                   (utils.compile_regexp(u"r[^\s*?Имя\s+?H\s+?Позиция\s+?Рядом\s+?Укр$]"), "HEALTH"),
                   (utils.compile_regexp(u"r[^\\s+?Имя\\s+?$]"), "INIT")]

  def __init__(self, cmd_engine, event_classifier, myself):
    bot.Bot.__init__(self, cmd_engine, event_classifier, myself)

    cler_mod = ClerMod(cmd_engine, event_classifier, self._group_list)
    self.add_mod(cler_mod, "cler_mod")
    summon_mod = bot.AutoSummonMod(cmd_engine, event_classifier, self._group_list)
    self.add_mod(summon_mod, "summon_mod")

    self._handle_near = True

  def __del__(self):
    bot.Bot.__del__(self)
    gc.collect()
    refs = gc.get_referrers(self._mods["cler_mod"])
    #for r in refs:
    #  if type(r) == list:
    #    exported.write_message("Globals Referer: {0} - {1}".format(r, namestr(r, globals())))
    #    exported.write_message("Locals Referer: {0} - {1}".format(r, namestr(r, locals())))

    exported.write_message(str(gc.get_referrers(self._mods["cler_mod"])))
    #exported.write_message("ClerBot: DEBUG: deleting ClerBot")
    #for r in refs:
    #  if type(r) == list:
    #    exported.write_message("ClerBot: DEBUG: list referrer")
    #    exported.write_message(str(gc.get_referrers(r)))
    #exported.write_message("ClerBot: DEBUG: done listed referrers")

  def start(self):
    self._mods["cler_mod"].start()

  def stop(self):
    self._mods["cler_mod"].stop()

class GroupCheckHealthCmd(cmds.Cmd):
  def __init__(self):
    cmds.Cmd.__init__(self, u"pgroup здоровье позиция рядом украсть.душу")

class ClerMod(object):
  def __init__(self, cmd_engine, event_classifier, group_list):
    exported.write_message("ClerMod: DEBUG: init {0}".format(self))
    factory = group.GroupColumnFactory()
    healView = group.GroupView()
    healView.add_column(factory.get_num_column())
    healView.add_column(factory.get_name_column())
    healView.add_column(factory.get_hp_column())
    healView.add_column(factory.get_position_column())
    healView.add_column(factory.get_near_column())
    healView.add_column(factory.get_drain_column())

    self._mode = False
    event_classifier.add_event("group_health_header", healView.header())
    event_classifier.add_event("group_health_member", healView.member())
    event_classifier.add_callback("group_health_header", self)
    event_classifier.add_callback("group_health_member", self)
    event_classifier.add_callback("prompt", self)

    self._event_classifier = event_classifier
    self._group_list = group_list
    self._cmd_engine = cmd_engine

  def unregister(self):
    exported.write_message("ClerMod: DEBUG: unregistering {0}".format(self))
    self._event_classifier.remove_callback("prompt", self)
    self._event_classifier.remove_callback("group_health_member", self)
    self._event_classifier.remove_callback("group_health_header", self)
    self._event_classifier.remove_event("group_health_member")
    self._event_classifier.remove_event("group_health_header")

  def mode(self):
    if self._mode:
      return "HEALTH"

  def on_event(self, ev_type, match):
    if ev_type == "group_health_header":
      self._event_classifier.gag_current()
      self._mode = True

    if (ev_type == "group_health_member") and self._mode:
      self._event_classifier.gag_current()
      colorline = self._event_classifier.get_raw()
      self.group_member_health(match, colorline)

    if (ev_type == "prompt") and self._mode:
      self.action()
      self._mode = False

  def group_member_health(self, match, colorline):
    num = match.group("num")
    name = match.group("name")
    hp = match.group("hp")
    position = match.group("position")
    near = (match.group("near") == u'Д')
    drain = (match.group("drained") == u'Д')

    name = name.strip()

    try:
      self._group_list[name].update(position, near, len(hp), drain)
    except KeyError:
      exported.write_message(u"ClerBot: WARN: could not find group member {0}".format(name))

    # Detect stone curse
    tokens = ansi.split_ansi_from_text(colorline)
    tokens = list(map(str.strip, tokens))
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

    # if (len(hp) > 2):
    #   pass
    # else:
    #   return u"{0} is in danger, {1}\n".format(name, position)

  # This is the main AI of the cleric
  def action(self):
    cmd = ""

    #for name, mute in list(self._palads.items()):
    #  if mute:
    #    cmd = cmds.CastCmd(ClerBot.unmute_spell, name)
    #    self._palads[name] = False

    if cmd == "":
      heal_need_cnt_near = 0
      for name, char in list(self._group_list.items()):
        if (char.hp() < 5) and char.is_near():
          heal_need_cnt_near = heal_need_cnt_near + 1

      if heal_need_cnt_near > 0:
        cmd = cmds.CastCmd(ClerBot.mass_heal_spell)

    if cmd != "":
      self._cmd_engine.put(cmd)
      return

    # The least prioriry is to clean drain level and stone curse
    drained_cnt = 0
    drained_name = ""
    stone_cursed_cnt = 0
    stone_cursed_name = 0
    for name, char in list(self._group_list.items()):
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

  def start(self):
    self.tick()

  def stop(self):
    self._timer.cancel()

  def tick(self):
    self._timer = Timer(2.5, ClerMod.check, [self])
    self._timer.start()

  def check(self):
    self._cmd_engine.put(GroupCheckHealthCmd())
    self.tick()

  def __del__(self):
    exported.write_message("ClerBot: DEBUG: deleting ClerMod object {0}".format(self))
    if self._timer is not None:
      self._timer.cancel()
