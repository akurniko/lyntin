# -*- coding: utf-8 -*-
from lyntin import exported, utils, ansi, settings
from lyntin.modules import modutils
import time

class Room():
  unknown_name = u"Безымянная комната"

  in_battle = u"Не получится! Вы сражаетесь за свою жизнь!"
  cannot_go = u"Вы не можете идти в этом направлении..."

  def __init__(self, name = unknown_name, desc = u"Без описания"):
    self._ts = time.time()
    self._name = name
    self._desc = desc
    self._exits = u"без выходов"
    self._adjacent_rooms = {}
    #print self._desc

  def to(self, where):
    try:
      return self._adjacent_rooms[where]
    except KeyError:
      return None

  def adjacent(self, where, room):
    self._adjacent_rooms[where] = room

  def init_from_room(self, room):
    self._name = room._name
    self._desc = room._desc
    self._exits = room._exits

  def update(self, name, desc, exits):
    self._name = name
    self._desc = u"\n".join(desc)
    self._exits = exits

  def add_desc_line(self, line):
    self._desc = u"\n".join([self._desc, line])

  def set_name(self, name):
    self._name = name

  def timestamp(self):
    return self._ts

  def named(self):
    return self._name != Room.unknown_name

  def set_exits(self, exits):
    self._exits = exits

  def __str__(self):
    res = self._name + u" " + self._exits
    return res.encode(settings.LOCAL_ENCODING)

  def __cmp__(self, other):
    if self._name != other._name: return cmp(self._name, other._name)
    if self._desc != other._desc: return cmp(self._desc, other._desc)
    if self._exits != other._exits: return cmp(self._exits, other._exits)
    return 0

class Zone():
  def __init__(self):
    self._rooms = []
    self._current_room = Room()

  def add_room(self, current, direction, name, desc):
    room = Room(name, desc)
    room.adjacent(World.opposite_directions[direction], current)
    current.adjacent(room, direction)
    self._rooms.append(room)  

  def current_room(self):
    return self._current_room

class World():
  directions = ['n', 'e', 's', 'w', 'u', 'd']
  directions_sym = [u'С', u'В', u'Ю', u'З', u'^', u'v']
  opposite_directions = {'n': 's', 'e': 'w', 's': 'n', 'w': 'e', 'u': 'd', 'd': 'u'}

  def __init__(self):
    self._zones = []
    self._current_zone = Zone()
    self._moving = None
    self._expected_room = None
    self._look_room = None
    self._position_unknown = True

  def start_looking(self):
    exported.write_message("started looking")
    self._look_room = Room()

  def stop_looking(self):
    smm = exported.get_manager("sowmud")
    exits = smm.get_prompt().exits()
    self._look_room.set_exits(exits)

    cur = self._current_zone.current_room()
    looked = self._look_room

    if not cur.named():
      cur.init_from_room( looked )

    elif cmp( cur, looked ) != 0:
      if not self._position_unknown:
        self._current_zone = Zone()
        self._current_zone.current_room().init_from_room( looked )
        self._position_unknown = True
      else:
        exported.write_message( "Looked from unknown position, ended up with yet another different room!" )

    else:
      # Okay, we've looked at the room and it turned out to match
      # with our expectation, but the position might still be
      # unknown, so it seems there should be two concepts here
      # 1. room mismatch -> position unknown
      # 2. position already unknown -> lets start recording the zone
      self._position_unknown = False
      pass

    self._look_room = None

  def stop_moving(self):
    smm = exported.get_manager("sowmud")
    exits = smm.get_prompt().exits()
    self._look_room.set_exits(exits)

    cur = self._current_zone.current_room()
    looked = self._look_room

    if not cur.named():
      cur.init_from_room( looked )

    elif cmp( cur, looked ) != 0:
      if not self._position_unknown:
        self._current_zone = Zone()
        self._current_zone.current_room().init_from_room( looked )
        self._position_unknown = True
      else:
        exported.write_message( "Looked from unknown position, ended up with yet another different room!" )

    else:
      # Okay, we've looked at the room and it turned out to match
      # with our expectation, but the position might still be
      # unknown, so it seems there should be two concepts here
      # 1. room mismatch -> position unknown
      # 2. position already unknown -> lets start recording the zone
      self._position_unknown = False
      pass

    self._look_room = None

  def mudfilter_looking(self, text):
    exported.write_message("looking")
    smm = exported.get_manager("sowmud")
    prompt = smm.get_prompt()
    ts = prompt.timestamp()

    if (ts > self._look_room.timestamp()) and (prompt.current()):
      self.stop_looking()

    else:
      if not self._look_room.named():
        self._look_room.set_name(text)
      else:
        self._look_room.add_desc_line(text)

  def mudfilter_moving(self, text):
    smm = exported.get_manager("sowmud")
    prompt = smm.get_prompt()
    ts = prompt.timestamp()

    if (ts > self._look_room.timestamp()) and (prompt.current()):
      self.stop_moving()

    else:
      if not self._look_room.named():
        self._look_room.set_name(text)
      else:
        self._look_room.add_desc_line(text)

  def userfilter(self, text):
    if text == "look":
      self.start_looking()

    if text in World.directions:
      self._moving = text
      self._expected_room = self._current_zone.current_room().to(text)

  def mudfilter(self, text):
    colorline = utils.filter_cm(text)
    nocolorline = ansi.filter_ansi(colorline)
    finalline = nocolorline.strip()

    if self._look_room is not None:
      self.mudfilter_looking(finalline)
    if self._expected_room is not None:
      self.mudfilter_moving(finalline)
    return text

  def status(self):
    smm = exported.get_manager("sowmud")
    if smm.enabled():
      exported.write_message("Current room: {0}, moving {1}, expected room: {2}, position unknown: {3}".format(
                             self._current_zone.current_room(), self._moving, self._expected_room, self._position_unknown))
    else:
      exported.write_message("Bot disabled")

commands_dict = {}

def map_status_cmd(ses, args, input):
  """
  Display the status of the mapper

  see also:  
  category: mapper
  """
  smm = exported.get_manager("sowmud")
  smm.get_world().status()

commands_dict["mapstatus"] = (map_status_cmd, "")

def load():
  """ Initializes the module by binding all the commands."""
  modutils.load_commands(commands_dict)

def unload():
  """ Unloads the module by calling any unload/unbind functions."""
  modutils.unload_commands(commands_dict.keys())
