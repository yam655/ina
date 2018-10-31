ina: Idiotic NaNoWroMo Appender
===============================

When a person engages in National Novel Writing Month, they are supposed to put
their inner editor away.

`ina` isn't an editor, so it helps you put your inner editor away. 

`ina` an appender. It has no editing capabilities.

Starting the program
--------------------

`ina` is a text-mode program, and needs to be run from a terminal or terminal
emulator. To get the most out of the program, the window should be at least
20 columns by 3 rows. (This means it should be fully functional on little LCD
displays.)

Less than three rows and you no longer get the status
line. Narrower than about 20 columns and the contest information (for word
wars and races) will no longer be available. (It has been tested and functions
in a 2x2 window, if you're just looking at blind-typing. My terminal emulator
window couldn't get smaller than that.)

`ina` primarily supports an optional file name. Here's the full usage::

    usage: ina [-h] [--user-config DIR] [--one-line] [--generate-config] [file]

    This is an Idiotic NaNoWriMo Appender.

    positional arguments:
      file               Name of target file to append to.

    optional arguments:
      -h, --help         show this help message and exit
      --user-config DIR  Specify an alternate user configuration directory.
      --one-line, -b     Enable one-line mode from the start.
      --generate-config  Create a config file in ~/.config/ina/settings.conf


Key commands
============

^X

    *Exit the program.* The file is always saved. It was saved long before you
    pressed ^X.

^H, ^?, Backspace, Delete

    *Add TODO marker.* There is no deletion. You can add a reminder to edit
    later, but this isn't an editor so you can find no deletion here.

^W

    *Start a Word War.* You will be prompted for how long to do the word war.
    Word wars are treated like a "contest" for the purpose of display.

^T

    *Start a Pomodoro.* This uses the standard 25 minute duration and starts
    immediately. Pomodoros are treated like "contests" for the purpose of
    display.

^P

    *Pause.* Pause your writing session. It also hides your current writing
    incase you are writing in a public place.

^R

    *Start a Word Race.* A word war has a fixed duration, while a word race
    has a fixed target word count.

^B

    *One-line Mode.* This is a special mode for writing in public places.
    This hides all of the text except for the current line.
    This toggles One-Line Mode, so if it is enabled, it will disable it.

Shift-Down

    *Next File.* This looks for the number in your filename and increments
    it. See "Project Support" for details.

Shift-Up

    *Previous File.* This looks for the number in your filename name
    decrements it. See "Project Support" for details.

Shift-Right

    *Outline on Right* This tries to show you a similarly named outline file.
    See "Project Support" for details.

Shift-Left

    *Outline on Left* This tries to show you a similarly named outline file.
    See "Project Support" for details.

Status Line
-----------

The status line is at the top of the window.

There are three sections of information. The left, middle and right.

The left has the session details. When the session is paused, it doesn't
increase the session time. It also has the session word count. If you're in
One-Line Mode, there will be a note about that here.

The right has the total word count for the file.

The middle will have contest details. When a contest is on-going, this details
which type of contest it is and the time will keep updating even if you don't
press any key. After the contest is over the details remain.

Contest modes
-------------

There are two main contest modes right now, "word war", and "word race" mode.
The "pomodoro" mode is currently very much like a "word war" with a fixed time.

A contest displays information in the middle of the status bar up top.
The information available is, time, words, and words-per-minute. Either the
time or the words will count down while the other increases.

To clear the details for a previous contest run, select either a "Word War" or
a "Word Race" and press enter instead of providing a value. It will clear the
central contest details.

To clear the contest data, select a word war or a word race and hit enter or
specify "0". This will clear the contest data without specifying a new contest.
This is needed to see the normal status bar if the window is narrow enough that
the contest data cannot be displayed with the normal status bar.

Project Support
---------------

There is some very crude support for multi-file projects.

There's support for using Shift-Down to go to the next file, and Shift-Up to
go to the previous file. There's some major caveats, though.

If you're writing with one chapter per file, it expects the chapter number to
be the only number in the filename. Whether this is one digit or three doesn't
matter, and it will zero-pad as needed to match what you previously had.

If you're writing with one scene per file, and you use the `<chapter><scene>`
combined numeric identifier, it will only work while in that chapter. It has
no way of incrementing the chapter-part of the number. If you separate the
chapter and scene number with anything and it sees two different numbers
in the filename, it will not do anything at all.

There is support for a file-specific outlines. The expectation is that
the leading part of the filenames will be the same. Ideally, there is an
underscore (`_`) or dash (`-`) separating the group-specific identifier
from the story / outline identifier.

Here's an example::

    ch01-story.txt
    ch01-outline.txt

However, if there are no dashes or underscores, it leans upon the period
as the separator::

    ch01.txt
    ch01.outline

Note that in this case, it ignores both the original extension, as well as the
period itself, so the following also works::

    ch01.txt
    ch01-outline.txt

This is currently designed to work with only two files. Three files and while
the Left-Outline and Right-Outline keys will be consistent, none of them may
be presenting the same information as Control-L. (Control-L will always
refresh the output file.)

Note that switching files will reset the "session time", but will not interrupt
on-going contests.

Screen shots
------------

If you run `./ina.py README.rst`, you will see::

    Session 00:16/0                                      3005 words


    Use ^X to exit. ^W for Word War. ^R for Word Race.
    ^P to Pause Session. ^B for One-Line Mode. ^T for Pomodoro.

    [...]ly, you need to let the soft-wrapping
    do its work.

    Things to remember:

    * There is no editing functionality.
    * It saves as you go.
    * Backspace inserts TODO.

    If you use a light-weight markup format, such as
    reStructuredText, Markdown, or similar, this
    should work well for you.

There are no bright or garish colors to distract you from your work. The status
bar is separated from your text with an empty line.

If you use `^P` to pause, the screen will be cleared and be replaced by
just::

                            Paused.

If you use `^W` to start a word war, you're presented with a dialog::

    Session 00:01/0                                      3132 words
    Word war for how long?

Once you specify a duration, it will switch to contest-mode::

    Session 00:52/9      Word War 01:35/9 22.425 WPM     3141 words

When the contest ends, the screen will flash. You will be left with the
final results::

    Session 01:15/56       00:00/56 56.154 WPM           3399 words

All of the contests function in a very similar fashion.

Are you interested in reducing what folks can see of your screen?
Consider using `^B` for "one-line mode"::

    Session 01:06/9 [One-Line]                        3539 words



    This is what one-line mode looks like... on 60x8



In one-line mode, text is removed from the preceding line as new text is
added. This means that when writing a paragraph, you have a one full line
of text always visible.

Since `ina` is not an editor, and does not keep track of what you type, when
you exit one-line mode you do not suddenly have context on your screen.

The ~/.config/ina/settings.conf file
------------------------------------

The `--generate-config` option will create a default configuration file.

That is currently as follows::

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


Original Example Text
---------------------

This is sample text for the earlier examples. This
was done with hard-returns and a much narrower 
right margin. However, if you want the tail-text
to wrap properly, you need to let the soft-wrapping
do its work.

Things to remember:

* There is no editing functionality.
* It saves as you go.
* Backspace inserts TODO.

If you use a light-weight markup format, such as
reStructuredText, Markdown, or similar, this
should work well for you.

