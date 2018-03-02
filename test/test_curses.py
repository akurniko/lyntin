# -*- coding: utf-8 -*-

from __future__ import print_function
import locale
import curses
from curses import ascii

group_setup = [u"1 Шыгос",
               u"2 Алиант",
               u"3 Цушка",
               u"4 Дарсу"]

group_setup1 = [u"1 Shygos",
                u"2 Aliant",
                u"3 Tsushka",
                u"4 Darsu"]

a = u"абвгдежзийклмнопрстуфхцчшщьыъэюя"
b = u"АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"

def init_curses():
    curses.noecho()
    curses.raw()
    #curses.cbreak()

    stdscr = curses.initscr()
    return stdscr

def shutdown_curses(stdscr):
    stdscr.keypad(0);
    curses.nocbreak();
    curses.echo()
    curses.endwin()

def main():
    #stdscr = init_curses()
    curses.wrapper(main_loop)
    #shutdown_curses(stdscr)
    code = locale.getpreferredencoding()
    print (a.encode(code))
    print (b)

def main_loop(stdscr):
    (screen_h, screen_w) = stdscr.getmaxyx()
    win = curses.newwin(1, screen_w, screen_h-1, 0)

    locale.setlocale(locale.LC_ALL, "")
    code = locale.getpreferredencoding()

    #print group_setup[0]
    #print group_setup1[0]
    ch = win.getch()
    #print ch
    stdscr.addstr(0,0,group_setup[0].encode(code))
    #stdscr.addstr(group_setup1[0])
    stdscr.refresh()
    ch = win.getch()
    stdscr.addstr(1,0,group_setup[1].encode(code))
    stdscr.addstr(2,50,group_setup[1].encode(code))
    stdscr.addstr(3,50,group_setup1[1].encode(code))
    stdscr.addstr(4,50,a.encode(code))
    stdscr.addstr(5,50,b.encode(code))
    stdscr.addstr(6,50,"b[0].isprint: " + str(ascii.isprint(ord(b[0]))))
    stdscr.addstr(7,50,b)
    stdscr.refresh()
    win.nodelay(False)
    #print(ch)
    x = 50
    y = 8
    while True:
        ch = win.get_wch()
        stdscr.addstr(y,x,ch)
        x = x + 1
        if x > 100:
            x = 50
            y = y + 1
        stdscr.refresh()

if __name__ == "__main__":
    main()
