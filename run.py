from __future__ import print_function
from gui import mainPage
import globs

if __name__ == "__main__":
    globs.init()
    globs.mainScheduler.generate_starting_population()
    print(globs.mainScheduler.weeks[0].print_concise())
    mainPage.main()
