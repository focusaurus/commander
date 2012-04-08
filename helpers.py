import fnmatch
import glob
import logging
import os
import shlex
import subprocess
import types
import urllib2
import webbrowser

logger = logging.getLogger("commander")


def browser(*args):
    [webbrowser.open_new_tab(addProtocol(arg)) for arg in args]


def expandPath(path):
    return os.path.abspath(os.path.expanduser(path))


def expandGlob(path):
    return glob.glob(expandPath(path))


def deepGlob(directory, pattern):
    directory = expandPath(directory)
    results = []
    for base, dirs, files in os.walk(directory):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results


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


def clear(*args, **kwargs):
    run("clear")


def search(url, terms):
    browser(url % quote(terms))


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
