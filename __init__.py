#!/usr/bin/env python
"""Command line general purpose OS automation triggering mechanism.
"""
import argparse
import logging
import logging.handlers
import os
import subprocess
import sys

import engine as _engine

logger = logging.getLogger("commander")
handler = logging.handlers.RotatingFileHandler(
    os.path.expanduser("~/.commander.log"),
    maxBytes=1024 ** 2, backupCount=5)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)

"This is the shared global engine instance that holds the state"
engine = _engine.Engine()


def command(*args, **kwargs):
    engine.command(*args, **kwargs)


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


def wrapped():
    output = subprocess.Popen(
            ["ps", "-p", str(os.getppid()), "-o", "command"],
            stdout=subprocess.PIPE).communicate()[0]
    return output.count("rlwrap") > 0


def parseArgs(args=sys.argv):
    parser = argparse.ArgumentParser(description="Command Line Bliss")
    parser.add_argument('--in', metavar='F', type=argparse.FileType("r+"),
        default=sys.stdin, nargs="?",
        help='file (FIFO usually) for integrating with shells')
    parser.add_argument('--out', metavar='F', type=argparse.FileType("w"),
        default=sys.stdout, nargs="?",
        help='file (FIFO usually) for integrating with shells')
    parser.add_argument("command", nargs="*")
    return parser.parse_args()


def main(args=sys.argv):
    engine.addReloader(args[0].replace(".pyc", ".py"), fullReload)
    engine.addReloader(__file__.replace(".pyc", ".py"), fullReload)
    #Load up the various submodules
    import builtins
    engine.addReloader(builtins.__file__.replace(".pyc", ".py"), fullReload)
    import sites
    engine.addReloader(sites.__file__.replace(".pyc", ".py"), fullReload)
    #loadMyCommands()
    args = parseArgs(args)
    inFile = vars(args)["in"]
    tty = inFile.isatty()
    commandLineCommand = " ".join(args.command)
    if commandLineCommand:
        engine.interpret(commandLineCommand)
    while True:
        if tty:
            args.out.write("> ")
        command = inFile.readline()
        if not command:
            #Typing CTRL-D at the prompt generates empty string,
            #which means quit
            sys.exit(0)
        if tty:
            #subprocess.call("clear")
            pass
        engine.interpret(command)

if __name__ == "__main__":
    main()

__all__ = ["builtins", "engine", "gui", "helpers", "mac", "sites"]
