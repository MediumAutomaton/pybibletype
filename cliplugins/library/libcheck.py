# A plugin can request a library plugin and this will either provide it
# or inform the user that they need it.
# This should be present.

from os.path import exists
from importlib import import_module

def checkFor(*libs):
    for lib in libs:
        if exists("cliplugins.library." + lib):
            return import_module("cliplugins.library." + lib)
        else:
            print("Required library plugin '" + lib + "' is missing! Please add it and try again.")
            exit()
