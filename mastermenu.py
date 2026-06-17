# MasterMenu object-oriented menu builder and renderer
# Version 2.0-0

# Exceptions
class InvalidSelectBy(Exception):
    def __init__(self, message, errors):
        super(message, errors)

class BadNumberedFormat(Exception):
    def __init__(self, message, errors):
        super(message, errors)

class BadItem(Exception):
    def __init__(self, message, errors):
        super(message, errors)


# Menu Contents
class UnnumberedItem:
    def __init__(self, name, data):
        self.name = name
        self.data = data

class NumberedItem:
    def __init__(self, name, data, callback):
        self.name = name
        self.data = data
        self.callback = callback

class Separator:
    def __init__(self, name, height):
        self.name = name
        self.height = height

class Header:
    def __init__(self, name):
        self.name = name


# Menu Configuration
class MenuFormat:
    def __init__(self):
        self.unnumberedStart = " -  "
        self.numberedStart = "[n] "
        self.nameDataSeparator = ": "
        self.headerLeft = "]]] "
        self.headerRight = " [[["
        self.titleLeft = "+-+-+ "
        self.titleRight = " +-+-+"
        self.leadingZeroes = False


class Menu:
    def __init__(self):
        self.title = ""
        self.items = []

    def addNumberedItem(self, name, data=None, callback=None):
        newItem = NumberedItem(name, data, callback)
        self.items.append(newItem)
        return newItem

    def addUnnumberedItem(self, name, data=None):
        newItem = UnnumberedItem(name, data)
        self.items.append(newItem)
        return newItem

    def addHeader(self, name):
        newItem = Header(name)
        self.items.append(newItem)
        return newItem

    def addSeparator(self, name, height=1):
        newItem = Separator(name, height)
        self.items.append(newItem)
        return newItem

    def removeItemByName(self, nameToRemove):
        for item in self.items:
            if item.name == nameToRemove:
                self.items.remove(item)

    def removeItemByIndex(self, indexToRemove):
        self.items.pop(indexToRemove)

    def render(self, selectBy="name", format=MenuFormat()):
        if selectBy not in ["name", "data", "callback"]:
            raise InvalidSelectBy("render(selectBy) must be 'name', 'data', or 'callback'")
        if format.numberedStart.count("n") < 1:
            raise BadNumberedFormat("numberedStart must contain the character 'n', where the item number will appear when rendering")
        outLines = [ format.titleLeft + str(self.title) + format.titleRight ]
        idx = 1
        mappingDict = {}
        for item in self.items:
            if isinstance(item, Header):
                out = format.headerLeft + str(item.name) + format.headerRight
            elif isinstance(item, Separator):
                out = "\n" * (item.height - 1) # less 1 because a newline is already added after this item later
            else: # Only item types that can display data are left
                # Do the bullet point first
                if isinstance(item, NumberedItem):
                    out = format.numberedStart.replace("n", str(idx), 1)
                    mappingDict.update( { idx : {"name":item.name, "data":item.data, "callback":item.callback}[selectBy] } )
                    idx += 1
                elif isinstance(item, UnnumberedItem):
                    out = format.unnumberedStart
                else:
                    raise BadItem("Invalid MasterMenu item! Use only Menu.add____() methods to avoid this problem.")
                # Now do name and, if applicable, data
                out += str(item.name)
                if item.data:
                    out += (": " + str(item.data))
            outLines.append(out)
        return {
            "render" : "\n".join(outLines),
            "mappingDict" : mappingDict
        }
