#Note that names "command", "alias", and "logger"
#Will be injected at runtime via commander.py
import shlex
import subprocess
import types
import urllib

def addProtocol(URL):
    if not URL.lower().startswith("http"):
        return "http://" + URL
    return URL

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

def run(args):
    if type(args) in types.StringTypes:
        args = shlex.split(args)
    subprocess.call(args)

def search(url, terms):
    browser(url % urlencode(terms)) 

def urlencode(terms):
    if type(terms) in types.StringTypes:
        terms = [terms.strip()]
    else:
        terms = [term.strip() for term in terms]
    return urllib.quote_plus(" ".join(terms))
