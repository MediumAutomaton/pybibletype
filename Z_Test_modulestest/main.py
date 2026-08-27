import one
import two
import menu

mainMenu = menu.Menu()
one = one.One(mainMenu)
two = two.Two(mainMenu)

mainMenu.prompt()
