#!/usr/bin/python
"""This is a command line general purpose OS automation triggering mechanism.
"""
from Tkinter import *
import copy
import logging
import logging.handlers
import os
import re
import shlex
import sys

import helpers

EC_UNKNOWN_COMMAND = 11
COMMENT_RE = re.compile("^\s*#")
SITE_CONF_MTIME = -1
SITE_CONF_PATH = os.path.join(os.path.dirname(sys.argv[0]), "sites.conf")
logger = logging.getLogger("commander")

handler = logging.handlers.RotatingFileHandler(
    os.path.expanduser("~/.commander.log"), maxBytes=1024**2, backupCount=5)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

#This is the global map of command names to command functions
commands = {}

reloaders = []
class Reloader(object):
 
    def __init__(self, path, reloadFunction):
        self.path = path
        self.reloadFunction = reloadFunction
        self.mtime = os.stat(self.path).st_mtime

    def reload(self, *args):
        logger.debug("BUGBUG checking mtime of %s" % self.path)
        if (not os.access(self.path, os.R_OK)) or \
                (not os.path.isfile(self.path)):
            return
        newMTime = os.stat(self.path).st_mtime 
        if self.mtime < newMTime:
            self.mtime = newMTime
            self.reloadFunction(*args)


class Application(Frame):
    def createWidgets(self):
        self.prompt = Entry(self, width=100, takefocus=True)
        self.prompt.bind("<Return>", self.run)
        self.prompt.pack({"anchor": "n"})
        self.prompt.focus_set()

        self.QUIT = Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["fg"]   = "red"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack()

    def run(self, *args):
        print "Running", self.prompt.get()
        interpret(self.prompt.get())
        self.quit()

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        



#decorator function to store command functions in commands map
def command(function):
    logger.debug("Adding function %s to commands map %s %s" % \
        (function.__name__, id(commands), commands.keys()))
    commands[function.__name__] = function
    return function

########## Helper Methods ##########
def alias(commandFunc, alias):
    commands[alias] = commandFunc

def siteShower(URLs):
    "Generate a closure function to open a list of URLs in the browser"
    #Note: If you rename this function, rename it inside loadSites as well
    def shower(*terms):
        global SITE_CONF_MTIME
        newMtime = os.stat(SITE_CONF_PATH).st_mtime 
        if newMtime > SITE_CONF_MTIME:
            SITE_CONF_MTIME = newMtime
            loadSites()
        for URL in URLs:
            if URL.count("%s") == 1:
                helpers.search(URL, terms)
            else:
                helpers.browser(URL)
    return shower

def loadCommander(command=""):
    #Main commander.py code has been changed, reload the entire program
    #TODO make rlwrap optional
    logger.info("Reloading commander.py")
    os.execvp("rlwrap", ["rlwrap", sys.argv[0]] + \
        #This makes sure the current command is not dropped, but
        #passed on to the next process via command line
        shlex.split(command))

def loadSites(*args):
    if (not os.access(SITE_CONF_PATH, os.R_OK)) or \
            (not os.path.isfile(SITE_CONF_PATH)):
        return
    logger.info("Reloading %s" % SITE_CONF_PATH)
    #Purge any existing sites
    purged = []
    for kw, func in copy.copy(commands).iteritems():
        if func.__name__ == "shower":
            purged.append(kw)
            del commands[kw]
    logger.debug("Purged site keyword commands: %s" % purged)
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
                    commands[alias] = siteShower(URLs)
            else:
                commands[keyword] = siteShower(URLs)

def loadMyCommands(*args):
    logger.info("loading mycommands")
    if "mycommands" in globals():
        #TODO this does not purge old commands, but it probably should
        reload(mycommands)
    else:
        try:
            logger.debug("Before mycommands we have %s" % commands.keys())
            import mycommands
            logger.debug("After mycommands we have %s" % commands.keys())
            logger.info("Loaded mycommands from: " + mycommands.__file__)
            reloaders.append(Reloader(mycommands.__file__, loadMyCommands))
        except ImportError, info:
            logger.debug("Could not import mycommands module. %s" % info)
    
def interpret(value):
    if not value:
        #Typing CTRL-D at the prompt generates empty string, which means quit
        return quit()
    [reloader.reload(value) for reloader in reloaders]
    value = value.strip()
    if not value:
        #Empty line, reprompt
        return
    try:
        args = shlex.split(value)
    except ValueError:
        args = value.split(" ")
    command = (args[0] or "").lower()
    args = args[1:]
    logger.debug("Looking for command %s in %s" % (command, commands.keys()))
    if command in commands:
        logger.debug("Calling command function %s with args %s" % (command, args))
        commands.get(command)(*args)
    else:
        unknown(command)

def unknown(command):
    message = "Unknown command: %s" % command
    sys.stderr.write(message + "\n")
    logger.debug(message)

########## Command Functions ##########
@command
def quit():
    sys.exit(0)
alias(quit, "q")

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

def main():
    global command
    #Expose our decorator and helpers via the helper module
    #This avoids a circular dependency with mycommands
    helpers.command = command
    helpers.alias = alias
    helpers.logger = logger
    
    reloaders.append(Reloader(sys.argv[0], loadCommander))
    reloaders.append(Reloader(SITE_CONF_PATH, loadSites))
    loadSites()
    loadMyCommands()

    commandLineCommand = " ".join(sys.argv[1:])
    if commandLineCommand:
        interpret(commandLineCommand)
    while True:
        sys.stdout.write("> ")
        command = sys.stdin.readline()
        #BUGBUG#helpers.run("clear")
        interpret(command)

if __name__ == "__main__":
    main()
