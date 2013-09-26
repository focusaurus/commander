import fnmatch
import glob
import functools
import logging
import os
import shlex
import subprocess
import types
import urllib2
import webbrowser

logger = logging.getLogger("commander")


def browser(*args):
    [webbrowser.open_new_tab(add_protocol(arg)) for arg in args]


def expand_path(path):
    return os.path.abspath(os.path.expanduser(path))


def expand_glob(path):
    return glob.glob(expand_path(path))


def deep_glob(directory, pattern):
    directory = expand_path(directory)
    results = []
    for base, dirs, files in os.walk(directory):
        goodfiles = fnmatch.filter(files, pattern)
        results.extend(os.path.join(base, f) for f in goodfiles)
    return results


def add_protocol(URL):
    if URL.find("://") >= 0:
        return URL
    return "http://" + URL


def _prepareArgs(args):
    toRun = []
    for arg in args:
        if type(arg) in types.StringTypes:
            toRun.extend(shlex.split(arg))
        else:
            toRun.extend(arg)
    return toRun


def run(*args):
    toRun = _prepareArgs(args)
    logger.debug("run: %s" % toRun)
    subprocess.call(toRun)


def background(*args):
    toRun = _prepareArgs(args)
    logger.debug("background: %s" % toRun)
    subprocess.Popen(toRun)


def script(script_text, interpreter="/bin/sh"):
    subprocess.Popen(interpreter, stdin=subprocess.PIPE).communicate(script_text)


def clear(command):
    if getattr(command, "clear", True):
        run("clear")


def noclear(function):
    function.clear = False
    return function


def search(url, terms):
    try:
        browser(url % quote(terms))
    except TypeError:
        print("Your URL placeholder is wrong. Fix and retry. %s" % url)


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

    @functools.wraps(function)
    def wrapper(args):
        logger.debug("Splitting args to %s: %s" % (function.__name__, args))
        return function(*shlex.split(args))
    return wrapper


def no_new_lines(function):
    """Create a decorator to convert new lines to spaces.

    This will wrap your command function such that the user entered string
    argument will have any internal newlines converted to spaces.

    CAREFUL if combining this decorator with the @command decorator.
    @command must come FIRST in the source code (so it is executed last), and
    the fully-decorated function is stored in the command map."""
    logger.debug("Functon %s will get spaces instead of newlines" % \
        function.__name__)

    @functools.wraps(function)
    def wrapper(args):
        logger.debug("no newlines in args to %s: %s" % (function.__name__, args))
        return function(args.replace("\n", ""))
    return wrapper
