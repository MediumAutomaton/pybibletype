from cliplugins.library import mastermenu


class Menu:
    def __init__(self):
        self.menu = mastermenu.Menu()
        self.menu.title = "Modules Test"

    def register(self, name, callback):
        self.menu.addNumberedItem(name, callback=callback)

    def prompt(self):
        renderOut = self.menu.render("callback")
        render = renderOut["render"]
        mappingDict = renderOut["mappingDict"]
        print(render)
        user = int(input("Select a number: "))
        mappingDict[user]()
