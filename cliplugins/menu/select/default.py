# Default start point selection menu plugin for pybibletype

from os import listdir as osListdir

from cliplugins.library import mastermenu, menutools

class Plugin:
    def __init__(self):
        self.mainMenu = mastermenu.Menu()
        self.mainMenu.title = "BibleType Project Selection"
        self.projectItem = self.mainMenu.addNumberedItem("Project", callback=self.selectProject)
        self.bookItem = self.mainMenu.addNumberedItem("Book", callback=self.selectBook)
        self.chapterItem = self.mainMenu.addNumberedItem("Chapter", self.chapterNumber, self.selectChapter)
        self.verseItem = self.mainMenu.addNumberedItem("Verse", self.verseNumber, self.selectVerse)

    def registerReader(self, displayName, importName):
        pass

    def useReader(self, importName):
        pass

    def selectProject(self):
        fileMenu = mastermenu.Menu()
        fileMenu.title = "Available Projects"
        [fileMenu.addNumberedItem(file[:-5]) for file in osListdir() if file[-5:] == ".json"]
        renderOut = fileMenu.render("name")
        print(renderOut["render"])

        num = menutools.askForNumber("Select # of project (Enter to cancel): ")
        if not num:
            return
        self.projectFileName = renderOut["mappingDict"][num] + ".json"
        try:
            with open(self.projectFileName, "r") as f:
                self.project = json.load(f)
        except Exception as x:
            print("Can't open that project.")
            self.debug(x)
        self.book = None
        self.chapterNumber = "None"
        self.verseNumber = "None"

    def present(self):
        pass # Return a reader for the selected project
