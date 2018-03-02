# -*- coding: utf-8 -*-
from lyntin import exported

def set_bot_mage(myself, irc_nick):
  smm = exported.get_manager("sowmud")
  bot = smm.set_bot_mage(myself, irc_nick)

def set_bot_cler(myself, irc_nick):
  smm = exported.get_manager("sowmud")
  bot = smm.set_bot_cler(myself, irc_nick)

def set_rotation(rotation):
  smm = exported.get_manager("sowmud")
  necrbot = smm.get_bot()
  necrbot.set_rotation(rotation)

def on_clan_message(name, message):
  smm = exported.get_manager("sowmud")
  chatbot = smm.get_chat()
  string = u"{0}: {1}".format(name, message)
  chatbot.send(string)

quest = {}

def on_ingr(mob, zone):
  global quest
  if zone in quest:
    if mob not in quest[zone]:
      quest[zone].append(mob)
  else:
    quest[zone] = [mob]

def display_ingr():
  global quest
  for k, v in quest.items():
    mobs = ", ".join(v)
    exported.lyntin_command("gtell |{:^25}: {mobs}".format(k, mobs=mobs))
  quest = {}
