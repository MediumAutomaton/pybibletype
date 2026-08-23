# Default CLI main menu plugin for pybibletype

from cliplugins.library import mastermenu, menutools

menu = mastermenu.Menu()
menu.title = "BibleType"

def register(name, callback):
    menu.addNumberedItem(name, callback)

def present():
    while True:
        menutools.clear()
        renderOut = menu.render("callback")
        print(renderOut["render"])
        user = menutools.askForNumber("Select a number (Enter to exit program): ")
        if not user:
            if menutools.confirm("Are you sure you want to exit?"):
                exit()
        else:
            if user < 1 or user > menu.size():
                menutools.pause("Number must be between 1 and 5")
            else:
                renderOut["mappingDict"][int(user)]()
