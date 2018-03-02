# -*- coding: utf-8 -*-
from future import standard_library
standard_library.install_aliases()
from builtins import chr
from lyntin.modules.sowmud import events, prompt
from lyntin import utils

def test_builtin_events():
  ec = events.EventClassifier()

  ec.mudfilter("Вы последовали за кем-то.")
  assert ec.current() == "you_followed"

  ec.mudfilter("Вы произнесли магические слова 'гроза'...")
  assert ec.current() == "you_casted"

  ec.mudfilter("Вы произнесли магические слова 'гроза' ( сила 310% )...")
  assert ec.current() == "you_casted"

  ec.mudfilter("Вы встали.")
  assert ec.current() == "you_stood_up"

  ec.mudfilter("Вы снова обрели способность разговаривать.")
  assert ec.current() == "you_unmute"

  ec.mudfilter("Черное безмолвие отступило от вас.")
  assert ec.current() == "you_unhardmute"

  ec.mudfilter("Вы снова можете двигаться.")
  assert ec.current() == "you_unhold"

def test_gag():
  ec = events.EventClassifier()

  ec.gag_current()
  assert ec.is_gagged()

class AssertListener(object):
  def __init__(self, ev_type_assertion):
    self._ev_type_assertion = ev_type_assertion
    pass

  def on_event(self, ev_type, match):
    assert ev_type == self._ev_type_assertion

def test_add_event():
  ec = events.EventClassifier()

  #a = utils.compile_regexp(u"r[^(?P<who>.+) произнес магические слова .$]")
  ev = utils.compile_regexp(u"r[^Вам лучше встать на ноги!]")

  ec.add_event("better_stand_up", ev)
  ec.add_callback("better_stand_up", AssertListener("better_stand_up"))
  ec.mudfilter("Вам лучше встать на ноги!")
  assert ec.current() == "better_stand_up"
