# -*- coding: utf-8 -*-
from lyntin import exported, utils, ansi, settings
from lyntin.modules import modutils
from threading import Thread
import time
import Queue

class CmdEngine():
  unknown_name = u"Безымянная комната"

  def __init__(self):
    self._queue = Queue.Queue()
    self._running = False
    self._thread = None
    self._sent = []

  def _main(self):
    while True:
      try:
        cmd = self._queue.get()
      except KeyboardInterrupt:
        self._running = False

      self._queue.task_done()
      if not self._running:
        self._clear()
        break

      self._sent.append((cmd[0], cmd[1], time.time()))
      exported.lyntin_command(cmd[0].command(), internal=1)
      self.clear_sent()

  def clear_sent(self):
    now = time.time()
    cnt = 0
    for cmd, enqueued, sent in self._sent:
      if now - sent > 10:
        cnt = cnt + 1
        #exported.write_message(u"clearing 10+ sec back sent command {0}".format(cmd.command()))
        self._sent.remove((cmd, enqueued, sent))
    return cnt

  def start(self):
    if self._running: return
    self._running = True
    self._thread = Thread(target = CmdEngine._main, args = [self])
    self._thread.start()

  def stop(self):
    if not self._running: return
    self._running = False
    self._join()

  def put(self, cmd, non_blocking = False):
    if non_blocking:
      exported.lyntin_command(cmd.command())
      return

    if self._running:
      self._queue.put((cmd, time.time()))

  def _join(self):
    # Put a command on the queue so that the running thread stops
    self._queue.put("join")
    self._queue.join()
    self._thread.join()

  def _clear(self):
    while True:
      try:
        self._queue.get_nowait()
        self._queue.task_done()
      except Queue.Empty:
        break


class Cmd():
  def __init__(self, string):
    self._string = string
    pass

  def command(self):
    return self._string


class CastCmd(Cmd):
  def __init__(self, spell, target = None):

    self._spell = spell
    self._target = target

    if self._target is None:
      string = u"cast {0}".format(self._spell)
    else:
      string = u"cast {0} {1}".format(self._spell, self._target)

    Cmd.__init__(self, string)


class GroupCheckHealthCmd(Cmd):
  def __init__(self):
    Cmd.__init__(self, u"pgroup здоровье позиция рядом украсть.душу")

