# -*- coding: utf-8 -*-
from lyntin.modules.sowmud import mapper

def test_room_cmp():
  r1 = mapper.Room()
  r2 = mapper.Room()
  r3 = mapper.Room()
  r4 = mapper.Room()
  assert cmp(r1, r2) == 0

  r4.set_exits(["n", "e"])
  assert cmp(r1, r4) != 0

  r3.add_desc_line("Room 3 is dark")
  assert cmp(r1, r3) != 0

  r2.set_name("Room 2")
  assert cmp(r1, r2) != 0
