#!/usr/bin/env python3

import time
import sys
from pathlib import Path
import io
import os
import re
import glob

import curses
import select
import argparse
from configparser import ConfigParser

import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

parser = argparse.ArgumentParser(
    description="This is an Idiotic NaNoWriMo Appender.")
parser.add_argument("--user-config", metavar="DIR", 
        help="Specify an alternate user configuration directory.")
parser.add_argument("file", nargs='?', 
                    help="Name of target file to append to.")
parser.add_argument("--one-line", "-b", action='store_true',
        help="Enable one-line mode from the start.")
parser.add_argument("--generate-config", action='store_true',
        help="Create a config file in ~/.config/ina/settings.conf")
parser.add_argument('--version', action='version', version='ina Version 0.9+PROJECT.1')


config = ConfigParser(inline_comment_prefixes=None)


DEFAULT_TAIL_COUNT = 280
DEFAULT_WRAP_MARGIN = "15"
DEFAULT_POMODORO_TIME = "25" 
DEFAULT_UNTITLED_FILENAME = "./%Y-%m-%d.txt"
DEFAULT_TODO_MARKER = "TODO"

dist_config = '''
[general]
## untitled-filename
##      While many applications may default to "Untitled", this
##      is guaranteed to be a bad title in every circumstance.
##      `ina` defaults to using date-based files in the current
##      directory. You can use an explicit journal directory
##      by specifying a path.
##
##      ~ is expanded to your home directory.
##
##      The standard strftime-based '%' escapes are available, so:
##          %a : Locale's abbreviated weekday name
##          %A : Locale's full weekday name
##          %b : Locale's abbreviated month name
##          %B : Locale's full month name
##          %c : Locale's appropriate date and time
##          %d : Day of month [01,31]
##          %H : Hour (24 hour clock) [00,23]
##          %I : Hour (12 hour clock) [01,12]
##          %j : day of year as number [001,366]
##          %m : month as number [01,12]
##          %M : minute [00,59]
##          %p : Locale's equivalent of AM/PM
##          %S : second as number [00,61]
##          %U : week number (Sunday as start of week) [00,53]
##          %w : weekday as number starting at Sunday [0,6]
##          %W : week number (Monday as start of week) [00,53]
##          %x : Locale's appropriate date
##          %X : Locale's appropriate time
##          %y : Year without century [00,99]
##          %Y : Year with century
##          %z : Time zone offset from UTC
##          %Z : Time zone name
##          %% : literal '%' character.
##
## Maybe you want something useless, but more standard.
# untitled-filename: ./Untitled Draft.txt 
## The default, current directory date-based: ./2017-03-11.txt
# untitled-filename: ./%Y-%m-%d.txt
## Journal directory hour-based file: ~/Journal/2017-03/11-13.txt
# untitled-filename: ~/Journal/%Y-%m/%d-%H.txt
## Documents folder, week-based file: ~/Documents/Early-Draft-2017-10.txt
# untitled-filename: ~/Documents/Early-Draft-%Y-%W.txt

## tail-count
##      We display the tail end of the file being appended to when
##      we start. You have a number of ways to specify this value,
##      but remember: This is limited to the last screenful of text
##      at most, so this really only changes whether you're likely
##      to see the help text.
##
##      All longer words have a short form. The trailing 's' may be
##      present or omitted. ("1 paragraph" or "1 paragraphs" are
##      both valid the file's purpose.)
##
## The default, the last 280 Unicode codepoints in the file.
## (May also be written as 'characters' or 'codepoints'.)
# tail-count: 280 chars
## The last five minutes work, if typing at 40 WPM
# tail-count: 200 words
## The last 10 lines, like the standard `tail` command
# tail-count: 10 lines
## The last paragraph
## (May also be written as 'paragraphs'.)
# tail-count: 1 para

## pomodoro-time
##      The ^T key starts a "pomodoro". The standard duration of a
##      pomodoro is 25 minutes, however in NaNo land a lot of folks
##      use 20 minute sprints with 10 minute breaks.
##
## Standard Pomodoro time according to the book
# pomodoro-time: 25
## Common Word Sprint time
# pomodoro-time: 20

## pomodoro-during-run
##      By default, during the Pomodoro, you don't see your time-left
##      and you don't see how many words you've typed. You see a
##      spinner, indicating time is passing, and you see your speed.
##
## The default is just the rate (spinner shows when 'time' is off)
# pomodoro-during-run: rate
## To make Pomodoro mode work like 'Word War'
# pomodoro-during-run: words time rate

## todo-marker
##      When you accidentally hit backspace and some other editing keys,
##      it will insert a to-do marker ("TODO" by default). If you
##      prefer another marker, change that here.
# todo-marker: TODO

## wrap-margin
##      Because 'ina' is not an editor, it has no concept of the text you
##      have entered. It can't go back a few letters and wrap a word you
##      have already started typing. Because of this, it uses a ragged
##      margin where as soon as you type a space in this margin, it
##      wraps your text. This is handled as a percentage of screen size.
# wrap-margin: 15
'''





CTRL_X = ord("X") - ord("@")
CTRL_H = ord("H") - ord("@")
CTRL_R = ord("R") - ord("@")
CTRL_W = ord("W") - ord("@")
CTRL_T = ord("T") - ord("@")
CTRL_L = ord("L") - ord("@")
CTRL_P = ord("P") - ord("@")
CTRL_B = ord("B") - ord("@")
CTRL_QUESTION = 0x7f
CONTEST_TITLES = {
    "war": "Word War",
    "race": "Word Race",
    "pomodoro": "Pomodoro"
}

class UiComponent:
    oneln_mode = False
    wrap_margin = int(DEFAULT_WRAP_MARGIN)
    _last_max_x = -1
    _last_max_y = -1
    def __init__(self, stdscr):
        self.stdscr = stdscr 
        self.need_reset = True

    def reset(self):
        self.need_reset = False
        self.stdscr.clear()
        self.stdscr.scrollok(1)
        max_y = self.stdscr.getmaxyx()[0]
        if max_y > 10:
            self.stdscr.move(5,0)
        elif max_y >= 3:
            self.stdscr.move(2,0)
        else:
            self.stdscr.move(0,0)
        self.stdscr.refresh()

    def status_line(self, *, run_time=None, contest_time=None,
                    total_words=None, new_words = None, contest_words = None,
                    contest_mode = None, contest_wpm = None,
                    oneline = False):
        stdscr = self.stdscr
        global CONTEST_TITLES
        max_y, max_x = self.stdscr.getmaxyx()
        if max_y < 3:
            return
        if max_y != self._last_max_y or max_x != self._last_max_x:
            self.need_reset = True
            self._last_max_x = max_x
            self._last_max_y = max_y
        y, x = stdscr.getyx()
        buf = ""
        left = ""
        center = ""
        right = ""

        if run_time is not None or new_words is not None:
            if buf != "":
                buf += "  "
            if max_x < 40:
                b = ["S."]
            else:
                b = ["Session "]
            if run_time is not None:
                b.append(human_duration(run_time))
                if new_words is not None:
                    b.append("/")
            if new_words is not None:
                b.append(str(new_words))
            left = "".join(b)
        if self.oneln_mode:
            if max_x < 40:
                left += " OL"
            else:
                left += " [One-Line]"

        if buf != "":
            buf += "  "
        if contest_mode is not None and max_x >= 40:
            title = CONTEST_TITLES.get(contest_mode, "Contest({})".format(contest_mode))
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
            if max_x < 40:
                right = "{}w".format(total_words)
            else:
                right = "{} words".format(total_words)

        stdscr.move(0, 0)
        stdscr.clrtoeol()
        ce = len(center)
        ri = len(right)
        le = len(left)
        if center and ce + ri + le + 2+ 2  >= max_x:
            if max_x < 6:
                pass
            elif ce >= max_x:
                stdscr.addstr(0, 0, "...")
                stdscr.addstr(center[ce - max_x - 3:])
            else:
                stdscr.addstr(0, 0, center) 
        elif center:
            space = (max_x - ce - ri - le) // 2;
            stdscr.addstr(0, 0, left)
            stdscr.addstr(" " * space)
            stdscr.addstr(center)
            stdscr.addstr(" " * space)
            stdscr.addstr(right)
        elif ri + le + 1 >= max_x:
            if le < max_x:
                stdscr.addstr(0, 0, left) 
        else:
            space = (max_x - ri - le);
            stdscr.addstr(0, 0, left)
            stdscr.addstr(" " * space)
            stdscr.addstr(right)

        if max_y > 5:
            stdscr.move(1,0)
            stdscr.clrtoeol()
        stdscr.move(y,x)

    def _query_narrow(self, question):
        global code
        cur_y, cur_x = self.stdscr.getyx()
        max_y, max_x = self.stdscr.getmaxyx()

        buf = [] 
        for y in range(max_y):
            buf.append(self.stdscr.instr(y, 0))

        self.stdscr.clear() 
        self.stdscr.move(cur_y,0)
        self.write(question)
        self.write(" ")
        cy, cx = self.stdscr.getyx()
        curses.echo()
        resp = self.stdscr.getstr(cy, cx)
        got = str(resp, code)
        curses.noecho() 

        self.stdscr.clear()
        for y in range(max_y):
            self.stdscr.insstr(y, 0, buf[y])
        self.stdscr.move(cur_y, cur_x)
        self.stdscr.refresh()

        return got

    def _query_small(self, question):
        global code
        cur_y, cur_x = self.stdscr.getyx()
        buf = self.stdscr.instr(0, 0)
        self.stdscr.addstr(0,0, question)
        self.stdscr.clrtoeol() 
        curses.echo()
        resp = self.stdscr.getstr(0, len(question) + 1)
        got = str(resp, code)
        curses.noecho() 
        self.stdscr.move(0,0)
        self.stdscr.clrtoeol()
        self.stdscr.insstr(0, 0, buf) 
        self.stdscr.move(cur_y, cur_x)
        return got

    def _query_large(self, question):
        global code
        cur_y, cur_x = self.stdscr.getyx()
        self.stdscr.addstr(1,0, question) 
        curses.echo()
        resp = self.stdscr.getstr(1, len(question) + 1)
        got = str(resp, code)
        curses.noecho()
        self.stdscr.move(1,0)
        self.stdscr.clrtoeol() 
        self.stdscr.move(cur_y, cur_x)
        return got

    def query(self, question): 
        max_y, max_x = self.stdscr.getmaxyx()
        if max_x < len(question) + 10:
            return self._query_narrow(question)
        elif max_y > 5:
            return self._query_large(question)
        else:
            return self._query_small(question) 

    def shared_write(self, outf, what):
        outf.write(what)
        self.write(what)

    def flash(self):
        stdscr = self.stdscr
        # curses.flash() exists, but didn't work in iTerm2 on the Mac for me.
        cur_y, cur_x = self.stdscr.getyx()
        max_y = self.stdscr.getmaxyx()[0]
        for y in range(max_y):
            stdscr.chgat(y, 0, curses.A_REVERSE)
        stdscr.refresh()
        time.sleep(0.1)
        for y in range(max_y):
            stdscr.chgat(y, 0, curses.A_NORMAL)
        stdscr.refresh()
        stdscr.move(cur_y, cur_x)

    def write(self, data):
        global code
        stdscr = self.stdscr
        cur_y = stdscr.getyx()[0]
        if isinstance(data, str):
            max_y, max_x = self.stdscr.getmaxyx()
            cur_y, cur_x = self.stdscr.getyx()
            limit = int(max_x * self.wrap_margin / 100)
            limit = max_x - limit
            for d in data:
                if self.oneln_mode and max_y >= 3:
                    stdscr.addstr(cur_y - 1, cur_x, " " * len(d))
                    stdscr.move(cur_y, cur_x)
                if d in " -" and cur_x >= limit:
                    if self.oneln_mode and max_y >= 3:
                        stdscr.move(cur_y - 1, 0)
                        stdscr.clrtoeol()
                        stdscr.move(cur_y, cur_x)
                    stdscr.addstr(d)
                    stdscr.addstr("\n")
                elif d in "\n":
                    if self.oneln_mode and max_y >= 3:
                        stdscr.move(cur_y - 1, 0)
                        stdscr.clrtoeol()
                        stdscr.move(cur_y, cur_x)
                    stdscr.addstr(d)
                else:
                    stdscr.addstr(d)
        else:
            for d in data:
                write(stdscr, d)

    def getch(self, block=True, timeout=None):
        stdscr = self.stdscr
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

    def pause(self):
        stdscr = self.stdscr
        cur_y, cur_x = self.stdscr.getyx()
        max_y, max_x = self.stdscr.getmaxyx()
        buf = []
        for y in range(max_y):
            buf.append(stdscr.instr(y, 0))
        stdscr.clear()
        msg = "Paused."
        stdscr.addstr(max_y // 2, max_x // 2 - len(msg) // 2, msg)
        self.getch(stdscr)
        stdscr.clear()
        for y in range(max_y):
            stdscr.insstr(y, 0, buf[y])
        stdscr.move(cur_y, cur_x)
        stdscr.refresh()

    def toggle_oneline(self, new_state = None):
        if new_state is None:
            new_state = not self.oneln_mode
        if new_state:
            max_y = self.stdscr.getmaxyx()[0]
            cur_y, cur_x = self.stdscr.getyx()
            for y in range(1,cur_y - 1):
                self.stdscr.move(y, 0)
                self.stdscr.clrtoeol()
            self.stdscr.addstr(cur_y - 1, 0, " " * cur_x)
            self.stdscr.move(cur_y, cur_x)
        self.oneln_mode = new_state
        return new_state



class IdioticNanowrimoAppender:
    pomodoro_during_run = {"rate"}
    pomodoro_time = DEFAULT_POMODORO_TIME
    tail_count = DEFAULT_TAIL_COUNT
    tail_type = "char"
    start_words = 0

    def _parse(self, argv):
        global dist_config
        args = parser.parse_args(argv)
        if args.user_config is not None:
            home_dir = Path(args.user_config)
        else:
            home_dir = Path("~/.config/ina").expanduser()
            if not home_dir.exists():
                trial = Path("~/.ina").expanduser()
                if trial.exists():
                    home_dir = trial
        home_dir.mkdir(parents=True, exist_ok=True)
        home_config = home_dir / "settings.conf"
        if home_config.exists():
            config.read(str(home_config)) 
            if args.generate_config:
                home_config_dist = home_config.with_suffix(".conf.dist")
                home_config_dist.write_text(dist_config)
        elif args.generate_config:
            home_config.write_text(dist_config)

        if "general" not in config:
            config.add_section("general")
        if "pomodoro-during-run" in config["general"]:
            self.pomodoro_during_run = set(split(config["general"]["pomodoro-during-run"].strip()))
        self.pomodoro_time = config["general"].get("pomodoro-time", DEFAULT_POMODORO_TIME).strip()
        if "tail-count" in config["general"]:
            tc = config["general"]["tail-count"].strip().split()
            try:
                self.tail_count = int(tc[0])
                if len(tc) > 1:
                    self.tail_type = tc[1]
            except ValueError:
                pass
        untitled_filename = config["general"].get("untitled-filename", DEFAULT_UNTITLED_FILENAME).strip()
        self.one_line = args.one_line
        if args.file:
            self.filename = args.file
        else:
            self.filename = os.path.expanduser(time.strftime(untitled_filename))
        self.next_filename = None
        self.todo_marker = config["general"].get("todo-marker", DEFAULT_TODO_MARKER)
        self.wrap_margin = int(config["general"].get("wrap-margin", DEFAULT_WRAP_MARGIN))

    def check_any_file(self, filename):
        ret = None
        whole = None
        fpath = Path(filename)
        if fpath.exists():
            whole = fpath.read_text()
        ret = whole
        if whole is not None:
            self.start_words = len(whole.split())
            if self.tail_type in ("word", "words"):
                t = whole.replace("\n\n"," [NEW-PARAGRAPH]").split()[-self.tail_count:]
                ret = " ".join(t).replace(" [NEW-PARAGRAPH]", "\n\n")
                if not whole.endswith("\n\n") and whole.endswith("\n"):
                    ret = ret + "\n"
            elif self.tail_type in ("line", "lines"):
                ret = "\n".join(whole.split("\n")[-self.tail_count:])
            elif self.tail_type in ("character", "characters", "codepoint",
    "codepoints", "byte", "bytes", "char", "chars"):
                ret = whole[-self.tail_count:]
            elif self.tail_type in ("para", "paras", "paragraph", "paragraphs"):
                t = whole.split("\n\n")
                r = []
                t.reverse()
                for para in t:
                    para = para.strip()
                    if para == "":
                        continue
                    r.append(para)
                    if len(r) >= self.tail_count:
                        break
                r.reverse()
                if whole.endswith("\n\n"):
                    r.append("")
                    ret = "\n\n".join(r)
                elif whole.endswith("\n"):
                    ret = "\n\n".join(r) + "\n"
                else:
                    ret = "\n\n".join(r)
            else:
                ret = whole[-DEFAULT_TAIL_COUNT:]
        return ret


    def check_file(self):
        return self.check_any_file(self.filename)

    def __init__(self, args):
        self._parse(args)

    def _reload(self, outf = None):
        if outf is not None:
            outf.flush()
        tail = self.check_file() 
        self.was_seperator = True
        if tail and tail[-1] and tail[-1][-1] not in " \n\r\t":
            self.was_seperator = False
            self.start_words -= 1

        self.ui.reset()
        self.ui.status_line(run_time=time.perf_counter() - self.start_time,
                            total_words=self.start_words + self.new_words,
                            new_words = self.new_words)
        self.ui.write("\n")
        self.ui.write("Use ^X to exit. ^W for Word War. ^R for Word Race.\n" +
                  "^P to Pause Session. ^B for One-Line Mode. ^T for Pomodoro.\n\n")
        if tail is None or tail.strip() == "":
            self.ui.write("(Empty File)\n")
        else:
            self.ui.write("[...]")
            self.ui.write(tail)

    def _show_outline(self, order):
        fn = Path(self.filename)
        c = re.split("[-_]", fn.stem)
        if len(c) == 1:
            c = fn.stem.split(".")
            spec = c[0] + "*"
        else:
            spec = c[0] + "*" + fn.suffix
        things = []
        for what in glob.glob(str(fn.parent / spec)):
            p = Path(what)
            if not p.is_file():
                continue
            if p.suffix == ".bak" or p.suffix.endswith("~") or p.suffix.startswith("~") or p.suffix.endswith("#"):
                continue
            things.append(str(what))
        if not things:
            self.ui.write("<<Could not find navel.>>\n")
            return
        things.sort()
        if order >= len(things):
            order = 0
        if order < 0 and -order > len(things):
            order = 0
        outline = Path(things[order])
        tail = None
        if outline.exists():
            tail = self.check_any_file(str(outline))
        self.ui.write("\n")
        if tail is None or tail.strip() == "":
            self.ui.write("<<Not available.>>\n")
        else:
            self.ui.write("<<{}>> ".format(outline))
            self.ui.write(tail.strip())
            self.ui.write(" <<{}>>\n".format(outline))

    def load(self, stdscr): 
        self.ui = UiComponent(stdscr)
        self.ui.toggle_oneline(self.one_line)
        self.ui.wrap_margin = self.wrap_margin
        self.new_words = 0
        self.start_duration = 0
        self.start_time = time.perf_counter() 
        self.contest_mode = None
        self.contest_starttime = None
        self.contest_startwords = None
        self.contest_time = None
        self.contest_words = None
        self.contest_data = None
        self.contest_wpm = None 

    def _update_status(self):
        self.ui.status_line(
            run_time = time.perf_counter()
                        - self.start_time + self.start_duration,
            contest_wpm = self.contest_wpm,
            contest_time = self.contest_time,
            contest_mode = self.contest_mode,
            contest_words = self.contest_words,
            total_words = self.start_words + self.new_words,
            new_words = self.new_words)

    def _do_input(self, outf, key): 
        if key in "- \n\t":
            if not self.was_seperator:
                self.new_words += 1
                outf.flush()
            self.was_seperator = True
        else:
            self.was_seperator = False
        self.ui.shared_write(outf, key)

    def _do_todo(self, outf): 
        if not self.was_seperator:
            self.new_words += 1
            self.ui.shared_write(outf, " ")
        self.was_seperator = True
        self.ui.shared_write(outf, self.todo_marker)
        self.ui.shared_write(outf, " ")
        self.new_words += 1
        outf.flush()

    def _do_pomodoro(self): 
        self.contest_data = from_human_duration(self.pomodoro_time, minutes=True)
        self.contest_starttime = time.perf_counter()
        self.contest_startwords = self.new_words
        self.contest_words = None
        self.contest_time = None
        self.contest_mode = "pomodoro"

    def _do_pause(self):
        self.start_duration += time.perf_counter() - self.start_time
        self.ui.pause()
        self.start_time = time.perf_counter()

    def _do_war(self):
        question = "Word war for how long?"
        got = self.ui.query(question) 
        self.contest_time = None
        self.contest_words = None
        self.contest_wpm = None 
        if got.strip() != "":
            self.contest_data = from_human_duration(got, minutes=True)
            if self.contest_data != 0:
                self.contest_time = time.perf_counter()
                self.contest_starttime = self.contest_time
                self.contest_words = 0
                self.contest_startwords = self.new_words
                self.contest_mode = "war"
            else:
                self.contest_mode = None
        else:
            self.contest_mode = None

    def _do_race(self): 
        question = "Race for how many words?"
        got = self.ui.query(question)
        self.contest_time = None
        self.contest_words = None
        self.contest_wpm = None 
        if got.strip() != "":
            try:
                self.contest_data = int(got)
            except ValueError:
                self.contest_data = 0
            if self.contest_data != 0:
                self.contest_starttime = time.perf_counter()
                self.contest_startwords = self.new_words
                self.contest_time = time.perf_counter() - self.contest_starttime
                self.contest_words = self.new_words - self.contest_startwords
                self.contest_mode = "race"
            else:
                self.contest_mode = None
        else:
            self.contest_mode = None

    def _do_oneline(self):
        if not self.ui.toggle_oneline():
            self._reload()

    def _run_key(self, outf, key):
        if isinstance(key, str):
            self._do_input(outf, key)
        elif key in (CTRL_H, CTRL_QUESTION,
                        curses.KEY_BACKSPACE, curses.KEY_DC):
            self._do_todo(outf)
        elif key == CTRL_W:
            self._do_war()
        elif key == CTRL_T:
            self._do_pomodoro()
        elif key == CTRL_P:
            self._do_pause()
        elif key == CTRL_R:
            self._do_race()
        elif key == CTRL_B:
            self._do_oneline()
        elif key == 393:
            self._show_outline(0)
        elif key == 402:
            self._show_outline(-1)
        elif key == curses.KEY_RESIZE or key == CTRL_L:
            self._reload(outf)
        elif key == 336:
            self._load_next(outf, 1)
        elif key == 337:
            self._load_next(outf, -1)
        elif key is not None:
            self._do_todo(outf)
            # self.ui.write(str(key))

    def _load_next(self, outf, offset):
        fn = Path(self.filename)
        pattern = re.compile(r"([0-9]+)")
        got = re.findall(pattern, fn.stem)
        if len(got) != 1:
            return
        orig = got[0]
        newn = int(orig) + offset
        if newn < 1:
            self.ui.flash()
            return
        new = str(newn)
        while len(new) < len(orig):
            new = "0" + new
        self.next_filename = self.filename.replace(orig, new)
        outf.close()
        return 

    def _calculate_war(self): 
        check = time.perf_counter() - self.contest_starttime
        self.contest_time = self.contest_data - check
        self.contest_words = self.new_words - self.contest_startwords
        self.contest_wpm = self.contest_words / (check / 60)
        if self.contest_time <= 0:
            self.contest_time = 0
            self.ui.flash()
            self.contest_mode = None

    def _calculate_pomodoro(self): 
        check = time.perf_counter() - self.contest_starttime
        w = self.new_words - self.contest_startwords
        if "rate" in self.pomodoro_during_run:
            self.contest_wpm = w / (check / 60)
        if "time" in self.pomodoro_during_run:
            self.contest_time = self.contest_data - check
        else:
            self.contest_time = '[' + "\\-/|"[int(time.perf_counter())%4] + ']'
        if "words" in self.pomodoro_during_run:
            self.contest_words = w
        if check >= self.contest_data:
            self.contest_words = w
            self.contest_wpm = w / (check / 60)
            self.contest_time = 0
            self.ui.flash()
            self.contest_mode = None

    def _calculate_race(self):
        check = self.new_words - self.contest_startwords
        self.contest_words = self.contest_data - check
        self.contest_time = time.perf_counter() - self.contest_starttime
        self.contest_wpm = check / (self.contest_time / 60)
        if check >= self.contest_data:
            self.contest_words = 0
            self.ui.flash()
            self.contest_mode = None

    def _run_contests(self):
        if self.contest_mode == "war":
            self._calculate_war()
        elif self.contest_mode == "pomodoro":
            self._calculate_pomodoro()
        elif self.contest_mode == "race":
            self._calculate_race()

    def loop(self, stdscr): 
        key = None
        self.next_filename = self.filename
        while self.next_filename is not None:
            self.filename = self.next_filename
            self.load(stdscr)
            self._reload()
            self.next_filename = None
            with open(self.filename, "at") as outf:
                while key != CTRL_X:
                    self._run_key(outf, key)
                    if outf.closed:
                        key = None
                        break
                    self._run_contests()
                    self._update_status()
                    if self.ui.need_reset:
                        self._reload(outf)
                    key = self.ui.getch(timeout=0.2)

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

def human_duration(seconds, floor=0):
    if seconds is None or seconds == "":
        return "??:??"
    if isinstance(seconds, str):
        if seconds.strip() == "":
            return "??:??"
        else:
            return seconds

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

if __name__ == "__main__":
    ina = IdioticNanowrimoAppender(sys.argv[1:])
    curses.wrapper(ina.loop)

