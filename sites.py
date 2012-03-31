import engine
import helpers
import re
import os
import sys


COMMENT_RE = re.compile("^\s*#")
SITE_CONF_PATH = os.path.join(os.path.dirname(sys.argv[0]), "sites.conf")
logger = engine.logger


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


def loadSites():
    if (not os.access(SITE_CONF_PATH, os.R_OK)) or \
            (not os.path.isfile(SITE_CONF_PATH)):
        return
    #Purge any existing sites
    purged = []
    for kw, func in engine.commands().iteritems():
        if func.__name__ == "opener":
            purged.append(kw)
            engine.remove(kw)
    logger.debug("Purged site keyword commands: %s" % purged)
    logger.info("Reloading %s" % SITE_CONF_PATH)
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
            if keyword.find(","):
                for alias in keyword.split(","):
                    engine.commands[alias] = siteOpener(URLs)
            else:
                engine.add(keyword, siteOpener(URLs))

engine.addReloader(SITE_CONF_PATH, loadSites)


@engine.command
def site(*terms):
    with open(SITE_CONF_PATH, 'a') as outFile:
        outFile.write(" ".join(terms) + "\n")
    loadSites()
