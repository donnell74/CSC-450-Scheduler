import Tkinter as tk

class MainWindow(tk.Frame):
    counter = 0

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.button = tk.Button(self, text = 'Make window', command = self.create_window)
        self.button.pack()

    def create_window(self):
        self.counter += 1
        t = tk.TopLevel(self)
        t.title('New Window')
        label = tk.Label(t, text = 'This is a new window')
        label.pack()
