# Commander: Command Line Utility for Hackers and Poets

This little utility gives you quick keyword-driven access to frequently used
URLs, programs, scripts, etc.  You can extend it to do more or less anything, 
but out of the box it's good for

* Opening one or more browser URLs (bookmarks)
* quick web based searches
* running programs and scripts
* miscellaneous system automation

# Snurtle: When a python crawls into your shell

This program can be run in several different ways, but I'll tell you about the OMG-good way first.

Unix shells are great (I prefer zsh). They give us the awesome in the form of:

* good tab completion (zsh shines here)
* great command line editing, even for long, wrapped lines
* searchable command history
* command history substitution

However, shell scripts pale in comparison to more modern scripting languages like Python or Ruby when you have to do anything non-trivial or not made trivial by existing posix utilities. I want all that interactive goodness the shell provides plus a decent programming language. There's a way to make this possible that is fairly clean and low-maintenance: `command_not_found_handler`.

`command_not_found_handler` function is a hook that zsh or bash (bash calls it `command_not_found_handle` though) will call whenever you type in something that doesn't match a target operation (a binary in your PATH, a builtin command, an alias, a function, etc). Ever seen an Ubuntu box tell you something like "The program 'cowsay' is currently not installed.  The program '%s' can be found in the following packages...". That's the [command-not-found](http://bazaar.launchpad.net/~command-not-found-developers/command-not-found/trunk/files) package using this hook to make that happen.

So what does this mean? I can now write a python function that will be directly available to me in my shell as soon as I save my `.py` file. In here I can do whatever awesome python fanciness I want.

To integrate with a shell, 
#Supported OS
* Currently this is tested only on OS X but it should work fine on linux (at 
  least eventually once I get around to testing it and making minor tweaks)
* It uses an (optional but suggested) external [rlwrap](https://trac.macports.org/browser/trunk/dports/sysutils/rlwrap/Portfile) (Readline Wrap) program for history and line
editing. `rlwrap` must be in your `PATH` environment varible

#Getting started

* clone this git repo
* cd into the working directory
    * `cd commander`
* Copy sites_sample.conf to sites.conf and edit it
    * `cp sites_sample.conf sites.conf`
    * `$EDITOR sites.conf`
* read `sites_sample.conf` for documentation on its syntax
* Fire up commander (optionally preceeded by `rlwrap` for history and line editing)
    * rlwrap python commander.py

Once started, Commander will automatically reload as needed when files are
updated, so don't worry about it.  You can use a new site added to `sites.conf`
right away.

#Built in commands
* quit
    * quits commander.py
* site
    * add a new site to sites.conf
    * `site example http://site.example`
* gui
    * A primitive TK gui I built for this.  Probably better to just run it
    in Terminal.app or gnome-terminal or whatever

#Adding your own commands
* Copy `mycommands_sample.py` to `mycommands.py` and edit it
* Read the comments in `mycommands_sample.py` for tips

## Keyboard Maestro

I wrote this as a complement to the excellent
[Keyboard Maestro](http://www.keyboardmaestro.com/). I use Keyboard Maestro 
for lots of UI automation including assinging my most-used apps to the function
keys on my macbook and text abbreviations.  I highly recommend it.  However,
Keyboard Maestro does not seem to have the notion of triggering actions by
global keystroke followed by typing a keyword/phrase then enter.  This is more along
the lines of other automation utilities like
[LaunchBar](http://www.obdev.at/products/launchbar/index.html).
You may also want to check out [Alfred](http://www.alfredapp.com/)
or [Quicksilver](http://qsapp.com/). However, I've never been into "adaptive"
automation and I like the simplicity and concreteness of knowing I'm tying into
a dumb static script that is going to do the same thing every time until I
change the code to do something else. That said, those commercial apps have
bells and whistles out the wazoo, so if you need iCal integration graphical
previews of your PDF files, have a look at them.

##My Workflow

I map Command-Space to a Keyboard Maestro action that actives Terminal.app,
positions the window at the top right corner, and resizes it to a small narrow
strip.  In this window I keep the commander.py prompt running in a loop.  Thus
to access any functionality I want from commander.py, I type Command-Space
followed by the command such as "unmount", which is a little script that
unmounts all my external disks so I can pack up my macbook. I can do this
globally no matter where my keyboard focus is at the moment, and the UI is
instantaneous.

# License

## Commander is licensed under the MIT License
Copyright (c) 2011 Peter Lyons

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
