#!/usr/bin/env python
"""Command line general purpose OS automation triggering mechanism."""
import argparse
import functools
import logging
import logging.handlers
import os
import re
import subprocess
import sys

import engine as _engine
# Import our useful submoduls so user scripts get everything they need
import helpers
import mac

logger = logging.getLogger("commander")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.handlers.RotatingFileHandler(
    os.path.expanduser("~/.commander.log"),
    maxBytes=1024 ** 2, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)
# logger.setLevel(logging.DEBUG)


pyc = functools.partial(re.compile("\.pyc$", re.I).sub, ".py")

"This is the shared global engine instance that holds the state"
engine = _engine.Engine()


def command(*args, **kwargs):
    return engine.command(*args, **kwargs)


def opener(file="open.json", task_name=None, pre_hook=None):
    import open_task
    engine.add_reloader(pyc(open_task.__file__), full_reload)
    task_name = task_name or os.path.splitext(os.path.basename(file))[0]
    open_task.load(file, task_name, pre_hook)


def full_reload(command=""):
    """Restart the Commander python process, preserving arguments."""
    current_args = vars(parse_args())
    new_args = []
    for arg in ["in", "out"]:
        fileName = current_args[arg].name
        if fileName and fileName != "<std%s>" % arg:
            new_args.extend(["--" + arg, fileName])
    if current_args["repl"]:
        new_args.append("--repl")
    # This makes sure the current command is not dropped, but
    # passed on to the next process via command line
    new_args.append(command)
    new_args.insert(0, sys.argv[0])
    sys.stdout.flush()
    sys.stderr.flush()
    logger.debug(
        "Commander reloading with args: %s %s" %
        (sys.argv[0], " ".join(new_args)))
    if wrapped():
        os.execvp("rlwrap", ["rlwrap"] + new_args)
    else:
        os.execvp(sys.argv[0], new_args)


def wrapped():
    output = subprocess.Popen(
        ["ps", "-p", str(os.getppid()), "-o", "command"],
        stdout=subprocess.PIPE).communicate()[0]
    return output.count("rlwrap") > 0


def parse_args(args=sys.argv):
    parser = argparse.ArgumentParser(description="Command Line Bliss")
    parser.add_argument(
        '--in',
        metavar='F',
        type=argparse.FileType("r+"),
        default=sys.stdin, nargs="?",
        help='file (FIFO usually) for integrating with shells')
    parser.add_argument(
        '--out',
        metavar='F',
        type=argparse.FileType("w"),
        default=sys.stdout, nargs="?",
        help='file (FIFO usually) for integrating with shells')
    parser.add_argument(
        '--repl',
        action='store_true',
        help='start a read-eval-print-loop interactive commander session')
    parser.add_argument("command", nargs="*")
    return parser.parse_args()


def main(args=sys.argv):
    engine.add_reloader(pyc(args[0]), full_reload)
    engine.add_reloader(pyc(__file__), full_reload)
    # Load up the various submodules
    import builtins
    engine.add_reloader(pyc(builtins.__file__), full_reload)
    import sites
    engine.add_reloader(pyc(sites.__file__), full_reload)
    import apps
    engine.add_reloader(pyc(apps.__file__), full_reload)
    import macros
    engine.add_reloader(pyc(macros.__file__), full_reload)
    args = parse_args(args)
    in_file = vars(args)["in"]
    command_line_command = " ".join(args.command)
    if command_line_command:
        engine.interpret(command_line_command)
    if not args.repl:
        sys.exit(0)
    while True:
        if in_file.isatty():
            args.out.write(engine.prompt())
        try:
            command = in_file.readline()
            if not command:
                # Typing CTRL-D at the prompt generates empty string,
                # which means quit
                sys.exit(0)
            engine.interpret(command)
        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main()

__all__ = [
    "apps",
    "builtins",
    "command",
    "engine",
    "gui",
    "helpers",
    "mac",
    "macros",
    "main",
    "opener",
    "sites"
]
