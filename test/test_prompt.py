# -*- coding: utf-8 -*-
from lyntin.modules.sowmud import prompt

def test_prompt_regexp():
  p1 = u"876H 1009M 66V 51503MX 0C Вых:В>"

  nonp1 = "not prompt"
  nonp2 = u"MX 0C Вых:В>"

  p = prompt.Prompt()

  p.mudfilter(p1)
  assert p.current()
  assert p.exits() == u"В"

  p.mudfilter(nonp1)
  assert not p.current()

  p.mudfilter(nonp2)
  assert not p.current()

def test_battle_prompt_regexp():
  p1 = u"320H 243M 174V 5MX 0C [Оланги:Великолепное] [рыжая белочка:Умирает] Вых:СЮЗ> "

  p = prompt.Prompt()

  p.mudfilter(p1)
  assert p.current()
  assert p.exits() == u"СЮЗ"

def test_assist_battle_prompt_regexp():
  p1 = u"320H 243M 174V 5MX 0C [Оланги:Великолепное]-[Дарсу:Жив] [рыжая белочка:Умирает] Вых:СЮЗ> "

  p = prompt.Prompt()

  p.mudfilter(p1)
  assert p.current()
  assert p.exits() == u"СЮЗ"
