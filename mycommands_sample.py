#!/usr/bin/python
import os
#Use the helpers.py module for some utility functions
#The most important one being the @command decorator
from helpers import alias, browser, command, run

#Use the @command decorator to mark a function as a command line command
#The function name is what you type at the prompt to execute it
@command
def directions(*terms):
    query = " ".join(terms)
    start, dest = query.lower().split("to", 1)
    url = "http://maps.google.com/maps?f=d&source=s_d&saddr=%s&daddr=%s"
    #Use browser or other functions from helpers.py as needed
    browser(url % (start.strip(), dest.strip()))
#Use helpers.alias to have several names for the same function (abbreviations)
alias(directions, "d")

@command
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
