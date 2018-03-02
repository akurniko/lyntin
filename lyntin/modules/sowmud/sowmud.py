from __future__ import absolute_import
import threading
from lyntin import exported, manager, utils, ansi
from . import prompt
from . import mapper
from . import cler
from . import mage
from . import cmds
from . import proxy
from . import events
from . import irc

class SowmudManager(manager.Manager):
  def __init__(self):
    self._enabled = False

    self._cmd_engine = cmds.CmdEngine()
    self._event_classifier = events.EventClassifier()
    self._prompt = prompt.Prompt(self._event_classifier)
    self._world = mapper.World()
    self._bot = None
    self._proxy = proxy.Proxy(5556)
    self._irker = irc.Irker("irc.cs.hut.fi", "lyntin")
    threading.Thread(target = self._irker.start).start()

  def mudfilter(self, args):
    ses = args["session"]
    text = args["dataadj"]

    colorline = utils.filter_cm(text)
    nocolorline = ansi.filter_ansi(colorline)

    if nocolorline == "\n":
      return text
    #if self._enabled:
    self._event_classifier.mudfilter(text)

    if self._event_classifier.is_gagged():
      text = ""

    with open('nocolor.log', 'ab') as f:
      try:
        f.write(ansi.filter_ansi(text).encode("utf-8"))
      except TypeError:
        exported.write_message("sowmud.mudfilter: ERROR: unexpected return type by submodule: {0}".format(type(text)))
        text = ""
    self._proxy.send(text)
    return text

  def userfilter(self, args):
    ses = args["session"]
    internal = args["internal"]
    verbatim = args["verbatim"]
    text = args["dataadj"]

    #exported.write_message(str(ses))
    if (ses.getName() != "common") and self._enabled:
      self._world.userfilter(text)
    return text
    
  def turn_on(self):
    if self._enabled:
      exported.write_message("Bot is already on")
    else:
      self._enabled = True

      self._cmd_engine.start()
      self._bot.start()
      exported.write_message("Turning bot on")

  def turn_off(self):
    if not self._enabled:
      exported.write_message("Bot is not on")
    else:
      self._enabled = False

      self._cmd_engine.stop()
      self._bot.stop()
      exported.write_message("Turning bot off")

  def status(self):
    status = self._bot.status()
    exported.write_message(status)

  def get_world(self):
    return self._world

  def get_prompt(self):
    return self._prompt

  def set_bot_mage(self, myself, irc_nick = "lyntin"):
    if self._bot is not None:
      self.turn_off()
      self._bot.unregister()
    self._bot = mage.MageBot(self._cmd_engine, self._event_classifier, myself)
    self._irker.nickname(irc_nick)
    self.turn_on()

  def set_bot_cler(self, myself, irc_nick = "lyntin"):
    if self._bot is not None:
      self.turn_off()
      self._bot.unregister()
    self._bot = cler.ClerBot(self._cmd_engine, self._event_classifier, myself)
    self._irker.nickname(irc_nick)
    self.turn_on()

  def get_bot(self):
    return self._bot

  def enabled(self):
    return self._enabled

  def reconnect(self, args):
    prev_ses = args['session'].getName()
    self.turn_off()
    exported.write_message("disconnected from SoW, {0}".format(prev_ses))
    exported.lyntin_command("#session a{0} sowmud.ru 5555".format(prev_ses))
