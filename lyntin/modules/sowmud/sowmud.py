from lyntin import exported, manager, utils, ansi
import prompt
import mapper
import cler
import cmds

class SowmudManager(manager.Manager):
  def __init__(self):
    self._enabled = False

    self._cmd_engine = cmds.CmdEngine()
    self._prompt = prompt.Prompt()
    self._world = mapper.World()
    self._clerbot = cler.ClerBot(self._cmd_engine)

  def mudfilter(self, args):
    ses = args["session"]
    text = args["dataadj"]

    colorline = utils.filter_cm(text)
    nocolorline = ansi.filter_ansi(colorline)

    if nocolorline == "\n":
      return text
    if self._enabled:
      text = self._prompt.mudfilter(text)
      text = self._world.mudfilter(text)

      if self._prompt.current():
        self._clerbot.on_prompt()
      else:
        text = self._clerbot.mudfilter(text)

    with open('nocolor.log', 'a') as f:
      try:
        f.write(ansi.filter_ansi(text).encode("utf-8"))
      except TypeError:
        exported.write_message("sowmud.mudfilter: ERROR: unexpected return type by submodule: {0}".format(type(text)))
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

      self._prompt.turn_on()
      self._cmd_engine.start()
      self._clerbot.start()
      exported.write_message("Turning bot on")

  def turn_off(self):
    if not self._enabled:
      exported.write_message("Bot is not on")
    else:
      self._enabled = False

      self._prompt.turn_off()
      self._cmd_engine.stop()
      self._clerbot.stop()
      exported.write_message("Turning bot off")

  def get_world(self):
    return self._world

  def get_prompt(self):
    return self._prompt

  def get_cler(self):
    return self._clerbot

  def enabled(self):
    return self._enabled

  def reconnect(self, args):
    prev_ses = args['session'].getName()
    exported.write_message("disconnected from SoW, {0}".format(prev_ses))
    exported.lyntin_command("#session a{0} sowmud.ru 5555".format(prev_ses))
