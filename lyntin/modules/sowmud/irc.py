# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from builtins import map
from builtins import object
from lyntin import exported, utils, ansi, settings
import irc.client
import irc.bot
import irc.strings
import socket
import threading
import random

class Irker(irc.bot.SingleServerIRCBot):
  def __init__(self, server, nickname, port=6667):
    irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
    random.seed()
    self.channel = "#sowmud"
    self.nick = nickname

  def on_nicknameinuse(self, c, e):
    c.nick(c.get_nickname() + "_")

  def on_welcome(self, c, e):
    c.join(self.channel)
    self.connection.nick(self.nick)

  def on_privmsg(self, c, e):
    self.do_command(e, e.arguments[0])

  def on_pubmsg(self, c, e):
    a = e.arguments[0].split(":", 1)
    if ( ( len(a) > 1 ) and
         ( irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()) ) ):
      self.do_command(e, a[1].strip())
    return

  def do_command(self, e, cmd):
    if cmd == "disconnect":
      exported.lyntin_command("#zap")

    if cmd == "smile":
      exported.lyntin_command("улыбнуться", internal=1)

    if cmd == "connect":
      r = random.randint(0, 10)
      exported.lyntin_command("#session a{0} sowmud.ru 5555".format(r))

  def send(self, text):
    self.connection.privmsg(self.channel, text)

  def nickname(self, nick):
    self.nick = nick
    try:
      self.connection.nick(nick)
    except irc.client.ServerNotConnectedError:
      pass
