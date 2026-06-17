import json
import os
import importlib
import sys

btdir = os.getcwd()

def btconvert1():
    # Select project
    os.chdir(btdir)
    os.chdir("projects")
    sys.path.append(os.getcwd())
    [ui.say(file) for file in os.listdir() if file[-3:] == ".py"]
    fileName = ui.ask("File name to convert (type out name as displayed above) (Enter to cancel)")
    if fileName == "":
        return

    # Back up
    with open(fileName, "r") as originalFile:
        with open(fileName + ".old", "w") as backupFile:
            backupFile.write(originalFile.read())

    # Convert
    oldProject = importlib.import_module(fileName[:-3]).BibleTypeProject().project
    newProject = {
        "name" : oldProject["name"],
        "books" : []
    }
    for oldBookName in oldProject["books"].keys():
        oldBook = oldProject["books"][oldBookName]
        newBook = {
            "name" : oldBookName,
            "chapters" : []
        }
        for chapterNumber in range(1, oldBook["numChapters"]+1):
            oldChapter = oldBook[chapterNumber]
            newChapter = []
            for verseNumber in range(1, oldChapter["numVerses"]+1):
                try:
                    newChapter.append(oldChapter[verseNumber])
                except KeyError:
                    newChapter.append(None)
            newBook["chapters"].append(newChapter)
        newProject["books"].append(newBook)

    # Save
    with open(fileName[:-3] + ".json", "w") as newFile:
        json.dump(newProject, newFile, indent="\t")

    # Verify
    with open(fileName[:-3] + ".json", "r") as newFile:
        temp = json.load(newFile)

    os.remove(fileName)
    ui.say("File converted and verified. You are in the BibleType projects directory.")


def btcommakill():
    # Select project
    os.chdir(btdir)
    os.chdir("projects")
    sys.path.append(os.getcwd())
    [ui.say(file) for file in os.listdir() if file[-5:] == ".json"]
    fileName = ui.ask("File name to convert (type out name as displayed above) (Enter to cancel)")
    if fileName == "":
        return

    # Back up and load project
    with open(fileName, "r") as originalFile:
        with open(fileName + ".old", "w") as backupFile:
            backupFile.write(originalFile.read())
        originalFile.seek(0)
        project = json.load(originalFile)

    # Iterate through and kill commas
    for book in project["books"]:
        for chapter in book["chapters"]:
            for idx, verse in enumerate(chapter):
                if verse:
                    inCommaChain = False
                    newVerse = ""
                    for letter in verse:
                        if letter == ",":
                            if not inCommaChain:
                                newVerse += letter
                                inCommaChain = True
                        else:
                            newVerse += letter
                            inCommaChain = False
                    chapter[idx] = newVerse

    # Save back to disk
    with open(fileName, "w") as newFile:
        json.dump(project, newFile, indent="\t")

    ui.say("Done. You are now in the BibleType projects directory.")
    ui.say("Make sure to re-select the project with 'btselect' to re-load it from the fixed file.")


def btrestore():
    # Select project
    os.chdir(btdir)
    os.chdir("projects")
    sys.path.append(os.getcwd())
    [ui.say(file) for file in os.listdir() if file[-7:] == ".backup"]
    fileName = ui.ask("File name to restore (type out name as displayed above) (Enter to cancel)")
    if fileName == "":
        return

    with open(fileName[:-7], "w") as newFile:
        with open(fileName, "r") as backupFile:
            newFile.write(backupFile.read())

    ui.say("File restored from backup. You are now in the BibleType projects directory.")


envVer = 1
def passEnv(env):
    global ui, utils
    ui = env["ui"]
    utils = env["Utils"]

newcomms = {
    "btconvert1" : "btconvert1()",
    "btcommakill" : "btcommakill()",
    "btrestore" : "btrestore()",
}

# Quickly syntax-check module by running it
if __name__ == "__main__":
    btconvert1()
    btcommakill()
