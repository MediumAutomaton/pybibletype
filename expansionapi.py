class TrackerAPI:
    pass

class ExpansionAPI:
    def __init__(self,
                 menu,
                 writePrompter,
                 settings
                 ):
        self.menu = menu;
        self.writePrompter = writePrompter;
        self.settings = settings;

    def addMainMenuItem(self, name, callback):
        self.menu.addMainMenuItem(name, callback)

    def addSelectMenuItem(self, name, data=None):
        self.menu.addSelectMenuItem(name, data)

    def addTrackMenuItem(self, name, callback):
        self.menu.addTrackMenuItem(name, callback)

    def addManageMenuItem(self, name, data=None, callback=None):
        self.menu.addManageMenuItem(name, data, callback)