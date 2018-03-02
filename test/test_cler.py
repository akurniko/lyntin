# -*- coding: utf-8 -*-
from lyntin.modules.sowmud import cler
from lyntin import exported
from lyntin import ansi
import Queue

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
                u"3 Цушка             Д",]

group1_health =  [u"1 Шыгос    ooooo    Стоит     Д  Д",
                  u"2 Алиант   ooooo    Сражается Д  Н",
                  u"3 Цушка    ooooo    Стоит     Д  Н",]

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

def init_group(clerbot, group_setup):
  for s, mode in group_headers:
    if mode == "INIT":
      clerbot.mudfilter(s)
      break

  for g_member in group_setup:
    clerbot.mudfilter(g_member)

  clerbot.on_prompt()


def test_group_header_regexp():
  p1 = u"876H 1009M 66V 51503MX 0C Вых:В>"

  q = Queue.Queue()
  clerbot = cler.ClerBot(q)

  for s, mode in group_headers:
    clerbot.mudfilter(s)
    assert clerbot.get_mode() == mode
    clerbot.on_prompt()
    assert clerbot.get_mode() == None

def test_auto_summon():
  q = Queue.Queue()
  clerbot = cler.ClerBot(q)

  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "NEAR":
      clerbot.mudfilter(s)
      break

  assert clerbot.get_mode() == "NEAR"

  for g_member in group1_near:
    clerbot.mudfilter(g_member)

  clerbot.on_prompt()

  assert clerbot.status() == u"Алиант\nЦушка\nШыгос\nДарсу"
  assert q.get_nowait().command() == u"cast призыв Алиант"

def test_undrain():
  q = Queue.Queue()
  clerbot = cler.ClerBot(q)

  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.get_mode() == "HEALTH"

  for g_member in group1_health:
    clerbot.mudfilter(g_member)

  clerbot.on_prompt()

  assert q.get_nowait().command() == u"cast слово.силы Шыгос"

def test_stand_up(monkeypatch):
  q = Queue.Queue()
  clerbot = cler.ClerBot(q)

  def cmd(command, **kwargs):
    assert command == "stand"

  monkeypatch.setattr(exported, "lyntin_command", cmd)
  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.get_mode() == "HEALTH"

  for g_member in group1_stand:
    clerbot.mudfilter(g_member)

  clerbot.on_prompt()

def test_unstone():
  q = Queue.Queue()
  clerbot = cler.ClerBot(q)

  init_group(clerbot, group_setup)

  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.get_mode() == "HEALTH"

  clerbot.mudfilter(color2_test.replace("^[", chr(27)))

  clerbot.on_prompt()

  assert q.get_nowait().command() == u"cast живое.прикосновение Шыгос"

  init_group(clerbot, stone_setup)
  for s, mode in group_headers:
    if mode == "HEALTH":
      clerbot.mudfilter(s)
      break

  assert clerbot.get_mode() == "HEALTH"

  for s in stone_test:
    clerbot.mudfilter(s.replace("^[", chr(27)))

  clerbot.on_prompt()
  assert q.get_nowait().command() == u"cast живое.прикосновение Китаст"
