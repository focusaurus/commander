from builtins import object
import logging
import os
import sys

logger = logging.getLogger("commander")


class Engine(object):

    def __init__(self):
        # This is the map of command names to command functions
        self._commands = {}
        self._reloaders = []
        self._pre_hooks = []
        self._post_hooks = []

    def commands(self):
        return self._commands.copy()

    def add(self, function, name):
        self._commands[name] = function
        logger.debug("engine.add %s engine: %s %s" %
                     (name, id(self), list(self._commands.keys())))

    def remove(self, name):
        del self._commands[name]

    def add_pre_hook(self, hook):
        self._pre_hooks.append(hook)

    def add_post_hook(self, hook):
        self._post_hooks.append(hook)

    def remove_pre_hook(self, hook):
        self._pre_hooks.remove(hook)

    def remove_post_hook(self, hook):
        self._post_hooks.remove(hook)

    def add_reloader(self, path, hook):
        self._reloaders.append(Reloader(path, hook))

    def prompt(self):
        return "> "

    def command(self, *args, **kwargs):
        """decorator function to store command functions in commands map"""
        alias = kwargs.get("alias")
        invoked = bool(not args or kwargs)
        if invoked:
            # Arguments passed to the decorator: @command(alias="foo")
            # Must operate in decorator-factory mode
            def add_with_alias(function):
                self.add(function, function.__name__)
                if alias:
                    for splitAlias in alias.split(","):
                        self.add(function, splitAlias)
                return function
            return add_with_alias
        else:
            # Decorator used directly: @command
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
            # Empty line, reprompt
            return
        args = None
        if " " in value:
            # At least one argument
            command, args = value.split(" ", 1)
        else:
            command = value
        command = command.lower()
        keys = list(self._commands.keys())
        keys.sort()
        logger.debug("Looking for command '%s' in %s" % (command, keys))
        if command in self._commands:
            command_func = self._commands.get(command)
            [hook(command_func) for hook in self._pre_hooks]
            if args:
                logger.debug(
                    "Calling command function %s with args %s" %
                    (command, args))
                # Do it with args!
                command_func(args)
            else:
                logger.debug("Calling command function %s" % command)
                # Do it without args!
                try:
                    command_func('')
                except TypeError:
                    command_func()
            [hook(command_func) for hook in self._post_hooks]
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
        new_mtime = os.stat(self.path).st_mtime
        if self.mtime < new_mtime:
            self.mtime = new_mtime
            return True
        return False
