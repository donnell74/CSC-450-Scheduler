from Tkinter import Label

class ToolTips(object):
    
    def __init__(self, root):
        self.root = root
        self.tip = Label()  # holds the tool tip text
        self.btn_name = ''

        self.buttons = ['Home', 'Constraint', 'View', 'Misc', 'RUN']
        
        # tool tip text paired with a button
        self.tips = {'Home' : 'Return home.',
                     'Constraint' : 'Make a custom schedule.',
                     'View' : 'View the schedules.',
                     'Misc' : 'Misc',
                     'RUN' : 'Generate schedules.'}
        # y position of the tool tip
        self.tip_y_pos = {'Home' : 2,
                        'Constraint' : 107,
                        'View' : 212,
                        'Misc' : 317,
                        'RUN' : 422}

        # create event listeners
        self.root.bind('<Enter>', self.__hover_on)
        self.root.bind('<Leave>', self.__hover_off)

    def __hover_on(self, event):
        """ Changes the button color and displays tool tip """
        try:
            button = event.widget
            self.btn_name = button['text']
            if self.btn_name in self.buttons:
                if not (self.btn_name == 'RUN'):
                    button['bg'] = 'white'
                self.__tool_tip()
        except:
            pass
            
    def __hover_off(self, event):
        """ Changes button color back to normal and deletes tool tip """
        try:
            button = event.widget
            self.btn_name = button['text']
            if self.btn_name in self.buttons:
                if not (self.btn_name == 'RUN'):
                    button['bg'] = 'SystemButtonFace'
                self.tip.destroy()  # remove tool tip
        except:
            pass

    def __tool_tip(self):
        """ Displays a tool tip on the GUI """
        self.tip = Label(self.root, width = 0, height = 2, padx = 10, text = '', bg = 'green')
        self.tip['text'] = self.tips[self.btn_name]
        self.tip.pack()
        self.tip.place(x = -150, y = self.tip_y_pos[self.btn_name])
        self.__animate()

    def __animate(self):
        try:
            if self.tip['width'] == 0:
                self.root.after(500, self.__animate)
            elif self.tip['width'] == 1:
                self.tip.place(x = 150)
                self.root.after(15, self.__animate)
            elif self.tip['width'] <= 25:
                self.root.after(15, self.__animate)
                
            self.tip['width'] += 1
        except:
            pass
