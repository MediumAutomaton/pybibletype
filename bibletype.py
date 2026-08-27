# Launcher for plugin-based BibleType
version = "3.0-0"

from os import chdir as osChdir
osChdir("projects")

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-d", "--debug", help="Enable extra debug messages", action="store_true")
parser.add_argument("-v", "--version", help="Show version then exit", action="store_true")
parser.add_argument("-p", "--defaultplugins", help="Just use all the default plugins", action="store_true")
args = parser.parse_args()

if args.version:
    print("pybibletype version " + version)
    exit()

if not args.defaultplugins:
    print("Please use --defaultplugins for now, the plugin manager isn't ready yet.")
    exit()


from cliplugins.library import debug
debug.enabled = args.debug

import cliplugins.menu.main.default
