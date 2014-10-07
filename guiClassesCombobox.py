from Tkinter import *

class MainWindow(Frame):
    counter = 0

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.button = Button(self, text = 'Make window', command = self.create_window)
        self.button.pack()

    def create_window(self):
        self.counter += 1
        t = TopLevel(self)
        t.title('New Window')
        label = Label(t, text = 'This is a new window')
        label.pack()


    def create_panels(self):
        con_panel =Frame(self)
        con_panel.pack(side=TOP, fill=BOTH, expand=Y)

        #create comboboxes
        option1 = ttk.Labelframe(con_panel, text="aaa")
        show_option = ttk.Combobox(option1)
        show_option.bind('<Return>', self._update_values)
        show_option.pack(pady=5, padx=10)

        con_panel2 = ttk.Labelframe(con_panel, text="BBB")
        ttk.Combobox(con_panel2, text="bbb").pack(pady=5, padx=10)

        con_panel(in_=con_panel, side=TOP, pady=5, padx=10)
        con_panel2(in_=con_panel, side=TOP, pady=5, padx=10)

    def _update_values(self,show):

        widget=show.widget
        txt = widget.cget('values')

##        if not vals:
##            widget.configure(values =(text,))
##        elif txt not in vals:
##            widget.configure(values=vals+(text, ))
##
##        return 'break'

        
