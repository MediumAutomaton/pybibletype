class One:
    def __init__(self, menu):
        menu.register("One", self.hello)

    def hello(self):
        print("One!")