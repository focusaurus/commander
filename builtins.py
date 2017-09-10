import sys
from commander import engine
from helpers import noclear


@engine.command(alias="?")
@noclear
def help():
    commands = engine.commands()
    keys = commands.keys()
    keys.sort()
    print 'Commander. CTRL-D or "quit" to quit. Available commands: '
    for key in keys:
        func = commands[key]
        label = key
        words = [key]
        if key is not func.func_name:
            words.extend([" (alias of ", func.func_name, ")"])
        if func.func_doc:
            words.extend([" ", func.func_doc])
        print("".join(words))


@engine.command(alias="q")
def quit():
    sys.exit(0)
