# Default project reader plugin for pybibletype 2.x project files

from json import load as jsonLoad

class Plugin:
    def __init__(self):
        self.project = None

    def selectFile(self, fileName):
        with open(fileName, "r") as f:
            self.project = jsonLoad(f)

    def verseContents(self, position):
        return len(self.fetchBook(position["bookName"])["chapters"][position["chapterNumber"]-1][position["verseNumber"]-1])
