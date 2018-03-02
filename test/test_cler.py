# -*- coding: utf-8 -*-
from future import standard_library
standard_library.install_aliases()
from builtins import chr
from lyntin.modules.sowmud import cler
from lyntin.modules.sowmud import events
from lyntin.modules.sowmud import prompt
from lyntin import exported
from lyntin import ansi
import queue

group_headers = [(u"   Имя  ", "INIT"), (u"   Имя wrong ", None),
                 (u" Имя  Рядом", "NEAR"), (u" Имя   Рядом wrong ", None),
                 (u" Имя wrong Рядом", None),
                 (u" Имя  H  Позиция Рядом Укр", "HEALTH")]

group_setup = [u"1 Шыгос",
               u"2 Алиант",
               u"3 Цушка",
               u"4 Дарсу"]

group1_near =  [u"1 Шыгос             Д",
                u" 2  Алиант               Н",
                u"3 Цушка             Н",]

group1_health =  [u"1 Шыгос    ooooo    Стоит     Д  Д",
                  u"2 Алиант   ooooo    Сражается Д  Н",
                  u"3 Цушка    ooooo    Стоит     Д  Н",]

group2_health =  [u"1 Шыгос    ooooo    Стоит     Д  Н",
                  u"2 Алиант   ooooo    Сражается Д  Н",
                  u"3 Цушка    ooooo    Стоит     Н  Н",]

group1_stand =  [u"1 Шыгос    ooooo    Стоит     Д  Н",
                 u"2 Алиант   ooooo    Сражается Д  Н",
                 u"3 Цушка    ooooo    Стоит     Д  Н",
                 u"4 Дарсу    ooooo    Сидит     Д  Н",]

color1_test = u"^[[1;33mКвортон начал медленно превращаться в камень...^[[0m"

color2_test = u"1 ^[[0mШыгос          ^[[32mooooo^[[0m  ^[[1;33mСражается^[[0m   ^[[1;32mД^[[0m    ^[[1;31mН^[[0m"
color3_test = u"4 ^[[0mДарсу            ^[[32mooooo^[[0m  Сражается   ^[[1;32mД^[[0m    ^[[1;31mН^[[0m"

stone_setup = [u"1 Шыгос",
               u"24 Цвахер",
               u"25 Китаст",
               u"26 Яромар"]

stone_test = [u"1 Шыгос ooooo Стоит Д Н",
              u"24 ^[[0mЦвахер          ^[[32mooooo^[[0m  Сражается   ^[[1;32mД^[[0m    ^[[1;31mН^[[0m",
              u"25 ^[[0mКитаст          ^[[32mooooo^[[0m  ^[[1;33mСтоит    ^[[0m   ^[[1;32mД^[[0m    ^[[1;31mН^[[0m",
              u"26 ^[[0mЯромар          ^[[32mooooo^[[0m  Сражается   ^[[1;32mД^[[0m    ^[[1;31mН^[[0m"]

p1 = u"876H 1009M 66V 51503MX 0C Вых:В>"

def init_group(ev_classifier, group_setup):
  for s, mode in group_headers:
    if mode == "INIT":
      ev_classifier.mudfilter(s)
      break

  for g_member in group_setup:
    ev_classifier.mudfilter(g_member)

  ev_classifier.mudfilter(p1)

def test_auto_summon():
  q = queue.Queue()
  ec = events.EventClassifier()
  prompt.Prompt(ec)
  clerbot = cler.ClerBot(q, ec, u"Дарсу")

  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "NEAR":
      clerbot.mudfilter(s)
      break

  assert clerbot.mode() == "NEAR"

  for g_member in group1_near:
    clerbot.mudfilter(g_member)

  ec.mudfilter(p1)
  assert q.get_nowait().command() == u"cast призыв Алиант"

  ec.mudfilter("Вы произнесли магические слова 'призыв'...")
  ec.mudfilter("Алиант неожиданно появился.")
  ec.mudfilter(p1)
  assert q.get_nowait().command() == u"cast призыв Цушка"

  ec.mudfilter("Вы произнесли магические слова 'призыв'...")
  assert q.empty()

  return q, clerbot

def test_auto_summon_with_heal_on():
  q = queue.Queue()
  ec = events.EventClassifier()
  prompt.Prompt(ec)
  clerbot = cler.ClerBot(q, ec, u"Дарсу")

  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "NEAR":
      clerbot.mudfilter(s)
      break

  assert clerbot.mode() == "NEAR"

  for g_member in group1_near:
    clerbot.mudfilter(g_member)

  ec.mudfilter(p1)
  assert q.get_nowait().command() == u"cast призыв Алиант"
  ec.mudfilter("Вы произнесли магические слова 'призыв'...")
  ec.mudfilter("Алиант неожиданно появился.")

  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  for g_member in group2_health:
    clerbot.mudfilter(g_member)

  ec.mudfilter(p1)
  assert q.get_nowait().command() == u"cast призыв Цушка"

  ec.mudfilter(p1)
  assert q.empty()

  return q, clerbot

#  status = clerbot.group_list()
#  assert u"Дарсу" in status
#  assert u"Алиант" in status
#  assert u"Шыгос" in status
#  assert u"Цушка" in status

def test_undrain():
  q = queue.Queue()
  ec = events.EventClassifier()
  prompt.Prompt(ec)
  clerbot = cler.ClerBot(q, ec, u"Дарсу")

  init_group(ec, group_setup)

  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.mode() == "HEALTH"

  for g_member in group1_health:
    clerbot.mudfilter(g_member)

  ec.mudfilter(p1)

  assert q.get_nowait().command() == u"cast слово.силы Шыгос"

def test_stand_up(monkeypatch):
  q = queue.Queue()
  ec = events.EventClassifier()
  prompt.Prompt(ec)
  clerbot = cler.ClerBot(q, ec, u"Дарсу")

  def cmd(command, **kwargs):
    assert command == "stand"

  monkeypatch.setattr(exported, "lyntin_command", cmd)
  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.mode() == "HEALTH"

  for g_member in group1_stand:
    clerbot.mudfilter(g_member)

  ec.mudfilter(p1)

def test_unstone():
  q = queue.Queue()
  ec = events.EventClassifier()
  prompt.Prompt(ec)
  clerbot = cler.ClerBot(q, ec, u"Дарсу")

  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.mode() == "HEALTH"

  clerbot.mudfilter(color2_test.replace("^[", chr(27)))

  ec.mudfilter(p1)

  assert q.get_nowait().command() == u"cast живое.прикосновение Шыгос"

  init_group(clerbot, stone_setup)
  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.mode() == "HEALTH"

  for s in stone_test:
    clerbot.mudfilter(s.replace("^[", chr(27)))

  ec.mudfilter(p1)
  assert q.get_nowait().command() == u"cast живое.прикосновение Китаст"
