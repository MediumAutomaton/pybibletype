# Default project writer plugin for pybibletype 2.x project files

from json import load as jsonLoad, dump as jsonDump
from os import listdir as osListdir, remove as osRemove, rename as osRename

from cliplugins.library.debug import debug

# Store position
projectFileName = None
bookName = None
chapterNumber = 0
verseNumber = 0

# Hold project in memory
project = None
book = None
chapter = None


def findSupportedProjects(self):
    projects = []
    for fileName in [x for x in osListdir() if x[-5:] == ".json"]:
        try:
            with open(fileName) as f:
                jsonLoad(f)
            projects.append(fileName[:-5])
        except:
            pass
    return projects


def selectFile(fileName):
    global projectFileName, project
    projectFileName = fileName
    with open(fileName, "r") as f:
        project = jsonLoad(f)


# Internal use only!
def fetchBook(bookName):
    for book in project["books"]:
        if book["name"] == bookName:
            return book


def setPosition(argBookName, argChapterNumber, argVerseNumber):
    global bookName, chapterNumber, verseNumber, book, chapter
    bookName = argBookName
    chapterNumber = argChapterNumber
    verseNumber = argVerseNumber

    book = fetchBook(argBookName)
    chapter = book[chapterNumber-1]


def getPosition():
    return {
        "bookName": bookName,
        "chapterNumber": chapterNumber,
        "verseNumber": verseNumber
    }


def commitVerse(verseContents):
    global verseNumber
    chapter[verseNumber-1] = verseContents
    if verseNumber == len(chapter):
        return True
    verseNumber += 1
    return False


def commitChapter():
    # Full Save to Memory (just in case)
    global book
    book["chapters"][chapterNumber-1] = chapter
    for idx, book in enumerate(project["books"]):
        if book["name"] == book["name"]:
            project["books"][idx] = book
            break
    # Back up
    try:
        # On Windows, os.rename() will not overwrite an existing file
        osRemove(projectFileName + ".backup")
    except:
        pass
    try:
        osRename(projectFileName, projectFileName + ".backup")
    except Exception as x:
        debug(x)
        if not input("Failed to back up old version. (This is a bad sign for the actual save.) Continue anyway? [y/n]: ").lower() in ["y", "yes"]:
            print("Aborting save to disk.")
            return
    # Save to Disk
    try:
        with open(projectFileName, "w") as newFile:
            jsonDump(project, newFile, indent="\t")
    except Exception as x:
        print("Failed to save your work to disk. Sorry!")
        debug(x)


def books():
    books = []
    for book in project["books"]:
        books.append(book["name"])


def chaptersInBook(bookName):
    return len(fetchBook(bookName)["chapters"])


def versesInChapter(bookName, chapterNumber):
    return len(fetchBook(bookName)["chapters"][chapterNumber-1])


def chapterProgress(bookName, chapterNumber):
    chapter = fetchBook(bookName)["chapters"][chapterNumber - 1]
    totalVerses = len(chapter)
    filledVerses = totalVerses - chapter.count(None)
    return {"total": totalVerses, "filled": filledVerses}


def bookProgress(bookName):
    book = fetchBook(bookName)
    totalVerses, filledVerses = 0, 0
    for chapterNumber in range(1, len(project["books"][bookName]["chapters"])+1):
        totalVerses += len(book[chapterNumber])
        filledVerses += totalVerses - book[chapterNumber].count(None)
        return {"total": totalVerses, "filled": filledVerses}


def modifiedTime(self):
    return 0
