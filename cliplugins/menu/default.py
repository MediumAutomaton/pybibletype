from cliplugins.library import mastermenu, menutools
import central

class Plugin:
    def __init__(self):
        self.mainMenu = mastermenu.Menu()
        self.selectMenu = mastermenu.Menu()
        self.trackMenu = mastermenu.Menu()
        self.manageMenu = mastermenu.Menu()
        self.settingsMenu = mastermenu.Menu()

        self.initMainMenu()
        self.initSelectMenu()
        self.initTrackMenu()
        self.initManageMenu()
        self.initSettingsMenu()


    def addMainMenuItem(self, name, callback):
        self.mainMenu.addNumberedItem(name, callback=callback)

    def addSelectMenuItem(self, name, data=None):
        self.selectMenu.addNumberedItem(name, data)

    def addTrackMenuItem(self, name, callback):
        self.trackMenu.addNumberedItem(name, callback=callback)

    def addManageMenuItem(self, name, data=None, callback=None):
        self.manageMenu.addNumberedItem(name, data, callback=callback)

    # Registering new settings will probably be handled by the settings plugin
    # def addSettingsMenuItem(self, name, callback):
        # self.settingsMenu.addNumberedItem(name, callback=callback)


    # Main Menu
    def initMainMenu(self):
        self.addMainMenuItem("Select Start Point", self.presentSelectMenu)
        self.addMainMenuItem("Start Writing", central.startcheck.prompt)
        self.addMainMenuItem("Track Progress", self.presentTrackMenu)
        self.addMainMenuItem("Manage Project", self.presentManageMenu)
        self.addMainMenuItem("Settings", self.presentSettingsMenu)

    def presentMainMenu(self):
        while True:
            menutools.clear()
            render = self.mainMenu.render("callback")
            print(render["render"])
            user = menutools.askForNumber("Select a number (Enter to exit program): ", max=self.mainMenu.size())
            if not user:
                if menutools.confirm("Are you sure you want to exit? [y/N]: "):
                    exit()
            else:
                render["mappingDict"][int(user)]()


    def presentSubmenu(self, menu):
        while True:
            menutools.clear()
            render = menu.render("callback")
            print(render["render"])
            user = menutools.askForNumber("Select a number (Enter to cancel): ", max=self.mainMenu.size())
            if not user:
                return
            else:
                render["mappingDict"][int(user)]()


    # Select Menu
    def initSelectMenu(self):
        pass

    def presentSelectMenu(self):
        self.presentSubmenu(self.selectMenu)


    # Track Menu
    def initTrackMenu(self):
        pass

    def presentTrackMenu(self):
        self.presentSubmenu(self.trackMenu)


    # Manage Menu
    def initManageMenu(self):
        pass

    def presentManageMenu(self):
        self.presentSubmenu(self.manageMenu)


    # Settings Menu
    def initSettingsMenu(self):
        pass

    def presentSettingsMenu(self):
        self.initSettingsMenu()
        self.presentSubmenu(self.settingsMenu)