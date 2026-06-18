version = "2.2-0"

import mastermenu
import os
import math
import json
import time
from argparse import ArgumentParser

class BibleType:
    def __init__(self):
        self.projectFileName = None
        self.project = None
        self.book = None
        self.chapterNumber = "None"
        self.chapter = None
        self.verseNumber = "None"
        self.filename = None
        self.unfilledchar = "."
        self.showDebug = False
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

    def debug(self, msg):
        if self.showDebug:
            print(msg)

    def clear(self):
        if self.config["clearForMenus"]:
            os.system(self.config["clrComm"])

    def askForNumber(self, prompt):
        while True:
            user = input(prompt)
            try:
                if user:
                    return int(user)
                return ""
            except:
                print("Please enter a number.")
                input("Press Enter to continue...")
        
    def changeToProjectsDir(self):
        if os.getcwd()[-8:] != "projects":
            try:
                os.chdir("projects")
            except:
                print("Something happened to the projects directory!")
                input("Press Enter to exit the program...")
                exit()


    def selectionMenu(self):
        menu = mastermenu.Menu()
        menu.title = "BibleType Project Selection"
        projectItem = menu.addNumberedItem("Project", callback=self.selectProject)
        bookItem = menu.addNumberedItem("Book", callback=self.selectBook)
        chapterItem = menu.addNumberedItem("Chapter", self.chapterNumber, self.selectChapter)
        verseItem = menu.addNumberedItem("Verse", self.verseNumber, self.selectVerse)

        while True:
            projectItem.data = self.project["name"] if self.project else "None"
            bookItem.data = self.book["name"] if self.book else "None"            
            chapterItem.data = self.chapterNumber
            verseItem.data = self.verseNumber
            
            renderOut = menu.render("callback")
            self.clear()
            print(renderOut["render"])
            user = self.askForNumber("Select a number (Enter to cancel): ")
            if not user:
                break
            renderOut["mappingDict"][user]()


    def selectProject(self):
        self.changeToProjectsDir()
            
        fileMenu = mastermenu.Menu()
        fileMenu.title = "Available Project Files"
        [fileMenu.addNumberedItem(file[:-5]) for file in os.listdir() if file[-5:] == ".json"]
        renderOut = fileMenu.render("name")
        print(renderOut["render"])

        num = self.askForNumber("Select # of project (Enter to cancel): ")
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


    def selectBook(self):
        if not self.project:
            print("Select a project first!")
            input("Press Enter to continue...")
            return
        bookMenu = mastermenu.Menu()
        bookMenu.title = "Books"
        [bookMenu.addNumberedItem(book["name"]) for book in self.project["books"]]
        renderOut = bookMenu.render()
        print(renderOut["render"])
        user = self.askForNumber("Select # of book (Enter to cancel): ")
        if not user:
            return
        self.book = self.project["books"][user-1]
            

    def selectChapter(self):
        if not self.book:
            print("Select a book first!")
            input("Press Enter to continue...")
            return
        numChapters = len(self.book["chapters"])
        print("This book has " + str(numChapters) + " chapters")
        user = self.askForNumber("Select a chapter (Enter to cancel): ")
        if not user:
            return
        if 0 < user and user <= numChapters:
            self.chapterNumber = user
            self.chapter = self.book["chapters"][user-1]
        else:
            print("That chapter doesn't seem to exist")
            input("Press Enter to continue...")

    def selectVerse(self):
        if not self.chapter:
            print("Select a chapter first!")
            input("Press Enter to continue...")
            return
        numVerses = len(self.chapter)
        print("This chapter has " + str(numVerses) + " verses")
        user = self.askForNumber("Select a verse (Enter to cancel): ")
        if not user:
            return
        if 0 < user and user <= numVerses:
            self.verseNumber = user
        else:
            print("That verse doesn't seem to exist")
            input("Press Enter to continue...")


    def write(self):
        if (not self.project) or (not self.book) or self.chapterNumber == "None" or self.verseNumber == "None":
            print("Select a start point with 'btselect' first!")
            input("Press Enter to continue...")
            return
        if self.verseNumber > len(self.chapter):
            print("You're at the end of a chapter! Please select a new start point with 'btselect' first.")
            input("Press Enter to continue...")
            return
        if self.config["wpm"]:
            startChapterNumber = self.chapterNumber
            startVerseNumber = self.verseNumber
            print("Will calculate WPM when you're done, and will account for time lost to saving and 'Next chapter?' prompts.")
        
        display = mastermenu.Menu()
        display.heading = "Starting Location"
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
                verseContents = input("[" + str(self.verseNumber) + "] ")
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
                print("Reached end of book. Please use 'btselect' to select another one.")
                input("Press Enter to continue...")
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
            print("Select a project first!")
            return

        if self.config["promptForExport"]:
            if input("Export to file? [y/n]: ").lower() in ["y", "yes"]:
                self.filename = input("Name of file to save: ")

        menu = mastermenu.Menu()
        menu.title = "Select View"
        menu.addNumberedItem("List", callback=bibleType.progressList)
        menu.addNumberedItem("Bar Graph by Book", callback=bibleType.progressBarGraphByBook)
        menu.addNumberedItem("Bar Graph by Chapter", callback=bibleType.progressBarGraphByChapter)

        renderOut = menu.render("callback")
        self.clear()
        print(renderOut["render"])
        user = self.askForNumber("Select a number (Enter to cancel)")
        if user:
            renderOut["mappingDict"][user]()


    def progressList(self):
        for bookIdx, book in enumerate(self.project["books"]):
            menu = mastermenu.Menu()
            menu.title = book["name"]
            for chapter in book["chapters"]:
                numVerses = len(chapter)
                numVersesTyped = 0
                for verse in chapter:
                    if verse:
                        numVersesTyped += 1
                menu.addNumberedItem(str(numVersesTyped) + " of " + str(numVerses) + " verses typed")
            if self.filename:
                if bookIdx == 0:
                    try:
                        with open(self.filename, "w") as f:
                            f.write("|" * (len(self.project["name"]) + 8) + "\n||| " + self.project["name"] + " |||\n" + "|" * (len(self.project["name"]) + 8) + "\n")
                            f.write(menu.render()["render"] + "\n\n")
                    except Exception as x:
                        print("Failed to save file")
                        input("Press Enter to continue...")
                        self.debug(x)
                else:
                    with open(self.filename, "a") as f:
                        f.write(menu.render()["render"] + "\n\n")
            else:
                if bookIdx == 0:
                    print("|" * (len(self.project["name"]) + 8) + "\n||| " + self.project["name"] + " |||\n" + "|" * (len(self.project["name"]) + 8) + "\n")
                print(menu.render()["render"] + "\n")
        if self.filename:
            print("Wrote file")
        else:
            input("Press Enter to continue...")


    def getTermWidth(self):
        if self.filename:
            user = self.askForNumber("How wide should the file be?")
            if not user:
                print("Using default of 80 columns")
                return 80
            if self.config["nopercent"]:
                return user - 5
            return user - 11
        else:
            try:
                termWidth = os.get_terminal_size().columns
            except:
                termWidth = int(input("How wide is your terminal? "))
            if self.config["nopercent"]:
                return termWidth - 5 # for extra menu characters
            return termWidth - 11  # for extra menu characters and percents


    def progressBarGraphByBook(self):
        actualTermWidth = self.getTermWidth()
        menu = mastermenu.Menu()
        menu.title = self.project["name"]
        for bookIdx, book in enumerate(self.project["books"]):
            bookName = book["name"]
            termWidth = actualTermWidth - len(bookName) - 2
            totalVersesComplete = 0
            totalVersesEmpty = 0
            for chapter in book["chapters"]:
                numVerses = len(chapter)
                numVersesTyped = 0
                for verse in chapter:
                    if verse:
                        numVersesTyped += 1
                numVersesEmpty = numVerses - numVersesTyped
                totalVersesComplete += numVersesTyped
                totalVersesEmpty += numVersesEmpty
            totalNumVerses = totalVersesComplete + totalVersesEmpty
            percentage = str( round( (totalVersesComplete / totalNumVerses) * 100, 1 ) ) + "%"
            if percentage == "100.0%":
                percentage = "100 %"
            elif len(percentage) < 5: # add a leading 0 if needed for a consistent look
                percentage = "0" + percentage
            if totalNumVerses > termWidth:
                if totalVersesComplete > 0:
                    totalVersesComplete = math.floor(totalVersesComplete * (termWidth / totalNumVerses))
                if totalVersesEmpty > 0:
                    totalVersesEmpty = math.floor(totalVersesEmpty * (termWidth / totalNumVerses))
            dataToWrite = ("|" * totalVersesComplete) + (self.unfilledchar * totalVersesEmpty) + "*"
            if not self.config["nopercent"]:
                numSpaces = (termWidth + 7 - len(dataToWrite) - 5)
                dataToWrite += (" " * numSpaces) + percentage
            menu.addUnnumberedItem(bookName, dataToWrite)
        if self.filename:
            try:
                with open(self.filename, "w") as f:
                    f.write(menu.render()["render"])
                print("Wrote file")
            except Exception as x:
                print("Failed to save file")
                input("Press Enter to continue...")
                self.debug(x)
        else:
            print(menu.render()["render"] + "\n")
            input("Press Enter to continue...")


    def progressBarGraphByChapter(self):
        termWidth = self.getTermWidth()
        if self.filename:
            with open(self.filename, "w") as f:
                f.write("|" * (len(self.project["name"]) + 8) + "\n||| " + self.project["name"] + " |||\n" + "|" * (len(self.project["name"]) + 8) + "\n")
        else:
            print("|" * (len(self.project["name"]) + 8) + "\n||| " + self.project["name"] + " |||\n" + "|" * (len(self.project["name"]) + 8) + "\n")
        for bookIdx, book in enumerate(self.project["books"]):
            menu = mastermenu.Menu()
            menu.title = book["name"]
            for idx, chapter in enumerate(book["chapters"]):
                numVerses = len(chapter)
                numVersesEmpty = chapter.count(None)
                numVersesTyped = numVerses - numVersesEmpty
                percentage = str( round( (numVersesTyped / numVerses) * 100, 1 ) ) + "%"
                if percentage == "100.0%":
                    percentage = "100 %"
                elif len(percentage) < 5:  # add a leading 0 if needed for a consistent look
                    percentage = "0" + percentage
                if numVersesTyped + numVersesEmpty > termWidth:
                    if numVersesTyped > 0:
                        numVersesTyped = math.floor(numVersesTyped * (termWidth / numVerses))
                    if numVersesEmpty > 0:
                        numVersesEmpty = math.floor(numVersesEmpty * (termWidth / numVerses))
                dataToWrite = ("|" * numVersesTyped) + (self.unfilledchar * numVersesEmpty) + "*"
                if not self.config["nopercent"]:
                    numSpaces = (termWidth + 8 - len(str(idx+1)) - len(dataToWrite) - 5)
                    dataToWrite += (" " * numSpaces) + percentage
                menu.addNumberedItem(dataToWrite)
            if self.filename:
                if bookIdx == 0:
                    try:
                        with open(self.filename, "w") as f:
                            f.write("|" * (len(self.project["name"]) + 8) + "\n||| " + self.project["name"] + " |||\n" + "|" * (len(self.project["name"]) + 8))
                            f.write(menu.render()["render"] + "\n\n")
                    except Exception as x:
                        print("Failed to save file")
                        input("Press Enter to continue...")
                        self.debug(x)
                else:
                    with open(self.filename, "a") as f:
                        f.write(menu.render()["render"] + "\n\n")
            else:
                print(menu.render()["render"] + "\n")
        if self.filename:
            print("Wrote file")
        else:
            input("Press Enter to continue...")


    def settingsMenu(self):
        while True:
            menu = mastermenu.Menu()
            menu.title = "BibleType Settings"
            for key in self.config.keys():
                menu.addNumberedItem(self.configLongNames[key], str(self.config[key]), key)
            render = menu.render("callback")
            self.clear()
            print(render["render"])
            user = self.askForNumber("Select the number of the setting you want to change (Enter to cancel): ")
            if not user:
                try:
                    with open("btsettings.json", "w") as f:
                        json.dump(self.config, f, indent="\t")
                except:
                    print("Failed to save settings to file")
                break
            if user > len(menu.items):
                print("That number is too high!")
                input("Press Enter to continue...")
            else:
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
    argparser.add_argument("--ver", "--version", help="Show program version then exit", action="store_true")
    args = argparser.parse_args()
    if args.ver:
        print("pybibletype " + version)
        exit()

    bibleType = BibleType()
    bibleType.showDebug = args.debug
    if os.name == "nt":
        bibleType.config["clrComm"] = "cls"
    else:
        bibleType.config["clrComm"] = "clear"
    try:
        with open("btsettings.json", "r") as f:
            bibleType.config.update(json.load(f))
    except:
        print("Failed to load settings from file; using defaults.")
        print("This is normal if you have never saved them before.")

    mainMenu = mastermenu.Menu()
    mainMenu.title = "BibleType"
    mainMenu.addNumberedItem("Select Start Point", callback=bibleType.selectionMenu)
    mainMenu.addNumberedItem("Start Writing", callback=bibleType.write)
    mainMenu.addNumberedItem("Track Progress", callback=bibleType.track)
    mainMenu.addNumberedItem("Create Project", callback=bibleType.createProject)
    mainMenu.addNumberedItem("Settings", callback=bibleType.settingsMenu)
    while True:
        bibleType.clear()
        render = mainMenu.render("callback")
        print(render["render"])
        user = bibleType.askForNumber("Select a number (Enter to exit program): ")
        if not user:
            if input("Are you sure you want to exit? [y/n]: ").lower() in ["y", "yes"]:
                exit()
        else:
            if user < 1 or user > 5:
                print("Number must be between 1 and 5")
                input("Press Enter to continue...")
            else:
                render["mappingDict"][int(user)]()
