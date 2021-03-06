"""Manage commander commands to open URLs and Apps"""
from future import standard_library

standard_library.install_aliases()
from builtins import input
import copy
from . import helpers
from commander import engine, full_reload, mac
import os
import sys
import json
import types


def full(name):
    return os.path.join(os.path.dirname(sys.argv[0]), name)


PRETTY = {"indent": 2, "sort_keys": True}

OPEN = "open"
if os.uname().sysname == "Linux":
    OPEN = "xdg-open"


def load(open_path, task_name=None, pre_hook=None):
    if not os.path.exists(open_path):
        return

    with open(open_path) as conf:
        try:
            commands = json.load(conf)
        except ValueError:
            sys.stderr.write("Warning: invalid JSON at {}".format(open_path))
            return
    engine.add_reloader(open_path, full_reload)
    [add_command(command, pre_hook) for command in commands]
    if task_name:
        engine.add(prompt_and_save(open_path), task_name)


def add_command(command, pre_hook):
    task = opener(command, pre_hook)
    names = command["name"]
    if type(names) in (str,):
        names = [names]
    [engine.add(task, name) for name in names]


def opener(_command, pre_hook):
    """
    Generate a closure function to open an app with arguments.

    return a closure-powered opener command function

    """

    def open_command(*repl_args):
        command = copy.copy(_command)
        if pre_hook:
            # might want to pass repl_args to the pre_hook
            pre_hook(command)
        to_run = [OPEN]
        app = command.get("app")
        if app:
            if os.uname().sysname == "Linux":
                to_run = [app.lower()]
            else:
                to_run.extend(["-a", app])
        repl_args = [arg for arg in repl_args if arg]
        args = command.get("args", [])
        for arg in args:
            if arg.count("%s") == 1:
                if len(repl_args) == 1:
                    arg = arg % helpers.quote(repl_args)
                else:
                    arg = arg % helpers.quote(helpers.paste())
            if arg.startswith("~"):
                arg = helpers.expand_path(arg)
            to_run.append(arg)
        helpers.background(to_run)

    return open_command


def append(command, open_path):
    with open(open_path, "r+") as conf:
        try:
            commands = json.load(conf)
        except ValueError:
            sys.stderr.write("Warning: invalid JSON at {}".format(open_path))
            return
        commands.append(command)
        conf.seek(0)
        json.dump(commands, conf, **PRETTY)


def prompt_and_save(path):
    def prompt_and_save_inner():
        """commander command function to add a new opener command by name."""
        command = {}
        names = input("Task name: ").split(",")
        command["app"] = input("Application (optional): ")
        command["args"] = input("Arguments (optional): ")

        if len(names) == 1:
            command["name"] = names[0]
        else:
            command["name"] = names
        [command.pop(key) for key, value in list(command.items()) if value is ""]
        if command.get("args"):
            command["args"] = command["args"].split(" ")
        add_command(command, path)
        append(command, path)

    return prompt_and_save_inner
