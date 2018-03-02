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
from . import group
import random

class Bot(object):
  def __init__(self, cmd_engine, event_classifier, myself):
    factory = group.GroupColumnFactory()

    self._group_list = GroupListMod(cmd_engine, event_classifier, myself)
    self._mods = {}

    self._cmd_engine = cmd_engine
    self._event_classifier = event_classifier

  def unregister(self):
    for m in self._mods.values():
      m.unregister()
    self._group_list.unregister()

  def __del__(self):
    exported.write_message("Bot: DEBUG: deleting Bot object")

  def mode(self):
    for m in self._mods.values():
      mode = m.mode()
      if mode is not None:
        return mode

  def on_event(self, ev_type, match):
    for mod in self._mods.values():
      mod.on_event(ev_type, match)

  def add_mod(self, mod, name):
    self._mods[name] = mod

  def mudfilter(self, text):
    self._event_classifier.mudfilter(text)

  def status(self):
    return "unknown"

  def group_list(self):
    return self._group_list

  def start(self):
    pass

  def stop(self):
    pass


class GroupListMod(dict):
  def __init__(self, cmd_engine, event_classifier, myself):
    factory = group.GroupColumnFactory()
    initView = group.GroupView()
    initView.add_column(factory.get_num_column())
    initView.add_column(factory.get_name_column())

    self._mode = False
    event_classifier.add_event("group_init_header", initView.header())
    event_classifier.add_event("group_init_member", initView.member())
    event_classifier.add_callback("group_init_header", self)
    event_classifier.add_callback("group_init_member", self)
    event_classifier.add_callback("prompt", self)

    self._event_classifier = event_classifier
    self._cmd_engine = cmd_engine
    self._myself = myself
    self._enabled = True

  def unregister(self):
    self._enabled = False
    self._event_classifier.remove_callback("prompt", self)
    self._event_classifier.remove_callback("group_init_header", self)
    self._event_classifier.remove_callback("group_init_member", self)

  # This supports legacy unit tests
  def mode(self):
    if self._mode:
      return "INIT"

  def myself(self):
    try:
      return self[self._myself]
    except KeyError:
      exported.write_message("Bot: WARN: could not find myself in group")
      return group.GroupMember("0", "unknown")

  def on_event(self, ev_type, match):
    if not self._enabled:
      exported.write_message("GroupMod: WARN: disabled mod got on_event")
    if ev_type == "group_init_header":
      self._event_classifier.gag_current()
      self._mode = True
      self.clear()
    if ev_type == "group_init_member" and self._mode:
      num = match.group("num")
      name = match.group("name")
      self[name] = group.GroupMember(num, name)
      self._event_classifier.gag_current()
    if (ev_type == "prompt") and self._mode:
      self._mode = False


class GroupCheckFightCmd(cmds.Cmd):
  def __init__(self):
    Cmd.__init__(self, u"пгр поз ряд")

class FragMod(object):
  def __init__(self, cmd_engine, event_classifier, group_list):
    factory = group.GroupColumnFactory()
    positionView = group.GroupView()
    positionView.add_column(factory.get_num_column())
    positionView.add_column(factory.get_name_column())
    positionView.add_column(factory.get_position_column())
    positionView.add_column(factory.get_near_column())

    self._mode = False
    event_classifier.add_event("group_position_near_header", positionView.header())
    event_classifier.add_event("group_position_near_member", positionView.member())
    event_classifier.add_callback("group_position_near_header", self)
    event_classifier.add_callback("group_position_near_member", self)
    event_classifier.add_callback("prompt", self)

    self._check_cmd = cmds.Cmd(u"пгр поз ряд")
    self._group_list = group_list
    self._event_classifier = event_classifier

    event_classifier.add_callback("you_stood_up", self)
    event_classifier.add_callback("you_followed", self)
    event_classifier.add_callback("you_unmute", self)
    event_classifier.add_callback("you_unhardmute", self)
    event_classifier.add_callback("you_unhold", self)
    event_classifier.add_callback("you_casted", self)
    event_classifier.add_callback("room_cast", self)
    self._spell_index = 0
    self._rotation = []
    self._cmd_engine = cmd_engine
    self._fight = False
    self._enabled = True
    self._id = random.randint(1,100)

  def unregister(self):
    self._enabled = False
    exported.write_message("FragMod: DEBUG: FragMod disabled")
    self._event_classifier.remove_callback("you_stood_up", self)
    self._event_classifier.remove_callback("you_followed", self)
    self._event_classifier.remove_callback("you_unmute", self)
    self._event_classifier.remove_callback("you_unhardmute", self)
    self._event_classifier.remove_callback("you_unhold", self)
    self._event_classifier.remove_callback("you_casted", self)
    self._event_classifier.remove_callback("room_cast", self)
    self._event_classifier.remove_callback("prompt", self)
    self._event_classifier.remove_callback("group_position_near_header", self)
    self._event_classifier.remove_callback("group_position_near_member", self)

  def __str__(self):
    return "FragMod #{0}".format(self._id)
  def __repr__(self):
    return "FragMod #{0}".format(self._id)

  # This supports legacy unit tests
  def mode(self):
    if self._mode:
      return "POSITION"

  def set_rotation(self, rotation = None):
    self._spell_index = 0
    if rotation is not None and rotation != '':
      self._rotation = rotation.split(" ")
    exported.write_message("FragMod: INFO: new rotation {0}".format(self._rotation))

  def get_next_spell(self):
    try:
      return self._rotation[self._spell_index]
    except IndexError:
      self._spell_index = 0

  def advance_rotation(self, spell):
    if spell_search(self._rotation, spell) is not None:
      self._spell_index = self._spell_index + 1
      if self._spell_index >= len(self._rotation):
        self._spell_index = 0

  def on_event(self, ev_type, match):
    if not self._enabled:
      exported.write_message("FragMod: WARN: disabled Mod got on_event")

    if ev_type == "group_position_near_header":
      self._event_classifier.gag_current()
      self._mode = True

    if ev_type == "group_position_near_member" and self._mode:
      self._event_classifier.gag_current()
      #exported.write_message("FragMod: DEBUG: FragMod on group_position_near_member")
      self.group_member_pos(match)

    if (ev_type == "prompt") and self._mode:
      self._mode = False
      if self._group_list.myself().position() == "SIT":
        self._cmd_engine.put(cmds.Cmd("stand"), True)
        return

      self._fight = False
      for m in self._group_list.values():
        if m.position() == "FIGHT":
          self._fight = True
          self._cmd_engine.put(cmds.CastCmd(self.get_next_spell()))
          return

    if ((ev_type == "you_followed") or
        (ev_type == "you_unmute") or
        (ev_type == "you_unhardmute") or
        (ev_type == "you_stood_up")):
      if ev_type == "you_followed":
        self._spell_index = 0
      self._cmd_engine.put(self._check_cmd)

    if (ev_type == "you_casted"):
      self.advance_rotation(match.group("spell"))
      self._cmd_engine.put(self._check_cmd)

    if (ev_type == "room_cast") and (not self._fight) and (not self._mode):
      self._fight = True
      self._cmd_engine.put(self._check_cmd)

  def group_member_pos(self, match):
    num = match.group("num")
    name = match.group("name")
    position = match.group("position")
    near = (match.group("near") == u'Д')

    name = name.strip()

    try:
      self._group_list[name].update(position, near)
    except KeyError:
      exported.write_message(u"Bot: WARN: could not find group member {0} in group_member_pos of {1}".format(name, self))


def spell_search(short_spell_dotted_list, long_spell_undotted):
  words = long_spell_undotted.split(' ')
  for s in short_spell_dotted_list:
    short_words = s.split('.')
    if len(short_words) != len(words):
      continue
    match = True
    for i in range(len(short_words)):
      if not words[i].startswith(short_words[i]):
        match = False
        break
    if match:
      return short_spell_dotted_list.index(s)
  return None

class AutoSummonMod(object):
  summon_spell = u"призыв"

  appear = utils.compile_regexp(u"r[^(?P<who>.+) неожиданно появился.$]")

  def __init__(self, cmd_engine, event_classifier, group_list, reverse = False):
    factory = group.GroupColumnFactory()
    nearView = group.GroupView()
    nearView.add_column(factory.get_num_column())
    nearView.add_column(factory.get_name_column())
    nearView.add_column(factory.get_near_column())

    self._mode = False
    event_classifier.add_event("group_near_header", nearView.header())
    event_classifier.add_event("group_near_member", nearView.member())
    event_classifier.add_event("appear", AutoSummonMod.appear)
    event_classifier.add_callback("group_near_header", self)
    event_classifier.add_callback("group_near_member", self)
    event_classifier.add_callback("appear", self)
    event_classifier.add_callback("prompt", self)
    event_classifier.add_callback("you_casted", self)

    self._event_classifier = event_classifier
    self._group_list = group_list
    self._cmd_engine = cmd_engine
    self._reverse = reverse

  def unregister(self):
    self._event_classifier.remove_callback("group_near_header", self)
    self._event_classifier.remove_callback("group_near_member", self)
    self._event_classifier.remove_callback("appear", self)
    self._event_classifier.remove_callback("prompt", self)
    self._event_classifier.remove_callback("you_casted", self)

  def mode(self):
    if self._mode:
      return "NEAR"

  def on_event(self, ev_type, match):
    if ev_type == "group_near_header":
      self._event_classifier.gag_current()
      self._mode = True

    if (ev_type == "group_near_member") and self._mode:
      self._event_classifier.gag_current()
      self.group_member_near(match)

    if (ev_type == "prompt") and self._mode:
      self.do_auto_summon()
      self._mode = False

    if ev_type == "you_casted":
      if match.group('spell') == AutoSummonMod.summon_spell:
        self._mode = True

    if ev_type == "appear":
      self.on_appear(match.group("who"))

  def group_member_near(self, match):
    num = match.group("num")
    name = match.group("name")
    near = (match.group("near") == u'Д')
    try:
      self._group_list[name].set_near(near)
    except KeyError:
      exported.write_message(u"Bot: WARN: {0} is unknown group member".format(name))

  def do_auto_summon(self):
    items = sorted(list(self._group_list.items()))
    if self._reverse:
      items = reversed(items)
    for name, char in items:
      if not char.is_near():
        #print "Summoning " + name + " {0}".format(flag)
        cmd = cmds.CastCmd(AutoSummonMod.summon_spell, name)
        char.set_near(True)
        self._cmd_engine.put(cmd)
        return

  def on_appear(self, name):
    try:
      self._group_list[name].set_near(True)
    except KeyError:
      pass
