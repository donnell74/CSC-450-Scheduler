import sys
from Tkinter import *

# Define click functions
def clickHome():
    topLabelText.set("Home Screen")
    return

def clickConstraint():
    topLabelText.set("Constraint Screen")
    return

def clickView():
    topLabelText.set("View Screen")
    return

def clickMisc():
    topLabelText.set("Misc Screen")
    return

def clickRun():
    # run the scheduler
    topLabelText.set("Scheduler should be running...")
    return

mainWindow = Tk()

windowWidth = 850
windowHeight = 600
screenXpos = (mainWindow.winfo_screenwidth() / 2) - (windowWidth / 2)
screenYpos = (mainWindow.winfo_screenheight() / 2) - (windowHeight / 2)

mainWindow.geometry(str(windowWidth) + 'x' + str(windowHeight) +\
                    '+' + str(screenXpos) + '+' + str(screenYpos))

mainWindow.title('CSC Scheduler')

topLabelText = StringVar()
topLabelText.set("You have just begun!")
topLabel = Label(mainWindow, textvariable = topLabelText)
topLabel.grid(row = 0, column = 2)

homeButton = Button(mainWindow, text = "Home", width = 15, height = 5, command = clickHome)
homeButton.grid(row = 0, column = 0)

constraintButton = Button(mainWindow, text = "Constraint", width = 15, height = 5, command = clickConstraint)
constraintButton.grid(row = 1, column = 0)

viewButton = Button(mainWindow, text = "View", width = 15, height = 5, command = clickView)
viewButton.grid(row = 2, column = 0)

miscButton = Button(mainWindow, text = "...", width = 15, height = 5, command = clickMisc)
miscButton.grid(row = 3, column = 0)

runButton = Button(mainWindow, text = "RUN", width = 15, height = 10, bg = "green", command = clickRun)
runButton.grid(row = 4, column = 0)

mainWindow.mainloop()   # NEED FOR MAC OSX AND WINDOWS



