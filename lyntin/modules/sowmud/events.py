# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from builtins import map
from builtins import object
from lyntin import exported, utils, ansi, settings
from lyntin.modules import modutils

class EventClassifier(object):
  followed = utils.compile_regexp(u"r[^Вы последовали за (?P<lead>.+)$]")

  successful_cast = utils.compile_regexp(
          u"r[^Вы произнесли магические слова '(?P<spell>.+)'\.\.\.$]")
  successful_cast_detect = utils.compile_regexp(
          u"r[^Вы произнесли магические слова '(?P<spell>.+)' \( сила .+ \)\.\.\.$]")
  successful_direct_cast = utils.compile_regexp(
          u"r[^Вы посмотрели на (?P<target>.+) и произнесли магические слова '(?P<spell>.+)'\.\.\.$]")
  successful_direct_cast_detect = utils.compile_regexp(
          u"r[^Вы посмотрели на (?P<target>.+) и произнесли магические слова '(?P<spell>.+)' \( сила .+ \)\.\.\.$]")

  room_cast = utils.compile_regexp(
          u"r[^(?P<caster>.+) произнес магические слова '(?P<spell>.+)'\.\.\.$]")
  room_cast_detect = utils.compile_regexp(
          u"r[^(?P<caster>.+) произнес магические слова '(?P<spell>.+)' \( сила .+ \)\.\.\.$]")

  stood_up = utils.compile_regexp(u"r[^Вы встали.$]")
  unmute = utils.compile_regexp(u"r[^Вы снова обрели способность разговаривать.$]")
  unhard_mute = utils.compile_regexp(u"r[^Черное безмолвие отступило от вас.$]")
  unhold = utils.compile_regexp(u"r[^Вы снова можете двигаться.$]")

  def __init__(self):
    # Dict of events: {"type": [regexp, ...]}
    self.__events = {}
    # Dict of callbacks: {"type": [listener, ...]}
    self.__callbacks = {}
    self._current = None
    self._raw = None
    self._gag = False
    self.add_event("you_followed", EventClassifier.followed)
    self.add_event("you_casted", EventClassifier.successful_cast)
    self.add_event("you_casted", EventClassifier.successful_cast_detect)
    self.add_event("you_casted", EventClassifier.successful_direct_cast)
    self.add_event("you_casted", EventClassifier.successful_direct_cast_detect)
    self.add_event("room_cast", EventClassifier.room_cast)
    self.add_event("room_cast", EventClassifier.room_cast_detect)
    self.add_event("you_stood_up", EventClassifier.stood_up)
    self.add_event("you_unhardmute", EventClassifier.unhard_mute)
    self.add_event("you_unmute", EventClassifier.unmute)
    self.add_event("you_unhold", EventClassifier.unhold)
 
  def add_event(self, ev_type, regexp):
    try:
      # Do not add the same regexp twice!
      if regexp not in self.__events[ev_type]:
        self.__events[ev_type].append(regexp)
      else:
        exported.write_message("EvenetClassifier: WARN: trying to add the same regexp")
    except KeyError:
      self.__events[ev_type] = [regexp]

    if ev_type not in self.__callbacks:
      self.__callbacks[ev_type] = []

  def remove_event(self, ev_type):
    try:
      self.__callbacks.pop(ev_type)
      self.__events.pop(ev_type)
      exported.write_message("EventClassifier: DEBUG: successfully removed event {0}".format(ev_type))
    except KeyError:
      exported.write_message("EventClassifier: DEBUG: failed to remove event {0}, KeyError".format(ev_type))
      return

  def add_callback(self, ev_type, listener):
    try:
      self.__callbacks[ev_type].append(listener)
    except KeyError:
      self.__callbacks[ev_type] = [listener]

  def remove_callback(self, ev_type, listener):
    try:
      self.__callbacks[ev_type].remove(listener)
      exported.write_message("EventClassifier: DEBUG: " +
          "successfully removed callback {0} {1}".format(ev_type, listener))
    except KeyError:
      exported.write_message("EventClassifier: DEBUG: " +
          "failed to remove callback {0} {1}, KeyError".format(ev_type, listener))
      return
    except ValueError:
      exported.write_message("EventClassifier: DEBUG: " +
          "failed to remove callback {0} {1}, ValueError".format(ev_type, listener))
      pass

  def gag_current(self):
    self._gag = True

  def is_gagged(self):
    return self._gag

  def current(self):
    return self._current

  def get_raw(self):
    return self._raw

  def mudfilter(self, text):
    colorline = utils.filter_cm(text)
    nocolorline = ansi.filter_ansi(colorline)
    self._raw = colorline

    #exported.write_message("EventClassifier: DEBUG: " +
    #      "callbacks {0}".format(self.__callbacks))
    #exported.write_message("EventClassifier: DEBUG: " +
    #      "events {0}".format(self.__events))

    self._gag = False
    self._current = None
    #i = 0
    #j = 0
    #pattern = ""
    for t, list_r in self.__events.items():
      for r in list_r:
        match = r.search(nocolorline)
        #pattern = pattern + "e{0} ".format(i)
        #i = i + 1
        if match:
          self._current = t
          for c in self.__callbacks[t]:
            #exported.write_message(u"EventClassifier: DEBUG: callback for {0}".format(t))
            #pattern = pattern + "c{0} ".format(j)
            #j = j + 1
            c.on_event(t, match)

    #exported.write_message("EventClassifier: DEBUG: " + pattern)
