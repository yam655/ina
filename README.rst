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

    _Exit the program._ The file is always saved. It was saved long before you
    pressed ^X.

^H, ^?, Backspace, Delete

    _Add TODO marker._ There is no deletion. You can add a reminder to edit
    later, but this isn't an editor so you can find no deletion here.

^W

    _Start a Word War._ You will be prompted for how long to do the word war.
    Word wars are treated like a "contest" for the purpose of display.

^T

    _Start a Pomodoro._ This uses the standard 25 minute duration and starts
    immediately. Pomodoros are treated like "contests" for the purpose of
    display.

^P

    _Pause._ Pause your writing session. It also hides your current writing
    incase you are writing in a public place.

^R

    _Start a Word Race._ A word war has a fixed duration, while a word race
    has a fixed target word count.

^B

    _Blind Mode._ This is a special mode for writing in public places.
    This hides all of the text except for the current line.
    As this toggles Blind mode, so if it is enabled, it will disble it.


Status Line
-----------

The status line is at the top of the window.

There are three sections of information. The left, middle and right.

The left has the session details. When the session is paused, it doesn't
increase the session time. It also has the session word count. If you're in
Blind Mode, there will be a note about that here.

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


