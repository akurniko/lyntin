from lyntin import exported
from lyntin.modules.sowmud import sowmud, mapper
from lyntin.modules import modutils

commands_dict = {}

def bot_on_cmd(ses, args, input):
  """
  Turn on SowMud bot

  see also:  
  category: bot
  """
  smm = exported.get_manager("sowmud")
  smm.turn_on()

commands_dict["boton"] = (bot_on_cmd, "")

def bot_off_cmd(ses, args, input):
  """
  Turn off SowMud bot

  see also:  
  category: bot
  """
  smm = exported.get_manager("sowmud")
  smm.turn_off()

commands_dict["botoff"] = (bot_off_cmd, "")


smm = None

def load():
  """ Initializes the module by binding all the commands."""
  global smm
  modutils.load_commands(commands_dict)
  smm = sowmud.SowmudManager()
  exported.add_manager("sowmud", smm)
  mapper.load()
  
  exported.hook_register("mud_filter_hook", smm.mudfilter, 76)
  exported.hook_register("user_filter_hook", smm.userfilter, 21)
  exported.hook_register("disconnect_hook", smm.reconnect, 50)

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  modutils.unload_commands(commands_dict.keys())
  mapper.unload()
  exported.remove_manager("sowmud")

  exported.hook_unregister("mud_filter_hook", smm.mudfilter)
  exported.hook_unregister("user_filter_hook", smm.userfilter)
  exported.hook_unregister("disconnect_hook", smm.reconnect)
