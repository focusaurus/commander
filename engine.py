import os
import sys


class Engine(object):

    def __init__(self, logger=None):
        print("BUGBUG init an engine")
        #This is the map of command names to command functions
        self._commands = {}
        self._reloaders = []
        self.logger = logger
        self.command(self.help)
        self.command(self.quit)

    def commands(self):
        return self._commands.copy()

    def add(self, function, name):
        self.logger.debug("Adding function %s to commands map %s %s" % \
            (name, id(self._commands), self._commands.keys()))
        self._commands[name] = function
        print("BUGBUG now have", id(self._commands), self._commands)

    def remove(self, name):
        del self._commands[name]

    def addReloader(self, path, hook):
        self._reloaders.append(Reloader(path, hook))

    def command(self, *args, **kwargs):
        """decorator function to store command functions in commands map"""
        alias = kwargs.get("alias")
        invoked = bool(not args or kwargs)
        if invoked:
            def wrapper(function):
                self.add(function, function.__name__)
                if alias:
                    self.add(function, alias)
                return function
            return wrapper
        else:
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
        print(id(self._commands))
        self.logger.debug("Looking for command '%s' in %s" % (command, keys))
        if command in self._commands:
            if args:
                self.logger.debug(
                    "Calling command function %s with args %s" % \
                    (command, args))
                #Do it with args!
                self._commands.get(command)(args)
            else:
                self.logger.debug("Calling command function %s" % command)
                #Do it without args!
                try:
                    self._commands.get(command)('')
                except TypeError:
                    self._commands.get(command)()
        else:
            self.unknown(command)

    def unknown(self, command):
        message = "Unknown command: %s" % command
        sys.stderr.write(message + "\n")
        self.logger.debug(message)

    def help(self):
        keys = self._commands.keys()
        keys.sort()
        print keys

    def quit(self):
        sys.exit(0)


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
