# Default writer startcheck plugin for pybibletype

def startcheck():
    pass

import central
central.mainMenu.register("Start Writing", startcheck)
