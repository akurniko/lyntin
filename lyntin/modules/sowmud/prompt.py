from builtins import object
from lyntin import exported, utils, ansi, settings
import time

class Prompt(object):
  def __init__(self, event_classifier):
    # First few numbers, then not greedy for exits to not consume >, finally not
    # mapped to the group in the match result spaces if any
    self.non_battle_compiled = utils.compile_regexp(u"r[^(?P<hp>\d+)H (?P<mana>\d+)M (?P<moves>\d+)V (\d+)(X|MX) (\d+)C Вых:(?P<exits>.*?)>(?:\s*)$]", 1)
    self.battle_compiled = utils.compile_regexp(u"r[^(?P<hp>\d+)H (?P<mana>\d+)M (?P<moves>\d+)V (\d+)(X|MX) (\d+)C \[.+?\] \[.+?\] Вых:(?P<exits>.*?)>(?:\s*)$]", 1)
    self.assist_battle_compiled = utils.compile_regexp(u"r[^(?P<hp>\d+)H (?P<mana>\d+)M (?P<moves>\d+)V (\d+)(X|MX) (\d+)C \[.+?\]-\[.+?\] \[.+?\] Вых:(?P<exits>.*?)>(?:\s*)$]", 1)
    self._event_classifier = event_classifier

    self._exits = None

    self._hp = 0
    self._mana = 0
    self._moves = 0

    self._last_received = None
    self._last_printed = None

    self._event_classifier.add_event("prompt", self.non_battle_compiled)
    self._event_classifier.add_event("prompt", self.battle_compiled)
    self._event_classifier.add_event("prompt", self.assist_battle_compiled)
    self._event_classifier.add_callback("prompt", self)

  def on_event(self, ev_type, match):
    if ev_type != "prompt":
      return

    old_exits = self._exits
    old_hp = int(self._hp)
    old_mana = int(self._mana)
    old_moves = int(self._moves)

    self._hp = int(match.group("hp"))
    self._mana = int(match.group("mana"))
    self._moves = int(match.group("moves"))
    self._exits = match.group("exits")

    self._last_received = time.time()

    # Do not print the prompt too often and do not print the same prompt
    if (((self._last_printed is not None) and
         (self._last_received - self._last_printed < 1) and
         (self._exits == old_exits)) or 
         ((old_hp == self._hp) and
         (old_mana == self._mana) and
         (old_moves == self._moves))):
      self._event_classifier.gag_current()
    else:
      self._last_printed = self._last_received

  def exits(self):
    return self._exits

  def current(self):
    return self._event_classifier.current() == "prompt"

  def timestamp(self):
    return self._last_received
