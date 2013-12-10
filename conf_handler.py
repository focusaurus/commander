import logging
import os
import re
import sys

from commander import engine


COMMENT_RE = re.compile("^\s*#")
logger = logging.getLogger("commander")


class ConfHandler:

    def __init__(self, name, make_task):
        self.name = name
        self.conf_path = os.path.join(
            os.path.dirname(sys.argv[0]), "%s.conf" % self.name)
        self.make_task = make_task
        if self.conf_exists():
            engine.addReloader(self.conf_path, self.load)
            self.load()

    def conf_exists(self):
        return os.access(self.conf_path, os.R_OK) and \
            os.path.isfile(self.conf_path)

    def load(self, *ignore):
        if (not self.conf_exists()):
            return
        #Purge any existing sites
        purged = []
        for kw, func in engine.commands().iteritems():
            if func.__name__ == self.name:
                purged.append(kw)
                engine.remove(kw)
        logger.debug("purged ConfHandler commands: %s" % purged)
        logger.debug("ConfHandler loading %s" % self.conf_path)
        with open(self.conf_path) as inFile:
            for line in inFile:
                if not line.strip():
                    continue
                if COMMENT_RE.match(line):
                    continue
                tokens = line.split()
                if len(tokens) < 2:
                    continue
                keyword = tokens[0]
                args = tokens[1:]
                for alias in keyword.split(","):
                    logger.debug("Adding conf_handler function with alias '%s' for args '%s'" % (alias, args))
                    engine.add(self.make_task(args), alias)
    def add(self, *terms):
        with open(self.conf_path, 'a') as outFile:
            outFile.write(" ".join(terms) + "\n")
        self.load()
