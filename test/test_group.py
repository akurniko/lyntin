# -*- coding: utf-8 -*-
from future import standard_library
standard_library.install_aliases()
from builtins import chr
from lyntin.modules.sowmud import group
from lyntin import exported
from lyntin import ansi
import queue

group_headers = [(u"   Имя  ", "INIT"), (u"   Имя wrong ", None),
                 (u" Имя  Рядом", "NEAR"), (u" Имя   Рядом wrong ", None),
                 (u" Имя wrong Рядом", None),
                 (u" Имя  Позиция Рядом", "POSITION")]

group_setup = [u"1 Шыгос",
               u"2 Алиант",
               u"3 Цушка",
               u"4 Дарсу",
               u"5 Ялхгау"]

group1_near =  [u"1 Шыгос             Д",
                u" 2  Алиант               Н",
                u"3 Цушка             Д",]

group1_fight =  [u"1 Шыгос    Стоит     Д",
                  u"2 Алиант   Сражается Д",
                  u"3 Цушка    Стоит     Д",]

group1_stand =  [u"1 Шыгос    Стоит     Д",
                 u"2 Алиант   Сражается Д",
                 u"3 Цушка    Стоит     Д",
                 u"4 Ялхгау   Сидит     Д",]

def init_group(group_setup):
  for s, mode in group_headers:
    if mode == "INIT":
      break

  for g_member in group_setup:
    pass

def test_factory():
  factory = group.GroupColumnFactory()
  name = factory.get_name_column()
  assert name.name() == "name"

  near = factory.get_near_column()
  assert near.name() == "near"

def test_group_header_regexp():
  factory = group.GroupColumnFactory()
  name = factory.get_name_column()
  view = group.GroupView()
  view.add_column(name)

  for s, mode in group_headers:
    if mode == "INIT":
      match = view.header().search(s)
      assert match

def test_group_member_regexp():
  factory = group.GroupColumnFactory()
  num = factory.get_num_column()
  name = factory.get_name_column()
  view = group.GroupView()
  view.add_column(num)
  view.add_column(name)

  for s in group_setup:
    match = view.member().search(s)
    assert match
