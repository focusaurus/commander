#!/usr/bin/python
from Tkinter import *
import copy
import helpers
import logging
import logging.handlers
import os
import re
import shlex
import sys

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
    def shower():
        global SITE_CONF_MTIME
        newMtime = os.stat(SITE_CONF_PATH).st_mtime 
        if newMtime > SITE_CONF_MTIME:
            SITE_CONF_MTIME = newMtime
            loadSites()
        [helpers.browser(URL) for URL in URLs]
    return shower

def loadSites():
    if (not os.access(SITE_CONF_PATH, os.R_OK)) or \
            (not os.path.isfile(SITE_CONF_PATH)):
        return
    #Purge any existing sites
    for kw, func in copy.copy(commands).iteritems():
        if func.__name__ == "shower":
            logger.debug("purging kw %s" % kw)
            del commands[kw]
    kwSites = {}
    with open(SITE_CONF_PATH) as inFile:
        for line in inFile:
            if not line.strip():
                continue
            if COMMENT_RE.match(line):
                continue
            tokens = line.split()
            if len(tokens) < 2:
                continue
            commands[tokens[0]] = siteShower(tokens[1:])

def interpret(value):
    if not value:
        #Typing CTRL-D at the prompt generates empty string, which means quit
        return quit()
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

def main():
    loadSites()
    global command
    #Expose our decorator and helpers via the helper module
    #This avoids a circular dependency with mycommands
    helpers.command = command
    helpers.alias = alias
    helpers.logger = logger
    try:
        logger.debug("Before mycommands we have %s" % commands.keys())
        import mycommands
        logger.debug("After mycommands we have %s" % commands.keys())
        logger.info("Loaded mycommands")
    except ImportError, info:
        logger.debug("Could not import mycommands module. %s" % info)

    commandLineCommand = " ".join(sys.argv[1:])
    if commandLineCommand:
        interpret(commandLineCommand)
    thisProg = sys.argv[0]
    modified = os.stat(thisProg).st_mtime
    while True:
        sys.stdout.write("> ")
        command = sys.stdin.readline()
        if os.stat(thisProg).st_mtime > modified:
               #Code has been changed, reload
               os.execvp("rlwrap", ["rlwrap", thisProg] + shlex.split(command))
        helpers.run("clear")
        interpret(command)

if __name__ == "__main__":
    main()
