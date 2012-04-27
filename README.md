# Commander: Command Line Utility for Hackers and Poets

Commander is a task-automation utility. The basic idea is:

* You write functions to do useful things in python
* You decorate them with the `@command` decorator commander provides
* You can now trigger your functions from the command line by name
* You don't need to write boilerplate code and wrapper scripts
* You can directly integrate your python commander functions into your interactive shell (!)

Commander designed to run in one of several modes:

1. As a standalone interactive REPL where you directly type commands
1. Integrated into your existing shell. Your commander functions are available directly in your shell as if they were shell functions.
1. As a build tool similar to [Make](http://en.wikipedia.org/wiki/List_of_build_automation_software), [Rake](http://rake.rubyforge.org/), or [Shovel](https://github.com/seomoz/shovel)

#What can I do with it?

Your commander functions can do just about anything since they are written in python. Out of the box, commander provides helpers to make the following things trivial.

* Opening one or more browser URLs (bookmarks)
* quick web based searches
* running programs and scripts
* miscellaneous system automation
* Integrate with [Keyboard Maestro](http://www.keyboardmaestro.com/main/) on OS X for automation that is challenging from python such as manipulating windows, simulating mouse clicks, and so on

Here are some ideas to seed your mind with commander functions you may want to write.

* Tweet something
* Search for something on google, wikipedia, youtube, or any site or search engine
* quickly check weather, stocks, sports scores, etc from the command line
* quickly append notes to a journal file with a timestamp
* add an item to your to-do list
* see the last few git commit messages in a particular repository
* perform an advanced renaming operation on all files under the current directory
* perform a smart search/replace across a set of files
* whatever else you feel would be useful to do from a command prompt
* Anything that works better in python than as a shell script

# Installation

Commander works will as a [git submodule](http://book.git-scm.com/5_submodules.html) under your [dotfiles](http://blog.smalleycreative.com/tutorials/using-git-and-github-to-manage-your-dotfiles/) repository. Set it up like this.


    cd ~/dotfiles
    git submodule add git@github.com:focusaurus/commander.git commander
    cp -a commander/commander_sample.py commander.py

Then edit your `commander.py` script. Read the samples there to get then hang of it. Once you see how it works, feel free to delete the sample command functions defined there.

#Running Commander in single-command mode

By default, commander will start up, interpret the command given on the command line, then exit. This mode is good for:

1. built tool automation a la Make/Rake/Shovel
1. invoking commander from a non-interactive shell script
1. Learning commander
1. Developing commander functions

.

    ./commander.py kablammo

This would run your custom-defined "kablammo" function then exit.

#Running an interactive REPL

Commander can also run as a continuous interactive read-eval-print-loop.

    ./commander.py --repl
    > kablammo
    >

This would start the interactive prompt, run your custom-defined `kablammo` function, then prompt for the next command. Type CTRL-D, "quit", or "q" to quit and return back to your shell.

This mode is good for:

1. Keeping available in an easily-accessible shell tab
1. Typing commands without worrying about shell quoting and globbing rules

## Making the REPL better with rlwrap

The external "readline wrap" `rlwrap` utility is highly recommended to add more sophisticated command line editing, history, etc to commander.

* `apt-get install rlwrap` on Ubuntu/Debian
* `brew install rlwrap` on OS X with [Homebrew](http://mxcl.github.com/homebrew/)
* `yum install rlwrap` on RPM+yum based linux distros (untested)

Then launch your repl like this:

    rlwrap ./commander.py --repl

You can now use the up arrow or CTRL-p to go back in your command history, etc.

##Automatic reloading

In repl mode, commander will watch the mtime on the code and configuration files and automatically reload itself when they change. If you add a new command to commander.py while a repl is already running, you can immediately use it in the repl. Same thing applies to `sites.conf`. You can use the `commander.engine.addReloader` function to watch additional files to trigger reloads.


#Integrating commander into your regular shell
## (Or: Complete Shell Nirvana)

Here's the mode that will allow you to seamlessly integrate commander commands into your normal interactive [bash](http://tldp.org/LDP/abs/html/bashver4.html) or [zsh](http://www.zsh.org/). Once you get this set up, my hope is you'll take advantage of the power of python and write more and more of your sophisticated functionality as a commander function instead of a shell function. In this mode you get the best of both worlds of your shell and python.

* All the normal shell features you love
* Ability to define simple shell alias and functions in the shell as always
* Ability to use environment variables (with tab completion, too)
* Awesome tab completion
* Awesome command editing
* Awesome command history and history manipulation
* filename globbing and pattern expantion
* Commander integration
  * Specifically your commander commands get all that good stuff, too: tab completion of environment variables, history searching, shell globbing, etc

Source the `commander.sh` script from your shell's configuration file (`~/.bashrc` or `~/.zshrc`) like this:

    [ -f ~/dotfiles/commander/commander.sh ] && source ~/dotfiles/commander/commander.sh

Now you can turn on commander shell integration by typing `commander on`

So what does this mean? It means now in your shell when you type a command your shell will look for that command as:

* a shell built-in command
* an alias or function
* an executable file or script on your `PATH`
* a commander function

To turn off commander integration with your shell type `commander off`.

To start commander in repl mode, type `commander repl`. This is good for a dedicated commander window and avoids having to deal with shell quoting and globbing rules.


For now, it is recommended that a new python process be started each time. This makes it easy to do interactive things like prompting for a password securely using the `getpass` module and so forth. However, commander can also read its input from a file via the `--in` command line argument. Thus it is possible for the shell to create a [fifo](http://www.gnu.org/software/libc/manual/html_node/FIFO-Special-Files.html), start a single long-running commander python process, and then feed it commands one at a time via the fifo. This avoids any startup/shutdown overhead and makes it easier for your commands to keep state in memory across multiple commands. However, it is not possible to interact with the tty in this mode, so you can't prompt the user for input (at least I haven't found a clean way yet). On most modern systems, the python startup is fast enough to be negligible, so single-command mode is probably sufficient. However, it's on my todo list to figure out a good way to do a background process IPC version.

To start commander shell integration in fifo mode, type `commander fifo`. Turn it off with `commander off`.

Note that if shell filename globbing is sometimes screwing with your commander arguments when you don't want it to, prefix your command with `noglob` to disable shell globbing for that single command.

    noglob mycommand_that_needs_a_regex  f?art


##More info on command_not_found_handler

`command_not_found_handler` function is a hook that zsh or bash (bash calls it `command_not_found_handle` though) will call whenever you type in something that doesn't match a target operation (a shell builtin command, an alias, a function, a binary in your PATH, etc). Ever seen an Ubuntu box tell you something like "The program 'cowsay' is currently not installed.  The program 'cowsay can be found in the following packages...". That's the [command-not-found](http://bazaar.launchpad.net/~command-not-found-developers/command-not-found/trunk/files) package using this hook to make that happen.

#Built-in support for opening web sites

Commander includes a `sites` module which gives you shortcuts to launch or search web sites from the command line. Your mapping of command trigger to URL is stored in a `sites.conf` configuration file. To set up the `sites` module:


* Copy sites_sample.conf to sites.conf and edit it
    * `cp commander/sites_sample.conf commander/sites.conf`
    * `$EDITOR sites.conf`
* read `sites_sample.conf` for documentation on its syntax


Now you can be hacking away in your shell, type `gh` (for example) and have [https://github.com]() open in a new browser tab. Passing in search terms via the query string is also supported by including a `%s` in the URL where the search terms go.

To add a new site to the configuration file, use the `site` commander command, so just type "site zefrank http://www.zefrank.com/" and it will be added to the configuration file and immediately available.

Note that `sites.conf` supports aliases as the site keywords as well as multiple URLs opened in browser tabs. This is handy for projects. For example, if you have a project "zippio" and you always need your docs, development server, art repo, and github repo open in browser tabs, you can make a site called "zippio" that will open all of those pages in tabs.


#Built in commands
* quit (also CTRL-D or just "q")
    * quits commander.py
* help (also "?")
    * Print a basic help message and a list of loaded commands

#Supported Environments

* Python 2.7 (probably 2.6 will also work)
* OS X (10.7, 10.6, probably the rest of them)
* Linux

#Using Commander over the network

It is pretty straightforward to use the basic unix utilities of fifos and netcat to make commander work across the network. Note this is entirely cleartext and insecure. Also, netcat will only handle one connection at a time.

* Create a [fifo](http://www.gnu.org/software/libc/manual/html_node/FIFO-Special-Files.html) for commander to use
  * `mkfifo ~/.commander.fifo`
* Start commander reading commands from that fifo
  * `./commander.py --in ~/.commander.fifo --out ~/.commander.fifo --repl`
* Start a local netcat daemon, sending its output to commander's fifo
  * `nc -k -l 1234 > ~/.commander.fifo`
* On a remote machine, use netcat as your commander shell
  * nc host.where.you.started.commander.and.netcat.example 1234
* Type your commander commands into that nc prompt and they will execute on the remote machine


# Keyboard Maestro

I wrote this as a complement to the excellent [Keyboard Maestro](http://www.keyboardmaestro.com/). I use Keyboard Maestro for lots of UI automation including assinging my most-used apps to the function keys on my macbook and text abbreviations.  I highly recommend it.  However, Keyboard Maestro does not seem to have the notion of triggering actions by global keystroke followed by typing a keyword/phrase then enter.  This is more along the lines of other automation utilities like [Spotlight](http://en.wikipedia.org/wiki/Spotlight_(software)) or [LaunchBar](http://www.obdev.at/products/launchbar/index.html).
You may also want to check out [Alfred](http://www.alfredapp.com/) or [Quicksilver](http://qsapp.com/). However, I've never been into "adaptive" automation and I like the simplicity and concreteness of knowing I'm typing into a dumb static script that is going to do the same thing every time until I
change the code to do something else. That said, those commercial apps have
bells and whistles out the wazoo, so if you need iCal integration graphical previews of your PDF files, have a look at them.

##My Workflow

I map Command-Space to a Keyboard Maestro macro that actives Terminal.app, positions the window at the top left corner, and resizes it to a small narrow strip.  In this window I keep the commander.py prompt running in the repl.  Thus to access any functionality I want from commander.py, I type Command-Space followed by the command such as "unmount", which is a little script that unmounts all my external disks so I can pack up my macbook. I can do this globally no matter where my keyboard focus is at the moment, and the UI is instantaneous.

# License

## Commander is licensed under the MIT License
Copyright (c) 2011 Peter Lyons

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
