# Conditional debug messages

enabled = False

def debug(msg):
    if enabled:
        print(msg)