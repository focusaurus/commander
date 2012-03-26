#Note that names "command", "alias", and "logger"
#Will be injected at runtime via commander.py
import glob
import os
import shlex
import subprocess
import types
import urllib2

#These helpers are (currently) OS X specific


def browser(args):
    if type(args) not in (types.ListType, types.TupleType):
        args = [args]
    #TODO this only works on OS X. Add linux support
    browser = ["open"]
    run(browser + args)


def pbcopy(text):
    subprocess.Popen("pbcopy", stdin=subprocess.PIPE).communicate(text)


def pbpaste():
    return subprocess.Popen("pbpaste", shell=False,
        stdout=subprocess.PIPE).stdout.read().strip()


def expandPath(path):
    return os.path.abspath(os.path.expanduser(path))


def expandGlob(path):
    return glob.glob(expandPath(path))


def maestro(scriptId):
    """Run a Keyboard Maestro script by ID (more robust) or name"""
    run("""osascript -e 'tell application "Keyboard Maestro Engine" to """ \
       """do script "%s"'\n""" % scriptId)


def search(url, terms):
    browser(url % quote(terms))
#END of OS X specific stuff


def addProtocol(URL):
    if URL.find("://") >= 0:
        return URL
    return "http://" + URL


def run(*args):
    toRun = []
    for arg in args:
        if type(arg) in types.StringTypes:
            toRun.extend(shlex.split(arg))
        else:
            toRun.extend(arg)
    logger.debug("run: %s" % toRun)
    subprocess.call(toRun)


def quote(terms):
    if type(terms) in types.StringTypes:
        terms = [terms.strip()]
    else:
        terms = [term.strip() for term in terms]
    return urllib2.quote(" ".join(terms))


def split(function):
    """Create a decorated function that will get passed pre-split arguments.

    This will wrap your command function such that the user entered string
    argument will be passed to your function as a list of strings already
    split by shlex.split.

    CAREFUL if combining this decorator with the @command decorator.
    @command must come FIRST in the source code (so it is executed last), and
    the fully-decorated function is stored in the command map."""
    logger.debug("Functon %s will get pre-split arguments" % \
        function.__name__)

    def wrapper(args):
        logger.debug("Splitting args to %s: %s" % (function.__name__, args))
        return function(*shlex.split(args))
    #maintain the same name so @command works properly
    wrapper.__name__ = function.__name__
    return wrapper

def noNewlines(function):
    """Creat a decorator to convert new lines to spaces.

    This will wrap your command function such that the user entered string
    argument will have any internal newlines converted to spaces.

    CAREFUL if combining this decorator with the @command decorator.
    @command must come FIRST in the source code (so it is executed last), and
    the fully-decorated function is stored in the command map."""
    logger.debug("Functon %s will get spaces instead of newlines" % \
        function.__name__)

    def wrapper(args):
        logger.debug("no newlines in args to %s: %s" % (function.__name__, args))
        return function(args.replace("\n", ""))
    #maintain the same name so @command works properly
    wrapper.__name__ = function.__name__
    return wrapper

def clipboard(function):
    """Create a decorated function that default to clipboard.

    This will wrap your command function such that the if the user did not
    provide any command line arguments, the contents of the OS clipboard will
    be used instead.

    CAREFUL if combining this decorator with the @command decorator.
    @command must come FIRST in the source code (so it is executed last), and
    the fully-decorated function is stored in the command map."""
    logger.debug("Functon %s will default to clipboard argument" % \
        function.__name__)

    def wrapper(args):
        if not args:
            args = pbpaste()
            logger.debug("Using clipboard as args to %s: %s" % (function.__name__, args))
        return function(args)
    #maintain the same name so @command works properly
    wrapper.__name__ = function.__name__
    return wrapper
