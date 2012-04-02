import sys
from commander import engine


@engine.command(alias="?")
def help():
    keys = engine.commands().keys()
    keys.sort()
    print keys


@engine.command(alias="q")
def quit():
    sys.exit(0)
