from helpers import run
import logging
import subprocess
import functools
import types

logger = logging.getLogger("commander")


def pbcopy(text):
    """Put a string on the OS clipboard via pbcopy."""
    subprocess.Popen("pbcopy", stdin=subprocess.PIPE).communicate(text)


def pbpaste():
    """Return a string from the OS clipboard via pbpaste."""
    return subprocess.Popen("pbpaste", shell=False,
                            stdout=subprocess.PIPE).stdout.read().strip()


def maestro(scriptId):
    """Run a Keyboard Maestro script by ID (more robust) or name."""
    run("""osascript -e 'tell application "Keyboard Maestro Engine" to """
        """do script "%s"'\n""" % scriptId)


def clipboard(function):
    """
    Create a decorated function taking arguments from the system clipboard.

    This will wrap your command function such that the if the user did not
    provide any command line arguments, the contents of the OS clipboard will
    be used instead.

    If the wrapped function returns something, the return value will be
    copied to the clipboard.

    CAREFUL if combining this decorator with the @command decorator.
    @command must come FIRST in the source code (so it is executed last), and
    the fully-decorated function is stored in the command map."""

    logger.debug("clipboard called with %s", function)

    @functools.wraps(function)
    def wrapper(args):
        logger.debug("clipboard.wrapper called with %s", args)
        if type(args) in types.StringTypes and not args:
            args = pbpaste()
        elif not args[0]:
            args = pbpaste()
        result = function(args)
        if result:
            pbcopy(str(result))
        return result
    return wrapper
