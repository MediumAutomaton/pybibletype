from os import name as osName, system as osSystem, get_terminal_size as termSize


if osName == "nt":
    clrComm = "cls"
else:
    clrComm = "clear"


def clear():
    osSystem(clrComm)


def pause(msg):
    if msg:
        print(msg)
    input("Press Enter to continue...")


def askForNumber(prompt, min=1, max=None):
    while True:
        user = input(prompt)
        if not user:
            return ""
        try:
            user = int(user)
            if user < min or (max and user > max):
                if max:
                    pause("Number must be between " + str(min) + " and " + str(max))
                else:
                    pause("Number must be greater than " + str(min))
            else:
                return user
        except:
            pause("Please enter a number.")


def confirm(prompt):
    return input(prompt + " [y/n]: ").lower() in ["y", "yes"]


def getTermWidth(prompt):
    if prompt:
        return askForNumber(prompt, 80)
    try:
        return termSize().columns
    except:
        return askForNumber("How wide is your terminal?: ", 80)
