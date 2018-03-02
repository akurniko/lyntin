# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from builtins import map
from builtins import object
from lyntin import exported, utils, ansi, settings
from lyntin.modules import modutils
import socket
import threading

class Proxy(object):
  def __init__(self, port):
    self._socket = socket.socket()
    self._clients = []
    try:
      self._socket.bind( ("localhost", port) )
      self._socket.listen()
      threading.Thread(target = Proxy.acceptor, args = [self]).start()
    except:
      pass

  def acceptor(self):
    exported.write_message("SowMud Proxy: DEBUG: started the acceptor")
    while True:
      try:
        sock, addr = self._socket.accept()
        self._clients.append(sock)
        threading.Thread(target = Proxy.receiver, args = [self, sock]).start()
        exported.write_message("SowMud Proxy: DEBUG: client connected")
      except:
        return

  def send(self, text):
    for c in self._clients:
      try:
        c.send(text.encode(settings.PROXY_ENCODING))
      except:
        exported.write_message("SowMud Proxy: DEBUG: client lost in send")
        self.remove_client(c)

  def remove_client(self, client):
    try:
        client.close()
    except:
        pass

    try:
        self._clients.remove(client)
    except:
        pass

  def receiver(self, sock):
    #session = exported.get_current_session()
    while True:
      try:
        data = sock.recv(4096)
        #session.handle_user_data(data.decode(settings.PROXY_ENCODING))
        if len(data) == 0:
            exported.write_message("SowMud Proxy: DEBUG: client lost in receive")
            return
        data = data.strip()
        exported.lyntin_command(data.decode(settings.PROXY_ENCODING))
      except:
        exported.write_message("SowMud Proxy: DEBUG: client lost in receive")
        self.remove_client(sock)
        return
