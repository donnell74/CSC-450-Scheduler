import sys
from Tkinter import *

mainWindow = Tk()

windowWidth = 700
windowHeight = 600
screenXpos = (mainWindow.winfo_screenwidth() / 2) - (windowWidth / 2)
screenYpos = (mainWindow.winfo_screenheight() / 2) - (windowHeight / 2)

mainWindow.geometry(str(windowWidth) + 'x' + str(windowHeight) +\
                    '+' + str(screenXpos) + '+' + str(screenYpos))

mainWindow.title('CSC Scheduler')




mainWindow.mainloop()   # NEED FOR MAC OSX AND WINDOWS
