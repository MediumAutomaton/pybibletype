# Version 2.1-0

import mastermenu
import os
import math
import json
import time

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
        self.showPercentsInTrack = True


    def askForNumber(self, prompt):
        while True:
            user = ui.ask(prompt)
            try:
                if user:
                    return int(user)
                return ""
            except:
                ui.say("Please enter a number.")
        

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
            ui.say(renderOut["render"])
            user = self.askForNumber("Select a number (Enter to cancel)")
            if not user:
                break
            renderOut["mappingDict"][user]()


    def selectProject(self):
        prevDir = os.getcwd()
        try:
            os.chdir(btDir)
            os.chdir("projects")
        except:
            ui.say("Could not change to the projects directory. Exiting.")
            
        fileMenu = mastermenu.Menu()
        fileMenu.title = "Available Project Files"
        [fileMenu.addNumberedItem(file[:-5]) for file in os.listdir() if file[-5:] == ".json"]
        renderOut = fileMenu.render("name")
        ui.say(renderOut["render"])

        num = self.askForNumber("Select # of project (Enter to cancel)")
        if not num:
            return
        self.projectFileName = renderOut["mappingDict"][num] + ".json"
        if utils.testfile(self.projectFileName):
            try:
                with open(self.projectFileName, "r") as f:
                    self.project = json.load(f)
            except Exception as x:
                ui.say("Can't open that project.")
                ui.debug(x)
            self.book = None
            self.chapterNumber = "None"
            self.verseNumber = "None"
        else:
            ui.say("That project doesn't seem to exist")
            ui.rawAsk("\nPress Enter to continue...")

        try:
            os.chdir(prevDir)
        except:
            ui.say("You are now in the BibleType projects directory.")


    def selectBook(self):
        if not self.project:
            ui.say("Select a project first!")
            return
        bookMenu = mastermenu.Menu()
        bookMenu.title = "Books"
        [bookMenu.addNumberedItem(book["name"]) for book in self.project["books"]]
        renderOut = bookMenu.render()
        ui.say(renderOut["render"])
        user = self.askForNumber("Select a book (Enter to cancel)")
        if not user:
            return
        self.book = self.project["books"][user-1]
            

    def selectChapter(self):
        if not self.book:
            ui.say("Select a book first!")
            return
        numChapters = len(self.book["chapters"])
        ui.say("This book has " + str(numChapters) + " chapters")
        user = self.askForNumber("Select a chapter (Enter to cancel)")
        if not user:
            return
        if 0 < user and user <= numChapters:
            self.chapterNumber = user
            self.chapter = self.book["chapters"][user-1]
        else:
            ui.say("That chapter doesn't seem to exist")
            ui.rawAsk("\nPress Enter to continue...")

    def selectVerse(self):
        if not self.chapter:
            ui.say("Select a chapter first!")
            return
        numVerses = len(self.chapter)
        ui.say("This chapter has " + str(numVerses) + " verses")
        user = self.askForNumber("Select a verse (Enter to cancel)")
        if not user:
            return
        if 0 < user and user <= numVerses:
            self.verseNumber = user
        else:
            ui.say("That verse doesn't seem to exist")
            ui.rawAsk("\nPress Enter to continue...")


    def write(self, cargs):
        if (not self.project) or (not self.book) or self.chapterNumber == "None" or self.verseNumber == "None":
            ui.say("Select a start point with 'btselect' first")
            return
        if self.verseNumber > len(self.chapter):
            ui.say("You're at the end of a chapter! Please select a new start point with 'btselect' first.")
            return
        if "wpm" in cargs:
            startChapterNumber = self.chapterNumber
            startVerseNumber = self.verseNumber
            ui.say("Will calculate WPM when you're done, and will account for time lost to saving and 'Next chapter?' prompts.")
        
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
        
        ui.say(display.render()["render"])
        if not utils.promptEnd("Good to start here? [y/n]"):
            return
        
        ui.say("Type '!exit' at any point to exit.")
        if "wpm" in cargs:
            startTime = time.time()
            lostTime = 0
        while self.chapterNumber <= len(self.book["chapters"]):
            self.chapter = self.book["chapters"][self.chapterNumber-1]
            while self.verseNumber <= len(self.chapter):
                verseContents = ui.ask("[" + str(self.verseNumber) + "] ")
                if verseContents == "!exit":
                    ui.say("Exiting. Saving your work to disk...")
                    time1 = time.time()
                    self.saveToDisk()
                    if "wpm" in cargs:
                        lostTime += time.time() - time1
                        self.calculateWPM(startChapterNumber, startVerseNumber, startTime, lostTime)
                    return
                elif verseContents == "!amend":
                    self.verseNumber -= 1
                else:
                    self.chapter[self.verseNumber-1] = verseContents
                    self.verseNumber += 1
            ui.say("Reached end of chapter. Saving your work to disk...")
            time1 = time.time()
            self.saveToDisk()
            if self.chapterNumber < len(self.book["chapters"]):
                if utils.promptEnd("Continue to the next chapter? [y/n]"):
                    self.chapterNumber += 1
                    self.verseNumber = 1
                else:
                    if "wpm" in cargs:
                        lostTime += time.time() - time1
                        self.calculateWPM(startChapterNumber, startVerseNumber, startTime, lostTime)
                    return
            else:
                ui.say("Reached end of book. Please use 'btselect' to select another one.")
                if "wpm" in cargs:
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
        ui.say("Typed " + str(words) + " words in " + str(minutes) + " minutes, or " + str(words/minutes) + " WPM.")
        return
    

    def saveToDisk(self):
        # Full Save to Memory (just in case)
        self.book["chapters"][self.chapterNumber-1] = self.chapter
        for idx, book in enumerate(self.project["books"]):
            if book["name"] == self.book["name"]:
                self.project["books"][idx] = self.book
                break
        
        # Change Directory
        prevDir = os.getcwd()
        try:
            os.chdir(btDir)
            os.chdir("projects")
        except:
            ui.say("Couldn't change to projects directory. I'm here:\n" + os.getcwd())
            if not utils.promptEnd("Should I save here instead [y/n]?"):
                ui.say("Aborting save to disk.")
                return

        # Back up
        try:
            os.rename(self.projectFileName, self.projectFileName + ".backup")
        except:
            if not utils.promptEnd("Failed to back up old version. (This is a bad sign for the actual save.) Continue anyway? [y/n]"):
                ui.say("Aborting save to disk.")
                return

        # Save
        try:
            with open(self.projectFileName, "w") as newFile:
                json.dump(self.project, newFile, indent="\t")
        except Exception as x:
            ui.say("Failed to save your work to disk. Sorry!")
            ui.debug(x)

        try:
            os.chdir(prevDir)
        except:
            ui.say("You are now in the BibleType projects directory.")


    def createProject(self):
        user = ui.ask("Project Name")
        newProject = {"name" : user, "books" : []}
        ui.say("Adding books. Enter '!exit' when you are done. Enter '!amend' to correct the previous chapter.")
        while user != "!exit":
            user = ui.ask("Book name")
            if user == "!exit":
                break
            newBook = {"name" : user, "chapters" : []}
            numChapters = int(ui.ask("Number of Chapters"))
            for chapterNumber in range(1, numChapters+1):
                numVerses = ui.ask("Number of Verses in Chapter " + str(chapterNumber))
                if numVerses == "!amend":
                    chapterNumber -= 1
                    newNumVerses = int(ui.ask("AMEND Number of Verses in Chapter " + str(chapterNumber)))
                    newChapter = []
                    for i in range(newNumVerses):
                        newChapter.append(None)
                    newBook["chapters"][chapterNumber] = newChapter
                    chapterNumber += 1
                    numVerses = int(ui.ask("Number of verses in Chapter " + str(chapterNumber)))
                else:
                    numVerses = int(numVerses)
                newChapter = []
                for i in range(numVerses):
                    newChapter.append(None)
                newBook["chapters"].append(newChapter)
            newProject["books"].append(newBook)
        fileName = ui.ask("Name of file to save (omit the '.json' file extension)")

        prevDir = os.getcwd()
        try:
            os.chdir(btDir)
            os.chdir("projects")
        except:
            ui.say("Couldn't change to projects directory. I'm here:\n" + os.getcwd())
            if not utils.promptEnd("Should I try to save here instead?"):
                ui.say("Aborting save to disk.")
                return
        try:
            with open(fileName + ".json", "w") as newFile:
                json.dump(newProject, newFile)
        except Exception as x:
            ui.say("Unable to save to disk.")
            ui.debug(x)

        try:
            os.chdir(prevDir)
        except:
            ui.say("You are now in the BibleType projects directory.")


    def track(self, cargs):
        if not self.project:
            ui.say("Select a project first!")
            return

        if "nodot" in cargs:
            self.unfilledchar = " "
        if "export" in cargs:
            self.filename = ui.ask("Name of file to save")
        self.showPercentsInTrack = not "nopercent" in cargs

        menu = mastermenu.Menu()
        menu.title = "Select View"
        menu.addNumberedItem("List", callback=bibleType.progressList)
        menu.addNumberedItem("Bar Graph by Book", callback=bibleType.progressBarGraphByBook)
        menu.addNumberedItem("Bar Graph by Chapter", callback=bibleType.progressBarGraphByChapter)

        renderOut = menu.render("callback")
        ui.say(renderOut["render"])
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
                            f.write(utils.coolBorder(" " + self.project["name"] + " ") + "\n\n")
                            f.write(menu.render()["render"] + "\n\n")
                    except Exception as x:
                        ui.say("Failed to save file")
                        ui.debug(x)
                else:
                    with open(self.filename, "a") as f:
                        f.write(menu.render()["render"] + "\n\n")
            else:
                if bookIdx == 0:
                    ui.say(utils.coolBorder(" " + self.project["name"] + " ") + "\n\n")
                ui.say(menu.render()["render"])
                ui.say()
        if self.filename:
            ui.say("Wrote file")


    def getTermWidth(self):
        if self.filename:
            user = self.askForNumber("How wide should the file be?")
            if not user:
                ui.say("Using default of 80 columns")
                return 80
            if self.showPercentsInTrack:
                return user - 11
            return user - 5
        else:
            try:
                termWidth = os.get_terminal_size().columns
            except:
                termWidth = int(ui.ask("How wide is your terminal?"))
            if self.showPercentsInTrack:
                return termWidth - 11 # for extra menu characters and percents
            return termWidth - 5 # for extra menu characters


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
            percentage = str( round( totalVersesComplete / totalNumVerses, 1 ) ) + "%"
            if len(percentage) < 5: # add a leading 0 if needed for a consistent look
                percentage = "0" + percentage
            if totalNumVerses > termWidth:
                if totalVersesComplete > 0:
                    totalVersesComplete = math.floor(totalVersesComplete * (termWidth / totalNumVerses))
                if totalVersesEmpty > 0:
                    totalVersesEmpty = math.floor(totalVersesEmpty * (termWidth / totalNumVerses))
            dataToWrite = ("|" * totalVersesComplete) + (self.unfilledchar * totalVersesEmpty) + "*"
            if self.showPercentsInTrack:
                numSpaces = (termWidth + 7 - len(dataToWrite) - 5)
                dataToWrite += (" " * numSpaces) + percentage
            menu.addUnnumberedItem(bookName, dataToWrite)
        if self.filename:
            try:
                with open(self.filename, "w") as f:
                    f.write(menu.render()["render"])
                ui.say("Wrote file")
            except Exception as x:
                ui.say("Failed to save file")
                ui.debug(x)
        else:
            ui.say(menu.render()["render"])


    def progressBarGraphByChapter(self):
        termWidth = self.getTermWidth()
        if self.filename:
            with open(self.filename, "w") as f:
                f.write(utils.coolBorder(" " + self.project["name"] + " ") + "\n\n")
        else:
            ui.say(utils.coolBorder(" " + self.project["name"] + " ") + "\n\n")
        for bookIdx, book in enumerate(self.project["books"]):
            menu = mastermenu.Menu()
            menu.title = book["name"]
            for idx, chapter in enumerate(book["chapters"]):
                numVerses = len(chapter)
                numVersesEmpty = chapter.count(None)
                numVersesTyped = numVerses - numVersesEmpty
                percentage = str( round( numVersesTyped / numVerses, 1 ) ) + "%"
                if len(percentage) < 5:  # add a leading 0 if needed for a consistent look
                    percentage = "0" + percentage
                if numVersesTyped + numVersesEmpty > termWidth:
                    if numVersesTyped > 0:
                        numVersesTyped = math.floor(numVersesTyped * (termWidth / numVerses))
                    if numVersesEmpty > 0:
                        numVersesEmpty = math.floor(numVersesEmpty * (termWidth / numVerses))
                dataToWrite = ("|" * numVersesTyped) + (self.unfilledchar * numVersesEmpty) + "*"
                if self.showPercentsInTrack:
                    numSpaces = (termWidth + 8 - len(str(idx+1)) - len(dataToWrite) - 5)
                    dataToWrite += (" " * numSpaces) + percentage
                menu.addNumberedItem(dataToWrite)
            if self.filename:
                if bookIdx == 0:
                    try:
                        with open(self.filename, "w") as f:
                            f.write(utils.coolBorder(" " + self.project["name"] + " ") + "\n\n")
                            f.write(menu.render()["render"] + "\n\n")
                    except Exception as x:
                        ui.say("Failed to save file")
                        ui.debug(x)
                else:
                    with open(self.filename, "a") as f:
                        f.write(menu.render()["render"] + "\n\n")
            else:
                ui.say(menu.render()["render"])
                ui.say()
        if self.filename:
            ui.say("Wrote file")



bibleType = BibleType()

envVer = 1
def passEnv(env):
    try:
        global ui, utils, btDir
        ui = env["ui"]
        utils = env["Utils"]
        btDir = os.getcwd()

        ui.say("Environment hand-off successful")
    except:
        print("Environment hand-off failed; bibletype will (probably) not work as expected")

newcomms = {
    "btselect" : "bibleType.selectionMenu()",
    "btwrite" : "bibleType.write(cargs)",
    "btcreate" : "bibleType.createProject()",
    "bttrack" : "bibleType.track(cargs)",
}
