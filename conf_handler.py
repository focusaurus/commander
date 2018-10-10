"""Base class for plain text configuration file driven commander commands."""
from builtins import object
import logging
import os
import re
import sys

from commander import engine


COMMENT_RE = re.compile("^\s*#")
logger = logging.getLogger("commander")


class ConfHandler(object):

    """Base class mapping a text configuration file to macro functions."""

    def __init__(self, name, make_task):
        self.name = name
        self.conf_path = os.path.join(
            os.path.dirname(sys.argv[0]), "%ss.conf" % self.name
        )
        self.make_task = make_task
        if self.conf_exists():
            engine.add_reloader(self.conf_path, self.load)
            self.load()

    def conf_exists(self):
        """return true if the configuration file for this handler exists."""
        return os.access(self.conf_path, os.R_OK) and os.path.isfile(self.conf_path)

    def load(self, *ignore):
        """Load the configuration file and activate the commands."""
        if not self.conf_exists():
            return
        # Purge any existing sites
        purged = []
        for kw, func in engine.commands().items():
            if func.__name__ == self.name + "_task":
                purged.append(kw)
                engine.remove(kw)
        logger.debug("purged ConfHandler commands: %s" % purged)
        logger.debug("ConfHandler loading %s" % self.conf_path)
        with open(self.conf_path) as in_file:
            for line in in_file:
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
                    message = (
                        "Adding conf_handler function with alias '%s'"
                        + " for args '%s'"
                    )
                    logger.debug(message % (alias, args))
                    engine.add(self.make_task(args), alias)

    def add(self, *terms):
        """add a new command to the configuration file and reload"""
        with open(self.conf_path, "a") as outFile:
            outFile.write(" ".join(terms) + "\n")
        self.load()
