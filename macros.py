"""Manage commander commands to run Keyboard Maestro macros by name."""
import conf_handler
from commander import engine
from commander.mac import maestro


def macro_runner(macro_name):
    """
    Generate a closure function to run a named Keyboard Maestro macro on OSX.

    return a closure-powered macro command function

    """
    #Note: this function name must match the ConfHandler instance name below
    def macro(*ignore):
        maestro(" ".join(macro_name))
    return macro


macro_handler = conf_handler.ConfHandler("macro", macro_runner)


@engine.command
def macro(*tokens):
    """commander command function to add a new macro command by macro name."""
    macro_handler.add(*tokens)
