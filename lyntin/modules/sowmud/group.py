# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from builtins import map
from builtins import object
from lyntin import utils

class GroupColumn(object):
  def __init__(self, header, name, regexp, parse_func = lambda x: x, value = None):
    self._header = header
    self._name = name 
    self._regexp = regexp
    self._value = value
    self._parse = parse_func

  def header(self):
    return self._header

  def name(self):
    return self._name

  def regexp(self):
    return self._regexp

  def parse(self, match):
    try:
      self._value = self._parse(match[self._name])
    except TypeError:
      self._value = self._parse(match)
    except KeyError:
      self._value = self._parse(match)

  def set_value(self, value):
    self._value = value

  def value(self):
    return self._value

class GroupColumnFactory(object):
  def __init__(self):
    pass

  def get_num_column(self):
    return GroupColumn( "", "num", "\d+" )

  def get_name_column(self):
    return GroupColumn( "Имя\s*", "name", "\S+" )

  def get_near_column(self):
    return GroupColumn( "Рядом", "near", "Д|Н", lambda x: x == 'Д', True )

  def get_hp_column(self):
    return GroupColumn( "H", "hp", "o+", lambda x: len(x), 5 )

  def get_drain_column(self):
    return GroupColumn( "Укр", "drained", "Д|Н", lambda x: x == 'Д', False )

  def get_position_column(self):
    positions = {u"Стоит": "STAND", u"Сражается": "FIGHT", u"Сидит": "SIT", u"Отдыхает": "REST"}
    return GroupColumn( "Позиция", "position", "({0})".format("|".join(positions.keys())), lambda x: positions[x] )

class GroupMember(object):

  def __init__(self, num, name):
    self._columns = {}

    factory = GroupColumnFactory()
    self.add_column(factory.get_num_column())
    self.add_column(factory.get_name_column())
    self.add_column(factory.get_near_column())
    self.add_column(factory.get_position_column())
    self.add_column(factory.get_hp_column())
    self.add_column(factory.get_drain_column())

    self.add_column(GroupColumn( "", "stone_curse", "" ))

  def add_column(self, c):
    self._columns[c.name()] = c

  def set_near(self, near):
    if "near" in self._columns:
      self._columns["near"].set_value(near)

  def is_near(self):
    if "near" in self._columns:
      return self._columns["near"].value()
    return True

  def name(self):
    if "name" in self._columns:
      return self._columns["name"].value()
    return "Unknown"

  def position(self):
    if "position" in self._columns:
      return self._columns["position"].value()
    return "Unknown"

  def set_num(self, num):
    if "num" in self._columns:
      self._columns["num"].set_value(num)

  def hp(self):
    if "hp" in self._columns:
      return self._columns["hp"].value()
    return 5

  def is_drained(self):
    if "drained" in self._columns:
      return self._columns["drained"].value()
    return False

  def set_stone_curse(self, stone_curse):
    if "stone_curse" in self._columns:
      self._columns["stone_curse"].set_value(stone_curse)

  def is_stone_cursed(self):
    if "stone_curse" in self._columns:
      return self._columns["stone_curse"].value()
    return False

  def update(self, position, near, hp = 5, drain_level = False):
    if "hp" in self._columns:
      self._columns["hp"].set_value(hp)
    if "near" in self._columns:
      self._columns["near"].set_value(near)
    if "drained" in self._columns:
      self._columns["drained"].set_value(drain_level)
    if "stone_curse" in self._columns:
      self._columns["stone_curse"].set_value(False)
    try:
      self._columns["position"].parse(position)
    except KeyError:
      exported.write_message(u"Bot: WARN: {0} is unknown position".format(position))

class GroupView(object):
  def __init__(self):
    self._columns = []

  def add_column(self, c):
    self._columns.append(c)

  def header(self):
    h = u"r[^\s*?"
    h = h + "\s+?".join( [c.header() for c in self._columns] )
    h = h + "$]"
    return utils.compile_regexp(h)

  def member(self):
    m = u"r[^\s*"
    m = m + "\s*".join( [
        "(?P<{0}>{1})".format(c.name(), c.regexp()) for c in self._columns] )
    m = m + "\s*$]"
    return utils.compile_regexp(m, 1)

