from __future__ import print_function
from __future__ import absolute_import
import sys
from commander import engine
from .helpers import noclear


@engine.command(alias="?")
@noclear
def help():
    commands = engine.commands()
    keys = commands.keys()
    keys.sort()
    print('Commander. CTRL-D or "quit" to quit. Available commands: ')
    for key in keys:
        func = commands[key]
        label = key
        words = [key]
        if key is not func.__name__:
            words.extend([" (alias of ", func.__name__, ")"])
        if func.__doc__:
            words.extend([" ", func.__doc__])
        print("".join(words))


@engine.command(alias="q")
def quit():
    sys.exit(0)
