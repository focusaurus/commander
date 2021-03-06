#!/usr/bin/env python
from future import standard_library

standard_library.install_aliases()
import json

commands = []
with open("sites.conf") as sites:
    for line in sites.readlines():
        line = line.strip()
        names, args = line.split(" ", 1)
        names = names.split(",")
        command = {"args": args.split(" ")}
        if len(names) == 1:
            command["name"] = names[0]
        else:
            command["name"] = names
        commands.append(command)

print(json.dumps(commands, sort_keys=True, indent=2))
