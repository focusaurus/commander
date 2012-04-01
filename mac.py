from helpers import quote, run
import subprocess
import types


def pbcopy(text):
    subprocess.Popen("pbcopy", stdin=subprocess.PIPE).communicate(text)


def pbpaste():
    return subprocess.Popen("pbpaste", shell=False,
        stdout=subprocess.PIPE).stdout.read().strip()


def maestro(scriptId):
    """Run a Keyboard Maestro script by ID (more robust) or name"""
    run("""osascript -e 'tell application "Keyboard Maestro Engine" to """ \
       """do script "%s"'\n""" % scriptId)


def clipboard(function):
    """Create a decorated function that default to clipboard.

    This will wrap your command function such that the if the user did not
    provide any command line arguments, the contents of the OS clipboard will
    be used instead.

    CAREFUL if combining this decorator with the @command decorator.
    @command must come FIRST in the source code (so it is executed last), and
    the fully-decorated function is stored in the command map."""
    #logger.debug("Functon %s will default to clipboard argument" % \
    #    function.__name__)

    def wrapper(args):
        if not args:
            args = pbpaste()
            #logger.debug(
            #    "Using clipboard as args to %s: %s" %
             #   (function.__name__, args))
        return function(args)
    #maintain the same name so @command works properly
    wrapper.__name__ = function.__name__
    return wrapper
