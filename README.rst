ina: Idiotic NaNoWroMo Appender
===============================

When a person engages in National Novel Writing Month, they are supposed to put
their inner editor away.

`ina` isn't an editor, so it helps you put your editor away. 

`ina` an appender. It has no editing capabilities.

Starting the program
--------------------

`ina` is a text-mode program, and needs to be run from a terminal or terminal
emulator. You run it with the name of the file to edit.

It does not currently have any arguments.

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
    This toggles One-Line Mode, so if it is enabled, it will disble it.


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



When the text wraps, the line is cleared. When you hit enter or return, the
line is cleared.

Since `ina` is not an editor, and does not keep track of what you type, when
you exit one-line mode you do not suddenly have context on your screen.

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



