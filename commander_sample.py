#!/usr/bin/env python
import os

import commander
#Import the @command decorator
from commander import command

#The helpers submodule has a bunch of handy utilities
#Read commander/helpers.py for details on all of them
from commander.helpers import browser, run


########## These are samples. Study, then delete at will. ##########
##### START SAFE TO EDIT/DELETE SECTION #####


#Use the @command decorator to mark a function as a command line command
#The function name is what you type at the prompt to execute it
@command
def directions(*terms):
    query = " ".join(terms)
    start, dest = query.lower().split("to", 1)
    url = "http://maps.google.com/maps?f=d&source=s_d&saddr=%s&daddr=%s"
    #Use browser or other functions from helpers.py as needed
    browser(url % (start.strip(), dest.strip()))

#Pass in an alias keyword argument to have an alternate name for the same
#command function
#I usually make the function name the full name for clarity and
#use an alias if I want a shortcut
@command(alias="um")
def unmount(*terms):
    vols = "/Volumes"
    for name in os.listdir(vols):
        if name == "Macintosh HD":
            continue
        path = os.path.join(vols, name)
        if os.path.isdir(path):
            run(["diskutil", "unmount", path])


@command
def te():
    #helpers.run is a convenient way to run command line stuff
    #It can take a string or a list of string arguments
    run("open -a Textedit")


@command
def calc():
    run("open -a Calculator")

##### END SAFE TO EDIT/DELETE SECTION #####

#Call commander.main() to start a read-eval-print-loop prompt
commander.main()
