# -*- coding: utf-8 -*-
from lyntin import exported

def group_reset():
  smm = exported.get_manager("sowmud")
  clerbot = smm.get_cler()
  clerbot.group_reset()

def group_mode( mode ):
  smm = exported.get_manager("sowmud")
  clerbot = smm.get_cler()
  clerbot.mode( mode )

def group_member_near(num, name, near):
  smm = exported.get_manager("sowmud")
  clerbot = smm.get_cler()
  clerbot.group_member_near( num, name.strip().decode("utf-8"), near )
  #print "adding group member near {0}".format(name.encode("cp866"))

def toggle_auto_summon():
  smm = exported.get_manager("sowmud")
  clerbot = smm.get_cler()
  clerbot.toggle_auto_summon()

def on_prompt():
  pass

def on_appear(name):
  smm = exported.get_manager("sowmud")
  clerbot = smm.get_cler()
  clerbot.on_appear(name.strip().decode("utf-8"))

def palad_mute(name, flag):
  smm = exported.get_manager("sowmud")
  clerbot = smm.get_cler()
  clerbot.palad_mute(name, flag)

def clerbot_action():
  smm = exported.get_manager("sowmud")
  clerbot = smm.get_cler()
  clerbot.action()
