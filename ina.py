#!/usr/bin/env python3

import time
import sys
from pathlib import Path
import io

import curses
import select

import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

blind_mode = False
SEEK_END = 2
TAIL_COUNT = 1024
WRAP_MARGIN = 15
start_words = 0
POMODORO_TIME = "25"

def flash(stdscr):
    cur_y, cur_x = stdscr.getyx()
    max_y = stdscr.getmaxyx()[0]
    for y in range(max_y):
        stdscr.chgat(y, 0, curses.A_REVERSE)
    stdscr.refresh()
    time.sleep(0.1)
    for y in range(max_y):
        stdscr.chgat(y, 0, curses.A_NORMAL)
    stdscr.refresh()
    stdscr.move(cur_y, cur_x)

def check_file(fname):
    global start_words
    ret = None
    whole = None
    fpath = Path(fname)
    if fpath.exists():
        with fpath.open("rt") as fin:
            fin.seek(0, SEEK_END)
            if fin.tell() > TAIL_COUNT:
                fin.seek(fin.tell() - TAIL_COUNT)
                ret = fin.read()
            fin.seek(0)
            whole = fin.read()
    if ret is None:
        ret = whole
    if whole is not None:
        for line in whole:
            start_words += len(line.split())
    return ret

def write(stdscr, data):
    global blind_mode
    global code
    cur_y = stdscr.getyx()[0]
    if isinstance(data, str):
        max_x = stdscr.getmaxyx()[1]
        limit = int(max_x // WRAP_MARGIN)
        if blind_mode:
            limit = limit + limit
        limit = max_x - limit
        for d in data:
            if d == " " and stdscr.getyx()[1] >= limit:
                if blind_mode:
                    stdscr.addstr("\r")
                    stdscr.clrtoeol()
                else:
                    stdscr.addstr("\n")
            elif d in "\n" and blind_mode:
                stdscr.addstr("\r")
                stdscr.clrtoeol()
            else:
                stdscr.addstr(d)
    else:
        if blind_mode:
            write(stdscr, "\n")
        else:
            for d in data:
                write(stdscr, d)
                stdscr.addstr("\n")

def getch(stdscr, block=True, timeout=None):
    stdscr.refresh()
    if timeout:
        check = select.select([sys.stdin], [], [], timeout)[0]
        if len(check) == 0:
            return None
        ret = stdscr.get_wch()
    elif block:
        ret = stdscr.get_wch()
    else:
        stdscr.nodelay(1)
        try:
            ret = stdscr.getkey()
            if ret == curses.ERR:
                ret = None
        except:
            ret = None
        finally:
            stdscr.nodelay(0)
    if isinstance(ret, str) and len(ret) == 1 and (ord(ret) < 0x20 or ord(ret) == 0x7f):
        if ret not in "\t\n":
            ret = ord(ret)
    return ret

def human_duration(seconds, floor=0):
    if seconds is None or seconds == "":
        return "??:??"
    if isinstance(seconds, str):
        if seconds.strip() == "":
            return "??:??"
        seconds = float(seconds)

    tiny = ""
    tiny_bit = seconds % 1.0
    neg = ""
    if seconds < 0:
        neg = "-"
        seconds = -seconds
    if floor == 0:
        pass
    elif floor < 0:
        if tiny_bit > 0:
            tiny = "{:.{floor}f}".format(tiny_bit, floor=-floor)[1:]
    elif floor != True:
        tiny = "{:.{floor}f}".format(tiny_bit, floor=floor)[1:]
    out = "{:02d}{}".format(int(seconds) % 60, tiny)
    n = int(seconds) // 60
    if n > 0:
        out = "{:02d}:{}".format(n % 60, out)
        n //= 60
    else:
        out = "00:{}".format(out)
    if n > 0:
        out = "{:02d}:{}".format(int(n) % 24, out)
        n //= 24
    if n > 0:
        out = "{}:{}".format(int(n), out)
    if neg:
        out = neg + out
    return out


def shared_write(outf, stdscr, what):
    global code
    outf.write(what)
    write(stdscr, what)

def from_human_duration(code, *, minutes = False):
    if code is None or isinstance(code, int) or isinstance(code,float) or code == "":
        return code
    splits = code.split(":")
    if minutes:
        splits.append(0)
    ret = 0
    if len(splits) > 3:
        ret += float(splits[0])
        del splits[0]
    ret *= 24
    if len(splits) > 2:
        ret += float(splits[0])
        del splits[0]
    ret *= 60
    if len(splits) > 1:
        ret += float(splits[0])
        del splits[0]
    ret *= 60
    if len(splits) > 0:
        ret += float(splits[0])
    return ret


CTRL_X = ord("X") - ord("@")
CTRL_H = ord("H") - ord("@")
CTRL_R = ord("R") - ord("@")
CTRL_W = ord("W") - ord("@")
CTRL_T = ord("T") - ord("@")
CTRL_P = ord("P") - ord("@")
CTRL_B = ord("B") - ord("@")
CTRL_QUESTION = 0x7f
TODO_MARKER = "TODO"
contest_titles = {
    "war": "Word War",
    "race": "Word Race",
    "pomodoro": "Pomodoro"
}

def status_line(stdscr, *, run_time=None, contest_time=None, total_words=None,
                new_words = None, contest_words = None, contest_mode = None, contest_wpm = None):
    global contest_titles
    global blind_mode
    max_x = stdscr.getmaxyx()[1]
    y, x = stdscr.getyx()
    buf = ""
    left = ""
    center = ""
    right = ""

    if run_time is not None or new_words is not None:
        if buf != "":
            buf += "  "
        b = ["Session "]
        if run_time is not None:
            b.append(human_duration(run_time))
            if new_words is not None:
                b.append("/")
        if new_words is not None:
            b.append(str(new_words))
        left = "".join(b)
    if blind_mode:
        left += " [BLIND]"

    if buf != "":
        buf += "  "
    if contest_mode is not None:
        title = contest_titles.get(contest_mode, "Contest({})".format(contest_mode))
        b = [title, " "]
    else:
        b = []
    if contest_time is not None:
        b.append(human_duration(contest_time))
        if contest_words is not None:
            b.append("/")
    if contest_words is not None:
        b.append(str(contest_words))
    if contest_wpm is not None:
        if isinstance(contest_wpm, float):
            b.append(" {:.3f} WPM".format(contest_wpm))
        else:
            b.append(str(contest_wpm))
    center = "".join(b)

    if total_words is not None:
        right = "{} words".format(total_words)

    stdscr.addstr(0, 0, left)
    stdscr.clrtoeol()
    if center:
        stdscr.addstr(0, max_x // 2 - len(center) // 2, center)
    if right:
        stdscr.addstr(0, max_x - len(right), right)
    stdscr.move(1,0)
    stdscr.clrtoeol()
    stdscr.move(y,x)

def main(stdscr, argv = tuple()):
    global start_words
    global blind_mode
    txtfile = argv[0]
    stdscr.clear()
    stdscr.scrollok(1)
    stdscr.refresh()
    tail = check_file(argv[0])

    was_space = True
    if tail and tail[-1] and tail[-1][-1] not in " \n\r\t":
        was_space = False
        start_words -= 1
    new_words = 0
    start_duration = 0
    start_time = time.perf_counter()
    contest_mode = None
    contest_starttime = None
    contest_startwords = None
    contest_time = None
    contest_words = None

    stdscr.move(5,0)
    status_line(stdscr, run_time=time.perf_counter() - start_time, total_words=start_words + new_words, new_words = new_words)
    write(stdscr, "\n")
    write(stdscr, "Use ^X to exit. ^W for Word War. ^R for Word Race.\n" +
                  "^P to Pause Session. ^B for Blind Mode. ^T for Pomodoro.\n\n")
    if tail is None:
        write(stdscr, "(New File)\n")
    else:
        write(stdscr, "[...]")
        write(stdscr, tail)

    contest_data = None
    contest_wpm = None
    key = getch(stdscr, timeout=0.7)
    with open(txtfile, "at") as outf:
        while key != CTRL_X:
            if isinstance(key, str):
                if key in " \n\t":
                    if not was_space:
                        new_words += 1
                        outf.flush()
                    was_space = True
                else:
                    was_space = False
                shared_write(outf, stdscr, key)
            elif key in (CTRL_H, CTRL_QUESTION, curses.KEY_BACKSPACE, curses.KEY_DC):
                    if not was_space:
                        new_words += 1
                        shared_write(outf, stdscr, " ")
                    was_space = True
                    shared_write(outf, stdscr, TODO_MARKER)
                    shared_write(outf, stdscr, " ")
                    new_words += 1
                    outf.flush()

            elif key == CTRL_W:
                cur_y, cur_x = stdscr.getyx()
                question = "Word war for how long?"
                stdscr.addstr(1,0, question)
                curses.echo()
                resp = stdscr.getstr(1, len(question) + 1)
                got = str(resp, code)
                if got.strip() == "":
                    contest_time = None
                    contest_words = None
                    contest_bpm = None
                else:
                    try:
                        contest_time = time.perf_counter()
                        contest_data = from_human_duration(got, minutes=True)
                        contest_starttime = contest_time
                        contest_words = 0
                        contest_startwords = new_words
                        contest_mode = "war"
                    except ValueError:
                        contest_time = None
                        contest_words = None
                curses.noecho()
                stdscr.move(1,0)
                stdscr.clrtoeol()
                stdscr.move(cur_y, cur_x)

            elif key == CTRL_T:
                cur_y, cur_x = stdscr.getyx()
                contest_time = time.perf_counter()
                contest_data = from_human_duration(POMODORO_TIME, minutes=True)
                contest_starttime = contest_time
                contest_words = 0
                contest_startwords = new_words
                contest_mode = "pomodoro"
                stdscr.move(cur_y, cur_x)

            elif key == CTRL_P:
                cur_y, cur_x = stdscr.getyx()
                max_y, max_x = stdscr.getmaxyx()
                buf = []
                start_duration += time.perf_counter() - start_time
                for y in range(max_y):
                    buf.append(stdscr.instr(y, 0))
                stdscr.clear()
                msg = "Paused."
                stdscr.addstr(max_y // 2, max_x // 2 - len(msg) // 2, msg)
                getch(stdscr)
                stdscr.clear()
                for y in range(max_y):
                    stdscr.insstr(y, 0, buf[y])
                stdscr.move(cur_y, cur_x)
                stdscr.refresh()
                start_time = time.perf_counter()

            elif key == CTRL_R:
                cur_y, cur_x = stdscr.getyx()
                question = "Race for how many words?"
                stdscr.addstr(1,0, question)
                curses.echo()
                resp = stdscr.getstr(1, len(question) + 1)
                got = str(resp, code)
                if got.strip() == "":
                    contest_time = None
                    contest_words = None
                    contest_bpm = None
                else:
                    contest_starttime = time.perf_counter()
                    contest_time = time.perf_counter() - contest_starttime
                    try:
                        contest_data = int(got)
                        contest_startwords = new_words
                        contest_words = new_words - contest_startwords
                        contest_mode = "race"
                    except ValueError:
                        contest_time = None
                        contest_words = None
                curses.noecho()
                stdscr.move(1,0)
                stdscr.clrtoeol()
                stdscr.move(cur_y, cur_x)
                stdscr.refresh()

            elif key == CTRL_B:
                if blind_mode:
                    blind_mode = False
                else:
                    max_y = stdscr.getmaxyx()[0]
                    stdscr.clear()
                    stdscr.move(max_y // 2, 0)
                    blind_mode = True

            if contest_mode == "war":
                check = time.perf_counter() - contest_starttime
                if check < contest_data:
                    contest_time = contest_data - check
                    contest_words = new_words - contest_startwords
                    contest_wpm = contest_words / (check / 60)
                else:
                    contest_time = 0
                    flash(stdscr)
                    contest_mode = None

            elif contest_mode == "pomodoro":
                check = time.perf_counter() - contest_starttime
                if check < contest_data:
                    contest_time = contest_data - check
                    contest_words = new_words - contest_startwords
                    contest_wpm = contest_words / (check / 60)
                else:
                    contest_time = 0
                    flash(stdscr)
                    contest_mode = None

            elif contest_mode == "race":
                check = new_words - contest_startwords
                contest_words = contest_data - check
                contest_time = time.perf_counter() - contest_starttime
                contest_wpm = check / (contest_time / 60)
                if check >= contest_data:
                    contest_words = 0
                    stdscr.refresh()
                    flash(stdscr)
                    stdscr.refresh()
                    contest_mode = None

            status_line(stdscr,
                run_time = time.perf_counter() - start_time + start_duration, contest_wpm = contest_wpm,
                contest_time = contest_time, contest_mode = contest_mode, contest_words = contest_words,
                total_words = start_words + new_words, new_words = new_words)
            key = getch(stdscr, timeout=0.7)

if __name__ == "__main__":
    curses.wrapper(main, sys.argv[1:])

