from os import name as osName, system as osSystem, get_terminal_size as termSize


if osName == "nt":
    clrComm = "cls"
else:
    clrComm = "clear"


def clear():
    osSystem(clrComm)


def askForNumber(prompt, default):
    while True:
        user = input(prompt)
        try:
            if user:
                return int(user)
            if default:
                print("Using default of " + str(default))
                return default
            return ""
        except:
            print("Please enter a number.")
            input("Press Enter to continue...")


def confirm(prompt):
    return input(prompt + " [y/n]: ").lower() in ["y", "yes"]


def pause(msg):
    if msg:
        print(msg)
    input("Press Enter to continue...")


def getTermWidth(prompt):
    if prompt:
        return askForNumber(prompt, 80)
    try:
        return termSize().columns
    except:
        return askForNumber("How wide is your terminal?: ", 80)
