# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from builtins import map
from builtins import object
from . import bot

class MageBot(bot.Bot):
  storm_spell = u"гроза"

  def __init__(self, cmd_engine, event_classifier, myself):
    bot.Bot.__init__(self, cmd_engine, event_classifier, myself)

    frag_mod = bot.FragMod(cmd_engine, event_classifier, self._group_list)
    frag_mod.set_rotation(MageBot.storm_spell)
    self.add_mod(frag_mod, "frag_mod")

    summon_mod = bot.AutoSummonMod(cmd_engine, event_classifier, self._group_list, True)
    self.add_mod(summon_mod, "summon_mod")

  def set_rotation(self, rotation):
    self._mods["frag_mod"].set_rotation(rotation)
