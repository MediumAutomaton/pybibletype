version = "2.3-1"

import os
import json
import time
from argparse import ArgumentParser

import mastermenu
from bargraph import BargraphRenderer

class BibleType:
    def __init__(self, startPoint, showDebug):
        self.projectFileName = None
        self.project = None
        self.bookName = None
        self.book = None
        self.chapterNumber = None
        self.chapter = None
        self.verseNumber = startPoint["verseNumber"]
        self.filename = None
        self.showDebug = showDebug
        self.bgRenderer = BargraphRenderer()
        self.config = {
            "wpm":False,
            "nopercent":False,
            "promptForExport":True,
            "clearForMenus":True,
            "clrComm":"clear",
        }
        self.configLongNames = {
            "wpm":"Measure WPM",
            "nopercent":"Hide percents at ends of bargraphs",
            "promptForExport":"Ask about exporting progress report to file",
            "clearForMenus":"Clear screen before drawing menus",
            "clrComm":"Host program used to clear the screen",
        }
        if startPoint["projectFileName"]:
            self.changeToProjectsDir()
            if self.loadProject(startPoint["projectFileName"]):
                self.projectFileName = startPoint["projectFileName"]
                self.bookName = startPoint["bookName"]
                if self.bookName:
                    for book in self.project["books"]:
                        if book["name"] == startPoint["bookName"]:
                            self.book = book
                self.chapterNumber = startPoint["chapterNumber"]
                if self.chapterNumber:
                    self.chapter = self.book["chapters"][startPoint["chapterNumber"]-1]



    def debug(self, msg):
        if self.showDebug:
            print(msg)

    def clear(self):
        if self.config["clearForMenus"]:
            os.system(self.config["clrComm"])

    def pause(self, msg):
        print(msg)
        input("Press Enter to continue...")

    def askForNumber(self, prompt, min=1, max=None):
        while True:
            user = input(prompt)
            if not user:
                return ""
            try:
                user = int(user)
                if user < min or (max and user > max):
                    if max:
                        self.pause("Number must be between " + str(min) + " and " + str(max))
                    else:
                        self.pause("Number must be greater than " + str(min))
                else:
                    return user
            except:
                self.pause("Please enter a number.")
        
    def changeToProjectsDir(self):
        if os.getcwd()[-8:] != "projects":
            try:
                os.chdir("projects")
            except:
                print("Where's the 'projects' directory? It should be right next to me.")
                input("Press Enter to exit the program...")
                exit()


    def selectionMenu(self):
        menu = mastermenu.Menu("BibleType Project Selection")
        projectItem = menu.addNumberedItem("Project", callback=self.selectProject)
        bookItem = menu.addNumberedItem("Book", callback=self.selectBook)
        chapterItem = menu.addNumberedItem("Chapter", callback=self.selectChapter)
        verseItem = menu.addNumberedItem("Verse", callback=self.selectVerse)

        while True:
            projectItem.data = self.project["name"] if self.project else "None"
            bookItem.data = self.book["name"] if self.book else "None"            
            chapterItem.data = self.chapterNumber if self.chapterNumber else "None"
            verseItem.data = self.verseNumber if self.verseNumber else "None"
            
            renderOut = menu.render("callback")
            self.clear()
            print(renderOut["render"])
            user = self.askForNumber("Select a number (Enter to save and go back): ", max=menu.size())
            if not user:
                break
            renderOut["mappingDict"][user]()


    def loadProject(self, projectFileName):
        try:
            with open(projectFileName, "r") as f:
                project = json.load(f)
                self.project = project
            return True
        except Exception as x:
            print("Can't open that project.")
            self.debug(x)
            return False

    def selectProject(self):
        self.changeToProjectsDir()
            
        fileMenu = mastermenu.Menu("Available Project Files")
        [fileMenu.addNumberedItem(file[:-5]) for file in os.listdir() if file[-5:] == ".json"]
        renderOut = fileMenu.render("name")
        print(renderOut["render"])

        num = self.askForNumber("Select # of project (Enter to cancel): ", max=fileMenu.size())
        if not num:
            return
        name = renderOut["mappingDict"][num] + ".json"
        if self.loadProject(name):
            self.projectFileName = name
            self.book = None
            self.chapterNumber = None
            self.verseNumber = None


    def selectBook(self):
        if not self.project:
            self.pause("Select a project first!")
            return
        bookMenu = mastermenu.Menu("Books")
        [bookMenu.addNumberedItem(book["name"]) for book in self.project["books"]]
        renderOut = bookMenu.render("name")
        print(renderOut["render"])
        user = self.askForNumber("Select # of book (Enter to cancel): ", max=bookMenu.size())
        if not user:
            return
        self.book = self.project["books"][user-1]
        self.bookName = renderOut["mappingDict"][user]
            

    def selectChapter(self):
        if not self.book:
            self.pause("Select a book first!")
            return
        numChapters = len(self.book["chapters"])
        print("This book has " + str(numChapters) + " chapters")
        user = self.askForNumber("Select a chapter (Enter to cancel): ", max=numChapters)
        if not user:
            return
        self.chapterNumber = user
        self.chapter = self.book["chapters"][user-1]

    def selectVerse(self):
        if not self.chapter:
            self.pause("Select a chapter first!")
            return
        numVerses = len(self.chapter)
        print("This chapter has " + str(numVerses) + " verses")
        user = self.askForNumber("Select a verse (Enter to cancel): ", max=numVerses)
        if not user:
            return
        self.verseNumber = user


    def write(self):
        if not (self.project and self.bookName and self.chapterNumber and self.verseNumber):
            self.pause("Select a start point with 'btselect' first!")
            return
        if self.verseNumber > len(self.chapter):
            self.pause("You're at the end of a chapter! Please select a new start point with 'btselect' first.")
            return
        if self.config["wpm"]:
            startChapterNumber = self.chapterNumber
            startVerseNumber = self.verseNumber
            print("Will calculate WPM when you're done, and will account for time lost to saving and 'Next chapter?' prompts.")
        
        display = mastermenu.Menu("Starting Location")
        display.addUnnumberedItem("Project", self.project["name"])
        display.addUnnumberedItem("Book", self.book["name"])
        display.addUnnumberedItem("Chapter", self.chapterNumber)
        display.addUnnumberedItem("Verse", self.verseNumber)
        
        verseContents = self.chapter[self.verseNumber-1]
        if not verseContents:
            verseContents = "Empty"
        display.addUnnumberedItem("Verse Contents", verseContents)

        self.clear()
        print(display.render()["render"])
        if not input("Good to start here? [y/n]: ").lower() in ["y", "yes"]:
            return
        
        print("Type '!exit' at any point to exit.")
        if self.config["wpm"]:
            startTime = time.time()
            lostTime = 0
        while self.chapterNumber <= len(self.book["chapters"]):
            self.chapter = self.book["chapters"][self.chapterNumber-1]
            while self.verseNumber <= len(self.chapter):
                verseContents = None
                while not verseContents:
                    try:
                        verseContents = input("[" + str(self.verseNumber) + "]: ")
                    except KeyboardInterrupt:
                        print()
                if verseContents == "!exit":
                    print("Exiting. Saving your work to disk...")
                    time1 = time.time()
                    self.saveToDisk()
                    if self.config["wpm"]:
                        lostTime += time.time() - time1
                        self.calculateWPM(startChapterNumber, startVerseNumber, startTime, lostTime)
                    return
                elif verseContents == "!amend":
                    self.verseNumber -= 1
                else:
                    self.chapter[self.verseNumber-1] = verseContents
                    self.verseNumber += 1
            print("Reached end of chapter. Saving your work to disk...")
            time1 = time.time()
            self.saveToDisk()
            if self.chapterNumber < len(self.book["chapters"]):
                if input("Continue to the next chapter? [y/n]: ").lower() in ["y", "yes"]:
                    self.chapterNumber += 1
                    self.verseNumber = 1
                else:
                    if self.config["wpm"]:
                        lostTime += time.time() - time1
                        self.calculateWPM(startChapterNumber, startVerseNumber, startTime, lostTime)
                    return
            else:
                self.pause("Reached end of book. Please use 'btselect' to select another one.")
                if self.config["wpm"]:
                    self.calculateWPM(startChapterNumber, startVerseNumber, startTime, lostTime)
                return
            

    def calculateWPM(self, startChapterNumber, startVerseNumber, startTime, lostTime):
        endTime = time.time()
        if self.verseNumber > len(self.chapter):
            self.verseNumber = len(self.chapter)
        endChapterNumber = self.chapterNumber
        endVerseNumber = self.verseNumber

        firstChapter = True
        charsTyped = 0
        for chapterNumber in range(startChapterNumber, endChapterNumber+1):
            if firstChapter:
                startVerse = startVerseNumber
                firstChapter = False
            else:
                startVerse = 1
            self.chapter = self.book["chapters"][chapterNumber-1]
            if chapterNumber == endChapterNumber:
                lastVerse = endVerseNumber
            else:
                lastVerse = len(self.chapter)
            for verseNumber in range(startVerse, lastVerse+1):
                # Add one for Enter press between verse prompts
                charsTyped += len(self.chapter[verseNumber-1]) + 1
                
        minutes = ((endTime - startTime) - lostTime) / 60
        words = charsTyped / 5
        print("Typed " + str(words) + " words in " + str(minutes) + " minutes, or " + str(words/minutes) + " WPM.")
        return
    

    def saveToDisk(self):
        # Full Save to Memory (just in case)
        self.book["chapters"][self.chapterNumber-1] = self.chapter
        for idx, book in enumerate(self.project["books"]):
            if book["name"] == self.book["name"]:
                self.project["books"][idx] = self.book
                break

        self.changeToProjectsDir()

        # Back up
        try:
            # On Windows, os.rename() will not overwrite an existing file
            os.remove(self.projectFileName + ".backup")
        except:
            pass

        try:
            os.rename(self.projectFileName, self.projectFileName + ".backup")
        except Exception as x:
            self.debug(x)
            if not input("Failed to back up old version. (This is a bad sign for the actual save.) Continue anyway? [y/n]: ").lower() in ["y", "yes"]:
                print("Aborting save to disk.")
                return

        # Save to Disk
        try:
            with open(self.projectFileName, "w") as newFile:
                json.dump(self.project, newFile, indent="\t")
        except Exception as x:
            print("Failed to save your work to disk. Sorry!")
            self.debug(x)


    def createProject(self):
        user = input("Project Name: ")
        newProject = {"name" : user, "books" : []}
        print("Adding books. Enter '!exit' when you are done. Enter '!amend' to correct the previous chapter.")
        while user != "!exit":
            user = input("Book name: ")
            if user == "!exit":
                break
            newBook = {"name" : user, "chapters" : []}
            numChapters = int(input("Number of Chapters: "))
            for chapterNumber in range(1, numChapters+1):
                numVerses = input("Number of Verses in Chapter " + str(chapterNumber) + ": ")
                if numVerses == "!amend":
                    chapterNumber -= 1
                    newNumVerses = int(input("AMEND Number of Verses in Chapter " + str(chapterNumber) + ": "))
                    newChapter = []
                    for i in range(newNumVerses):
                        newChapter.append(None)
                    newBook["chapters"][chapterNumber] = newChapter
                    chapterNumber += 1
                    numVerses = int(input("Number of verses in Chapter " + str(chapterNumber) + ": "))
                else:
                    numVerses = int(numVerses)
                newChapter = []
                for i in range(numVerses):
                    newChapter.append(None)
                newBook["chapters"].append(newChapter)
            newProject["books"].append(newBook)
        fileName = input("Name of file to save (omit the '.json' file extension): ")

        try:
            with open(fileName + ".json", "w") as newFile:
                json.dump(newProject, newFile)
        except Exception as x:
            print("Unable to save to disk.")
            self.debug(x)


    def track(self):
        if not self.project:
            self.pause("Select a project first!")
            return

        if self.config["promptForExport"]:
            if input("Export to file? [y/n]: ").lower() in ["y", "yes"]:
                self.filename = input("Name of file to save: ")
            else:
                self.filename = None

        menu = mastermenu.Menu("Select View")
        menu.addNumberedItem("List", callback=bibleType.progressList)
        menu.addNumberedItem("Bar Graph by Book", callback=bibleType.progressBarGraphByBook)
        menu.addNumberedItem("Bar Graph by Chapter", callback=bibleType.progressBarGraphByChapter)

        renderOut = menu.render("callback")
        self.clear()
        print(renderOut["render"])
        user = self.askForNumber("Select a number (Enter to cancel): ", max=menu.size())
        if user:
            self.bgRenderer.width = self.getTermWidth()
            self.bgRenderer.showPercent = not self.config["nopercent"]
            renderOut["mappingDict"][user]()


    def chapterCount(self, bookNumber, chapterNumber):
        chapter = self.project["books"][bookNumber-1]["chapters"][chapterNumber-1]
        totalVerses = len(chapter)
        filledVerses = totalVerses - chapter.count(None)
        return {"total":totalVerses, "filled":filledVerses}

    def bookCount(self, bookName):
        numChapters = len(self.project["books"][bookName]["chapters"])
        totalVerses = 0
        filledVerses = 0
        for chapterNumber in range(1, numChapters + 1):
            count = self.chapterCount(bookName, chapterNumber)
            totalVerses += count["total"]
            filledVerses += count["filled"]
        return {"total":totalVerses, "filled":filledVerses}

    def percentageFromCount(self, count):
        return count["filled"] / count["total"]

    def present(self, render):
        if isinstance(render, list):
            render = "\n".join(render)
        if self.filename:
            try:
                with open(self.filename, "w") as f:
                    f.write(render)
                print("Wrote file")
            except Exception as x:
                self.debug(x)
                self.pause("Failed to save file")
        else:
            self.pause(render)


    def progressList(self):
        outLines = ["Project: " + self.project["name"]]
        for bookIdx, book in enumerate(self.project["books"]):
            menu = mastermenu.Menu(book["name"])
            for chapterIdx, chapter in enumerate(book["chapters"]):
                count = self.chapterCount(bookIdx, chapterIdx+1)
                menu.addNumberedItem(str(count["filled"]) + " of " + str(count["total"]) + " verses typed")
            outLines.append("\n" + menu.render()["render"])
        self.present(outLines)


    def getTermWidth(self):
        if self.filename:
            user = self.askForNumber("How wide should the file be?", min=13)
            if not user:
                print("Using default of 80 columns")
                return 80
            return user
        else:
            try:
                termWidth = os.get_terminal_size().columns
            except:
                termWidth = self.askForNumber("How wide is your terminal?: ", min=13)
            return termWidth


    def progressBarGraphByBook(self):
        outLines = []
        outLines.append("Project: " + self.project["name"])
        for bookIdx, book in enumerate(self.project["books"]):
            self.bgRenderer.name = book["name"]
            outLines.append(self.bgRenderer.render(self.percentageFromCount(self.bookCount(bookIdx))))
        self.present(outLines)


    def progressBarGraphByChapter(self):
        outLines = []
        outLines.append("|" * (len(self.project["name"]) + 8) + "\n||| " + self.project["name"] + " |||\n" + "|" * (len(self.project["name"]) + 8) + "\n")
        for bookIdx, book in enumerate(self.project["books"], 1):
            outLines.append("\nBook: " + book["name"])
            for idx in range(1, len(book["chapters"])+1):
                self.bgRenderer.name = str(idx)
                outLines.append(self.bgRenderer.render(self.percentageFromCount(self.chapterCount(bookIdx, idx))))
        self.present(outLines)


    def settingsMenu(self):
        while True:
            menu = mastermenu.Menu("BibleType Settings")
            for key in self.config.keys():
                menu.addNumberedItem(self.configLongNames[key], str(self.config[key]), key)
            render = menu.render("callback")
            self.clear()
            print(render["render"])
            user = self.askForNumber("Select the number of the setting you want to change (Enter to cancel): ", max=menu.size())
            if not user:
                try:
                    if os.getcwd()[-8:] == "projects":
                        filename = "../btsettings.json"
                    else:
                        filename = "btsettings.json"
                    with open(filename, "w") as f:
                        json.dump(self.config, f, indent="\t")
                except:
                    self.pause("Failed to save settings to file")
                break
            key = render["mappingDict"][user]
            if isinstance(self.config[key], bool):
                self.config[key] = not self.config[key]
            else:
                newVal = input("Enter new value: ")
                if isinstance(self.config[key], int):
                    self.config[key] = int(newVal)
                else:
                    self.config[key] = newVal


# Run Standalone
if __name__ == "__main__":
    argparser = ArgumentParser()
    argparser.add_argument("-d", "--debug", help="Show extra debug info when stuff goes wrong", action="store_true")
    argparser.add_argument("-r", "--readline", help="Use readline", action="store_true")
    argparser.add_argument("--ver", "--version", help="Show program version then exit", action="store_true")
    argparser.add_argument("-p", "--project", help="Load a project file on startup", action="store")
    argparser.add_argument("-b", "--book", help="Select a book on startup. Requires --project.", action="store")
    argparser.add_argument("-c", "--chapter", help="Select a chapter on startup. Requires --project and --book.", action="store")
    argparser.add_argument("-v", "--verse", help="Select a verse on startup. Requires --project, --book, and --chapter.", action="store")
    args = argparser.parse_args()
    if args.ver:
        print("pybibletype " + version)
        exit()

    if args.readline:
        import readline

    try:
        args.chapter = int(args.chapter)
    except:
        args.chapter = None
    try:
        args.verse = int(args.verse)
    except:
        args.verse = None
    startPoint = {
        "projectFileName": args.project,
        "bookName": args.book,
        "chapterNumber": args.chapter,
        "verseNumber": args.verse
    }
    if startPoint["projectFileName"]:
        if not startPoint["projectFileName"][-5:] == ".json":
            startPoint["projectFileName"] = startPoint["projectFileName"] + ".json"

    bibleType = BibleType(startPoint, args.debug)
    if os.name == "nt":
        bibleType.config["clrComm"] = "cls"
    else:
        bibleType.config["clrComm"] = "clear"
    try:
        if os.getcwd()[-8:] == "projects":
            fileName = "../btsettings.json"
        else:
            fileName = "btsettings.json"
        with open(fileName, "r") as f:
            bibleType.config.update(json.load(f))
    except:
        print("Failed to load settings from file; using defaults. This is normal if you have never saved them before.")

    mainMenu = mastermenu.Menu("BibleType")
    mainMenu.addNumberedItem("Select Start Point", callback=bibleType.selectionMenu)
    mainMenu.addNumberedItem("Start Writing", callback=bibleType.write)
    mainMenu.addNumberedItem("Track Progress", callback=bibleType.track)
    mainMenu.addNumberedItem("Create Project", callback=bibleType.createProject)
    mainMenu.addNumberedItem("Settings", callback=bibleType.settingsMenu)
    while True:
        bibleType.clear()
        render = mainMenu.render("callback")
        print(render["render"])
        user = bibleType.askForNumber("Select a number (Enter to exit program): ", max=mainMenu.size())
        if not user:
            if input("Are you sure you want to exit? [y/N]: ").lower() in ["y", "yes"]:
                exit()
        else:
            render["mappingDict"][int(user)]()
