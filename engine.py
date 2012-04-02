import logging
import os
import sys

logger = logging.getLogger("commander")


class Engine(object):

    def __init__(self):
        #This is the map of command names to command functions
        self._commands = {}
        self._reloaders = []
        self._preHooks = []
        self._postHooks = []

    def commands(self):
        return self._commands.copy()

    def add(self, function, name):
        self._commands[name] = function
        logger.debug("engine.add %s engine: %s %s" % \
            (name, id(self), self._commands.keys()))

    def remove(self, name):
        del self._commands[name]

    def addPreHook(self, hook):
        self._preHooks.append(hook)

    def addPostHook(self, hook):
        self._postHooks.append(hook)

    def removePreHook(self, hook):
        self._preHooks.remove(hook)

    def removePostHook(self, hook):
        self._postHooks.remove(hook)

    def addReloader(self, path, hook):
        self._reloaders.append(Reloader(path, hook))

    def command(self, *args, **kwargs):
        """decorator function to store command functions in commands map"""
        alias = kwargs.get("alias")
        invoked = bool(not args or kwargs)
        if invoked:
            #Arguments passed to the decorator: @command(alias="foo")
            #Must operate in decorator-factory mode
            def addWithAlias(function):
                self.add(function, function.__name__)
                if alias:
                    self.add(function, alias)
                return function
            return addWithAlias
        else:
            #Decorator used directly: @command
            function = args[0]
            self.add(function, function.__name__)
            return function

    def interpret(self, value):
        for reloader in self._reloaders:
            if reloader.check():
                # This will exit the process and re-execute
                reloader.hook(value)
        value = value.strip()
        if not value:
            #Empty line, reprompt
            return
        args = None
        if " " in value:
            #At least one argument
            command, args = value.split(" ", 1)
        else:
            command = value
        command = command.lower()
        keys = self._commands.keys()
        keys.sort()
        logger.debug("Looking for command '%s' in %s" % (command, keys))
        if command in self._commands:
            [hook(command) for hook in self._preHooks]
            if args:
                logger.debug(
                    "Calling command function %s with args %s" % \
                    (command, args))
                #Do it with args!
                self._commands.get(command)(args)
            else:
                logger.debug("Calling command function %s" % command)
                #Do it without args!
                try:
                    self._commands.get(command)('')
                except TypeError:
                    self._commands.get(command)()
            [hook(command) for hook in self._postHooks]
        else:
            self.unknown(command)

    def unknown(self, command):
        message = "Unknown command: %s" % command
        sys.stderr.write(message + "\n")
        logger.debug(message)


class Reloader(object):
    """Check whether a file has been modified since the last check"""

    def __init__(self, path, hook):
        self.path = path
        self.mtime = os.stat(self.path).st_mtime
        self.hook = hook

    def check(self, *args):
        if (not os.access(self.path, os.R_OK)) or \
                (not os.path.isfile(self.path)):
            return False
        newMTime = os.stat(self.path).st_mtime
        if self.mtime < newMTime:
            self.mtime = newMTime
            return True
        return False
