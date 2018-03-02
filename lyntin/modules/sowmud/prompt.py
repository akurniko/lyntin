from lyntin import exported, utils, ansi, settings
from lyntin.modules import lyntinuser
import time

class Prompt():
  def __init__(self):
    # First few numbers, then not greedy for exits to not consume >, finally not
    # mapped to the group in the match result spaces if any
    self.non_battle_compiled = utils.compile_regexp("r[^(?P<hp>\d+)H (?P<mana>\d+)M (?P<moves>\d+)V (\d+)(X|MX) (\d+)C Вых:(?P<exits>.*?)>(?:\s*)$]".decode("utf-8"), 1)
    self.battle_compiled = utils.compile_regexp("r[^(?P<hp>\d+)H (?P<mana>\d+)M (?P<moves>\d+)V (\d+)(X|MX) (\d+)C \[.+?\] \[.+?\] Вых:(?P<exits>.*?)>(?:\s*)$]".decode("utf-8"), 1)
    self.assist_battle_compiled = utils.compile_regexp("r[^(?P<hp>\d+)H (?P<mana>\d+)M (?P<moves>\d+)V (\d+)(X|MX) (\d+)C \[.+?\]-\[.+?\] \[.+?\] Вых:(?P<exits>.*?)>(?:\s*)$]".decode("utf-8"), 1)
    self._exits = None

    self._hp = 0
    self._mana = 0
    self._moves = 0

    self._prompt = False
    self._last_received = None
    self._last_printed = None

  def mudfilter(self, text):
    colorline = utils.filter_cm(text)
    nocolorline = ansi.filter_ansi(colorline)

    match = self.non_battle_compiled.search(nocolorline)
    if not match:
      match = self.battle_compiled.search(nocolorline)
    if not match:
      match = self.assist_battle_compiled.search(nocolorline)
    if match:
      #exported.write_message("Got prompt with {0} HP, {1} M, {2} moves ".format(match.group("hp"), match.group("mana"), match.group("moves")))
      old_exits = self._exits
      old_hp = int(self._hp)
      old_mana = int(self._mana)
      old_moves = int(self._moves)

      self._hp = int(match.group("hp"))
      self._mana = int(match.group("mana"))
      self._moves = int(match.group("moves"))
      self._exits = match.group("exits")
      self._prompt = True

      self._last_received = time.time()
      lyntinuser.on_prompt()

      # Do not print the prompt too often and do not print the same prompt
      if (((self._last_printed is not None) and
          (self._last_received - self._last_printed < 1) and
          (self._exits == old_exits)) or 
         ((old_hp == self._hp) and
          (old_mana == self._mana) and
          (old_moves == self._moves))):
        return ""
      else:
        self._last_printed = self._last_received
        return text

    else:
      if self._prompt and self._last_printed == self._last_received:
        text = "\n" + text
      self._prompt = False
      return text
      #exported.write_message("Got no prompt (%s)" % text)

  def exits(self):
    return self._exits

  def current(self):
    return self._prompt

  def timestamp(self):
    return self._last_received

  def turn_on(self):
    enc = self.non_battle_compiled.pattern.encode(settings.LOCAL_ENCODING)
    exported.write_message("pattern {0}".format(enc))
    #exported.lyntin_command("#action {^ >} {}")
    pass

  def turn_off(self):
    #exported.lyntin_command("#action {^ >} {}")
    pass
