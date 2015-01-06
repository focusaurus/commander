"""Manage commander commands to open URLs and Apps"""
import helpers
from commander import engine
import os
import sys
import json
import types

MAIN = "open.json"
LOCAL = "open_local.json"
pretty = {
    "indent": 2,
    "sort_keys": True
}

def path(name):
    return os.path.join(os.path.dirname(sys.argv[0]), name)


def load(open_path):
    if not os.path.exists(open_path):
        return

    with open(open_path) as conf:
        try:
            commands = json.load(conf)
        except ValueError:
            sys.stderr.write("Warning: invalid JSON at {}".format(open_path))
            return
    engine.addReloader(open_path, load)
    [add_command(command) for command in commands]


def add_command(command):
    task = opener(command)
    names = command["name"]
    if type(names) in types.StringTypes:
        names = [names]
    [engine.add(task, name) for name in names]


def opener(command):
    """
    Generate a closure function to open an app with arguments.

    return a closure-powered opener command function

    """
    def open_command(*repl_args):
        to_run = ["open"]
        if "app" in command:
            to_run.extend(["-a", command["app"]])
        for arg in command.get("args", []):
            if arg.count("%s") == 1:
                arg = arg % helpers.quote(repl_args)
            if arg.startswith("~"):
                arg = helpers.expand_path(arg)
            to_run.append(arg)
        print(to_run)  # @bug
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
        json.dump(commands, conf, **pretty)


@engine.command(alias="open")
@helpers.split
def _open(*ignore):
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
    append(command, path(MAIN))

for name in [MAIN, LOCAL]:
    load(path(name))
