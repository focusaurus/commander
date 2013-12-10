#!/usr/bin/env python
"""Command line general purpose OS automation triggering mechanism.
"""
import argparse
import functools
import logging
import logging.handlers
import os
import re
import subprocess
import sys

import engine as _engine
#Import our useful submoduls so user scripts get everything they need
import helpers
import mac

logger = logging.getLogger("commander")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fileHandler = logging.handlers.RotatingFileHandler(
    os.path.expanduser("~/.commander.log"),
    maxBytes=1024 ** 2, backupCount=5)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


pyc = functools.partial(re.compile("\.pyc$", re.I).sub, ".py")

"This is the shared global engine instance that holds the state"
engine = _engine.Engine()


def command(*args, **kwargs):
    return engine.command(*args, **kwargs)


def fullReload(command=""):
    """Restart the Commander python process, preserving arguments"""
    currentArgs = vars(parseArgs())
    newArgs = []
    for arg in ["in", "out"]:
        fileName = currentArgs[arg].name
        if fileName and fileName != "<std%s>" % arg:
            newArgs.extend(["--" + arg, fileName])
    if currentArgs["repl"]:
        newArgs.append("--repl")
    #This makes sure the current command is not dropped, but
    #passed on to the next process via command line
    newArgs.append(command)
    newArgs.insert(0, sys.argv[0])
    sys.stdout.flush()
    sys.stderr.flush()
    logger.debug(
        "Commander reloading with args: %s %s" %
            (sys.argv[0], " ".join(newArgs)))
    if wrapped():
        os.execvp("rlwrap", ["rlwrap"] + newArgs)
    else:
        os.execvp(sys.argv[0], newArgs)


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
    parser.add_argument('--repl', action='store_true',
        help='start a read-eval-print-loop interactive commander session')
    parser.add_argument("command", nargs="*")
    return parser.parse_args()


def main(args=sys.argv):
    engine.addReloader(pyc(args[0]), fullReload)
    engine.addReloader(pyc(__file__), fullReload)
    #Load up the various submodules
    import builtins
    engine.addReloader(pyc(builtins.__file__), fullReload)
    import sites
    engine.addReloader(pyc(sites.__file__), fullReload)
    import apps
    engine.addReloader(pyc(apps.__file__), fullReload)
    args = parseArgs(args)
    inFile = vars(args)["in"]
    commandLineCommand = " ".join(args.command)
    if commandLineCommand:
        engine.interpret(commandLineCommand)
    if not args.repl:
        sys.exit(0)
    while True:
        if inFile.isatty():
            args.out.write(engine.prompt())
        try:
            command = inFile.readline()
            if not command:
                #Typing CTRL-D at the prompt generates empty string,
                #which means quit
                sys.exit(0)
            engine.interpret(command)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()

__all__ = ["builtins", "engine", "gui", "helpers", "mac", "sites", "apps"]
