import helpers
import conf_handler
from commander import engine
from commander.mac import maestro

def macro_runner(macro_name):
    "Generate a closure function to open a named application on OSX"
    #Note: this function name must match the ConfHandler instance name below
    def macros(*ignore):
        maestro(" ".join(macro_name))
    return macros


macro_handler = conf_handler.ConfHandler("macros", macro_runner)


@engine.command
def macro(*tokens):
    macro_handler.add(*tokens)
