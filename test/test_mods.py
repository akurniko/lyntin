# -*- coding: utf-8 -*-
from future import standard_library
standard_library.install_aliases()
from builtins import chr
from lyntin.modules.sowmud import bot, prompt, events
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
               u"5 Эригон",
               u"6 Ялхгау"]

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

p1 = u"876H 1009M 66V 51503MX 0C Вых:В>"

def init_group(event_classifier, group_setup):
  for s, mode in group_headers:
    if mode == "INIT":
      event_classifier.mudfilter(s)
      break

  for g_member in group_setup:
    event_classifier.mudfilter(g_member)

  event_classifier.mudfilter(p1)

def test_frag_mod():
  q = queue.Queue()
  event_classifier = events.EventClassifier()
  prompt.Prompt(event_classifier)
  group_mod = bot.GroupListMod(q, event_classifier, u"Эригон")
  mod = bot.FragMod(q, event_classifier, group_mod)

  init_group(event_classifier, group_setup)

  for s, mode in group_headers:
    event_classifier.mudfilter(s)
    if mode == "POSITION":
      assert mod.mode()
    event_classifier.mudfilter(p1)
    assert (mod.mode() == None)

def test_stand_up(monkeypatch):
  q = queue.Queue()
  event_classifier = events.EventClassifier()
  prompt.Prompt(event_classifier)
  group_mod = bot.GroupListMod(q, event_classifier, u"Эригон")
  mod = bot.FragMod(q, event_classifier, group_mod)

  def cmd(command, **kwargs):
    assert command == "stand"

  monkeypatch.setattr(exported, "lyntin_command", cmd)
  init_group(event_classifier, group_setup)

  for s, mode in group_headers:
    if mode == "POSITION":
      event_classifier.mudfilter(s)
      break

  for g_member in group1_stand:
    event_classifier.mudfilter(g_member)

  event_classifier.mudfilter(p1)
