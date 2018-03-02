# -*- coding: utf-8 -*-

from __future__ import print_function
from lyntin.utils import columnize

a = u"абвгдежзийклмнопрстуфхцчшщьыъэюя"
b = u"АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"

def test_columnize():
  columnize(a)
