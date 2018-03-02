# -*- coding: utf-8 -*-
from lyntin import exported
from lyntin.modules.sowmud import cmds
import Queue
import time

def test_cmds_start_stop(monkeypatch):
  #def write_message(msg):
  #  write_message.msg = msg
  #write_message.msg = None

  def command(command, **kwargs):
    pass

  #monkeypatch.setattr(exported, 'write_message', write_message)
  monkeypatch.setattr(exported, 'lyntin_command', command)
  #msg = None
  #monkeypatch.setattr(exported.write_message, 'msg', msg)

  eng = cmds.CmdEngine()
  cast = cmds.CastCmd(u"перенос", u"меня")

  eng.start()

  eng.put(cast)
  #time.sleep(11)
  eng.put(cast)
  #time.sleep(1)
  eng.stop()

  #assert msg is not None
