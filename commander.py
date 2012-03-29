#!/usr/bin/env python
"""This is a command line general purpose OS automation triggering mechanism.
"""
from Tkinter import *
import argparse
import logging
import logging.handlers
import os
import re
import subprocess
import sys

import helpers

EC_UNKNOWN_COMMAND = 11
COMMENT_RE = re.compile("^\s*#")
SITE_CONF_PATH = os.path.join(os.path.dirname(sys.argv[0]), "sites.conf")
logger = logging.getLogger("commander")

handler = logging.handlers.RotatingFileHandler(
    os.path.expanduser("~/.commander.log"), maxBytes=1024 ** 2, backupCount=5)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

#This is the global map of command names to command functions
commands = {}
reloaders = []


class Reloader(object):
    """Check whether a file has been modified since the last check"""

    def __init__(self, path):
        self.path = path
        self.mtime = os.stat(self.path).st_mtime

    def check(self, *args):
        if (not os.access(self.path, os.R_OK)) or \
                (not os.path.isfile(self.path)):
            return False
        newMTime = os.stat(self.path).st_mtime
        if self.mtime < newMTime:
            self.mtime = newMTime
            return True
        return False


class Application(Frame):
    def createWidgets(self):
        self.input = StringVar()
        self.prompt = Entry(self, width=100, takefocus=True,
                textvariable=self.input)
        self.prompt.bind("<Return>", self.run)
        self.prompt.pack({"anchor": "n"})
        self.prompt.focus_set()

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit

        self.QUIT.pack()

    def run(self, *args):
        interpret(self.input.get())
        self.input.set("")
        #self.quit()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()


def add(function, name):
    logger.debug("Adding function %s to commands map %s %s" % \
        (name, id(commands), commands.keys()))
    commands[name] = function


def command(*args, **kwargs):
    """decorator function to store command functions in commands map"""
    alias = kwargs.get("alias")
    invoked = bool(not args or kwargs)
    if invoked:
        def wrapper(function):
            add(function, function.__name__)
            if alias:
                add(function, alias)
            return function
        return wrapper
    else:
        function = args[0]
        add(function, function.__name__)
        return function

########## Helper Methods ##########


def siteOpener(URLs):
    "Generate a closure function to open a list of URLs in the browser"
    #Note: If you rename this function, rename it inside loadSites as well
    def opener(*terms):
        for URL in URLs:
            if URL.count("%s") == 1:
                helpers.search(URL, terms)
            else:
                helpers.browser(URL)
    return opener


def loadSites(*args):
    if (not os.access(SITE_CONF_PATH, os.R_OK)) or \
            (not os.path.isfile(SITE_CONF_PATH)):
        return
    #Purge any existing sites
    purged = []
    for kw, func in commands.copy().iteritems():
        if func.__name__ == "opener":
            purged.append(kw)
            del commands[kw]
    logger.debug("Purged site keyword commands: %s" % purged)
    logger.info("Reloading %s" % SITE_CONF_PATH)
    with open(SITE_CONF_PATH) as inFile:
        for line in inFile:
            if not line.strip():
                continue
            if COMMENT_RE.match(line):
                continue
            tokens = line.split()
            if len(tokens) < 2:
                continue
            keyword = tokens[0]
            URLs = tokens[1:]
            if keyword.find(","):
                for alias in keyword.split(","):
                    commands[alias] = siteOpener(URLs)
            else:
                commands[keyword] = siteOpener(URLs)


def loadMyCommands(*args):
    logger.info("loading mycommands")
    try:
        logger.debug("Before mycommands we have %s" % commands.keys())
        import mycommands
        logger.debug("After mycommands we have %s" % commands.keys())
        path = mycommands.__file__
        logger.info("Loaded mycommands from: " + path)
        if path.endswith("pyc"):
            path = path[0:-1]  # Watch the .py file for change, not the .pyc
        reloaders.append(Reloader(path))
    except ImportError, info:
        logger.error("Could not import mycommands module. %s" % info)


def fullReload(command=""):
    logger.info("Reloading commander.py")
    #This makes sure the current command is not dropped, but
    #passed on to the next process via command line
    args = [sys.argv[0], command]
    sys.stdout.flush()
    sys.stderr.flush()
    if wrapped():
        os.execvp("rlwrap", ["rlwrap"] + args)
    else:
        os.execvp(sys.argv[0], args)


def interpret(value):
    if not value:
        #Typing CTRL-D at the prompt generates empty string, which means quit
        return quit()
    for reloader in reloaders:
        if reloader.check():
            fullReload(value)  # This will exit the process and re-execute
    value = value.strip()
    if not value:
        #Empty line, reprompt
        return
    args = None
    if " " in value:
        #At least one argument
        command, args = value.split(" ", 1)
    else:
        command = value
    command = command.lower()
    keys = commands.keys()
    keys.sort()
    logger.debug("Looking for command '%s' in %s" % (command, keys))
    if command in commands:
        if args:
            logger.debug("Calling command function %s with args %s" % \
                (command, args))
            #Do it with args!
            commands.get(command)(args)
        else:
            logger.debug("Calling command function %s" % command)
            #Do it without args!
            try:
                commands.get(command)('')
            except TypeError:
                commands.get(command)()
    else:
        unknown(command)


def unknown(command):
    message = "Unknown command: %s" % command
    sys.stderr.write(message + "\n")
    logger.debug(message)


def wrapped():
    output = subprocess.Popen(
            ["ps", "-p", str(os.getppid()), "-o", "command"],
            stdout=subprocess.PIPE).communicate()[0]
    return output.count("rlwrap") > 0

########## Command Functions ##########


@command
def help():
    keys = commands.keys()
    keys.sort()
    print keys


@command(alias="q")
def quit():
    sys.exit(0)


@command
def help():
    keys = commands.keys()
    keys.sort()
    print keys


@command
def gui():
    root = Tk()
    root.title("Commander")
    app = Application(master=root)
    app.mainloop()
    root.destroy()


@command
def site(*terms):
    with open(SITE_CONF_PATH, 'a') as outFile:
        outFile.write(" ".join(terms) + "\n")
    loadSites()


def parseArgs(args=sys.argv):
    parser = argparse.ArgumentParser(description="Command Line Bliss")
    parser.add_argument('--in', metavar='F', type=argparse.FileType("r+"),
        default=sys.stdin, nargs="?", help='file (FIFO usually) for integrating with shells')
    parser.add_argument('--out', metavar='F', type=argparse.FileType("w"),
        default=sys.stdout, nargs="?", help='file (FIFO usually) for integrating with shells')
    parser.add_argument("command", nargs="*")
    return parser.parse_args()


def main():
    global command
    #Expose our decorator and helpers via the helper module
    #This avoids a circular dependency with mycommands
    helpers.command = command
    helpers.logger = logger

    reloaders.append(Reloader(sys.argv[0]))
    reloaders.append(Reloader(SITE_CONF_PATH))
    loadSites()
    loadMyCommands()
    args = parseArgs()
    inFile = vars(args)["in"]
    tty = inFile.isatty()
    commandLineCommand = " ".join(args.command)
    if commandLineCommand:
        interpret(commandLineCommand)
    while True:
        if tty:
            args.out.write("> ")
        command = inFile.readline()
        if tty:
            helpers.run("clear")
        interpret(command)

if __name__ == "__main__":
    main()
