# -*- coding: utf-8 -*-
from future import standard_library
standard_library.install_aliases()
from builtins import chr
from lyntin.modules.sowmud import mage, bot, prompt, events
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

def test_cast():
  q = queue.Queue()
  event_classifier = events.EventClassifier()
  prompt.Prompt(event_classifier)
  magebot = mage.MageBot(q, event_classifier, u"Эригон")

  init_group(event_classifier, group_setup)

  for s, mode in group_headers:
    if mode == "POSITION":
      event_classifier.mudfilter(s)
      break

  for g_member in group1_fight:
    event_classifier.mudfilter(g_member)

  event_classifier.mudfilter(p1)
  assert q.get_nowait().command() == u"cast гроза"

def test_check():
  q = queue.Queue()
  event_classifier = events.EventClassifier()
  prompt.Prompt(event_classifier)
  magebot = mage.MageBot(q, event_classifier, u"Эригон")

  init_group(event_classifier, group_setup)
  magebot.mudfilter(u"Вы произнесли магические слова 'гроза'...")

  assert q.get_nowait().command() == u"пгр поз ряд"

def advance_battle_round(ev_classifier):
  for s, mode in group_headers:
    if mode == "POSITION":
      ev_classifier.mudfilter(s)
      break

  for g_member in group1_fight:
    ev_classifier.mudfilter(g_member)

  ev_classifier.mudfilter(p1)

def test_rotation():
  q = queue.Queue()
  event_classifier = events.EventClassifier()
  prompt.Prompt(event_classifier)
  magebot = mage.MageBot(q, event_classifier, u"Эригон")

  init_group(event_classifier, group_setup)

  advance_battle_round(event_classifier)
  assert q.get_nowait().command() == u"cast гроза"

  event_classifier.mudfilter(u"Вы произнесли магические слова 'гроза'...")

  assert q.get_nowait().command() == u"пгр поз ряд"
  advance_battle_round(event_classifier)

  assert q.get_nowait().command() == u"cast гроза"

  return q, magebot

def test_following():
  q = queue.Queue()
  event_classifier = events.EventClassifier()
  prompt.Prompt(event_classifier)
  magebot = mage.MageBot(q, event_classifier, u"Эригон")

  init_group(event_classifier, group_setup)

  magebot.mudfilter(u"Вы последовали за Дарсу.")
  assert q.get_nowait().command() == u"пгр поз ряд"

  return q, magebot

def test_detect_magic():
  q, magebot = test_rotation()

  magebot.mudfilter(u"Вы произнесли магические слова 'гроза' ( сила 300% )...")

  assert q.get_nowait().command() == u"пгр поз ряд"

def test_after_prompt():
  q, magebot = test_rotation()

  magebot.mudfilter(u"3018H 4793M 308V 4186151389384X 485111C [Эригон:Великолепное]-[Тэйрос:Великолепное] [исследователь минералов:Хорошее] Вых:^>")
  text = u"Вы произнесли магические слова 'гроза' ( сила 300% )..."
  magebot.mudfilter(text)

  assert q.get_nowait().command() == u"пгр поз ряд"
