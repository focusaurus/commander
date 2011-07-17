#Note that names "command", "alias", and "logger"
#Will be injected at runtime via commander.py
import shlex
import subprocess
import types
import urllib2

#These helpers are (currently) OS X specific
def browser(args):
    if type(args) not in (types.ListType, types.TupleType):
        args = [args]
    #TODO this only works on OS X. Add linux support
    run(["open"] + args)

def copyText(text):
    popen = subprocess.Popen("pbcopy", stdin=subprocess.PIPE).communicate(text)

def maestro(scriptId):
    """Run a Keyboard Maestro script by ID (more robust) or name"""
    return """osascript -e 'tell application "Keyboard Maestro Engine" to """ \
       """do script "%s"'\n""" % scriptId

def search(url, terms):
    browser(url % quote(terms))
#END of OS X specific stuff

def addProtocol(URL):
    if not URL.lower().startswith("http://"):
        return "http://" + URL
    return URL

def run(args):
    if type(args) in types.StringTypes:
        args = shlex.split(args)
    subprocess.call(args)

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
        return function(shlex.split(args))
    #maintain the same name so @command works properly
    wrapper.__name__ = function.__name__
    return wrapper
