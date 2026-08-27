class Two:
    def __init__(self, menu):
        menu.register("Two", self.hello)

    def hello(self):
        print("Two!")