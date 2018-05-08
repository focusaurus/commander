from future import standard_library
standard_library.install_aliases()
import fnmatch
import glob
import functools
import logging
import os
import shlex
import subprocess
import types
import urllib.request, urllib.error, urllib.parse
import webbrowser

logger = logging.getLogger("commander")


OS_IS_LINUX = os.uname().sysname == "Linux"
OS_IS_MAC = os.uname().sysname == "Darwin"
def to_str(input):
    if type(input) == bytes:
        return input.decode()
    return input

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


def _prepare_args(args):
    to_run = []
    for arg in args:
        if type(arg) in (str,):
            to_run.extend(shlex.split(arg))
        else:
            to_run.extend(arg)
    return to_run


def run(*args):
    to_run = _prepare_args(args)
    logger.debug("run: %s" % to_run)
    subprocess.call(to_run)


def background(*args):
    to_run = _prepare_args(args)
    logger.debug("background: %s" % to_run)
    subprocess.Popen(to_run, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)


def script(script_text, interpreter="/bin/sh"):
    subprocess.Popen(interpreter, stdin=subprocess.PIPE).communicate(
        script_text)


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
    terms = to_str(terms)
    if type(terms) == str:
        terms = [terms.strip()]
    if type(terms) in (list, tuple):
        terms = [term.strip() for term in terms]
    return urllib.parse.quote(" ".join(terms))


def split(function):
    """Create a decorated function that will get passed pre-split arguments.

    This will wrap your command function such that the user entered string
    argument will be passed to your function as a list of strings already
    split by shlex.split.

    CAREFUL if combining this decorator with the @command decorator.
    @command must come FIRST in the source code (so it is executed last), and
    the fully-decorated function is stored in the command map."""
    logger.debug("Functon %s will get pre-split arguments" % function.__name__)

    @functools.wraps(function)
    def wrapper(args):
        args = to_str(args)
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
    logger.debug("Functon %s will get spaces instead of newlines" %
                 function.__name__)

    @functools.wraps(function)
    def wrapper(args):
        logger.debug(
            "no newlines in args to %s: %s" % (function.__name__, args))
        return function(args.replace("\n", ""))
    return wrapper


def copy(text):
    """Put a string on the OS clipboard."""
    if type(text) != bytes:
        text = text.encode("utf8")
    command = ["pbcopy"]
    if os.uname().sysname == "Linux":
        command = ["xsel", "-b"]
    subprocess.Popen(command, stdin=subprocess.PIPE).communicate(text)


def paste():
    """Return a string from the OS clipboard."""
    command = ["pbpaste"]
    if os.uname().sysname == "Linux":
        command = ["xclip", "-selection", "clipboard", "-o"]
    return subprocess.Popen(command, shell=False,
                            stdout=subprocess.PIPE).stdout.read().strip()


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
    the fully-decorated function is stored in the command map.

"""

    logger.debug("clipboard called with %s", function)

    @functools.wraps(function)
    def wrapper(args, **kwargs):
        logger.debug("clipboard.wrapper called with %s", args)
        if type(args) in (str,bytes) and not args:
            args = paste()
        elif not args[0]:
            args = paste()
        result = function(args, **kwargs)
        if result:
            copy(str(result))
        return result
    return wrapper
