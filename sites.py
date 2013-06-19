import helpers
import logging
import os
import re
import sys

from commander import engine


COMMENT_RE = re.compile("^\s*#")
SITE_CONF_PATH = os.path.join(os.path.dirname(sys.argv[0]), "sites.conf")
logger = logging.getLogger("commander")


def haveFile(path):
    return os.access(path, os.R_OK) and os.path.isfile(path)


def siteOpener(URLs):
    "Generate a closure function to open a list of URLs in the browser"
    #Note: If you rename this function, rename it inside loadSites as well
    def opener(*terms):
        for URL in URLs:
            if URL.count("%s") == 1:
                helpers.search(URL, terms)
            else:
                helpers.browser(URL)
    return opener


def loadSites(*ignore):
    if (not haveFile(SITE_CONF_PATH)):
        return
    #Purge any existing sites
    purged = []
    for kw, func in engine.commands().iteritems():
        if func.__name__ == "opener":
            purged.append(kw)
            engine.remove(kw)
    logger.debug("purged site keyword commands: %s" % purged)
    logger.debug("loading %s" % SITE_CONF_PATH)
    with open(SITE_CONF_PATH) as inFile:
        for line in inFile:
            if not line.strip():
                continue
            if COMMENT_RE.match(line):
                continue
            tokens = line.split()
            if len(tokens) < 2:
                continue
            keyword = tokens[0]
            URLs = tokens[1:]
            for alias in keyword.split(","):
                #logger.debug("Adding site opener function with alias '%s' for URLs '%s'" % (alias, URLs))
                engine.add(siteOpener(URLs), alias)


@engine.command
def site(*terms):
    with open(SITE_CONF_PATH, 'a') as outFile:
        outFile.write(" ".join(terms) + "\n")
    loadSites()

if haveFile(SITE_CONF_PATH):
    engine.addReloader(SITE_CONF_PATH, loadSites)
    loadSites()
