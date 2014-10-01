from Tkinter import *

class MainWindow(Frame):
    counter = 0

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.button = Button(self, text = 'Make window', command = self.create_window)
        self.button.pack()

    def create_window(self):
        self.counter += 1
        t = TopLevel(self)
        t.title('New Window')
        label = Label(t, text = 'This is a new window')
        label.pack()
