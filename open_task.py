"""Manage commander commands to open URLs and Apps"""
import helpers
from commander import engine, full_reload
import os
import sys
import json
import types


def full(name):
    return os.path.join(os.path.dirname(sys.argv[0]), name)

PRETTY = {
    "indent": 2,
    "sort_keys": True
}

# I didn't actually, y'know, test this on linux yet
OPEN = "open"
if os.uname()[0] == "Linux":
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
    if type(names) in types.StringTypes:
        names = [names]
    [engine.add(task, name) for name in names]


def opener(command, pre_hook):
    """
    Generate a closure function to open an app with arguments.

    return a closure-powered opener command function

    """
    def open_command(*repl_args):
        if pre_hook:
            pre_hook(command)
        to_run = [OPEN]
        if "app" in command:
            to_run.extend(["-a", command["app"]])
        for arg in command.get("args", []):
            if arg.count("%s") == 1:
                arg = arg % helpers.quote(repl_args)
            if arg.startswith("~"):
                arg = helpers.expand_path(arg)
            to_run.append(arg)
        helpers.run(to_run)
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
        names = raw_input("Task name: ").split(",")
        command["app"] = raw_input("Application (optional): ")
        command["args"] = raw_input("Arguments (optional): ")

        if len(names) == 1:
            command["name"] = names[0]
        else:
            command["name"] = names
        [command.pop(key) for key, value in command.items() if value is ""]
        if command.get("args"):
            command["args"] = command["args"].split(" ")
        add_command(command)
        append(command, path)
    return prompt_and_save
