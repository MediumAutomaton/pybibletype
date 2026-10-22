# Namespace for some objects shared between files

menu = None
startcheck = None
prompter = None
prompttemplate = None
modifytemplate = None

makeproject = None
maketemplate = None
open = None
writer = None
settings = None



class DummyMainMenu:
    def register(self, name, callback):
        pass

mainMenu = DummyMainMenu()

writer = None