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
    run(["open"] + args)

def copyText(text):
    popen = subprocess.Popen("pbcopy", stdin=subprocess.PIPE).communicate(text)

def maestro(scriptId):
    return """osascript -e 'tell application "Keyboard Maestro Engine" to """ \
       """do script "%s"'\n""" % scriptId

def run(args):
    if type(args) in types.StringTypes:
        args = shlex.split(args)
    subprocess.call(args)

def search(url, terms):
    termList = [urlencode(term) for term in terms]
    print termList
    browser(url % tuple(termList))

def urlencode(terms):
    if type(terms) in types.StringTypes:
        terms = [terms.strip()]
    else:
        terms = [term.strip() for term in terms]
    return urllib.quote_plus(" ".join(terms))
