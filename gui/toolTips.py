from Tkinter import Label

class ToolTips(object):
    
    def __init__(self, root):
        self.root = root
        self.tip = Label()  # holds the tool tip text
        self.btn_name = ''
        self.animation_delay = 500     # begin animation after 0.5 seconds
        self.animation_speed = 15      # call __animate every 0.015 seconds
        self._animation = None         # holds a call to __animate
        self.buttons_clicked = []
        
        # holds the button text of the buttons that need tooltips
        self.buttons = ['Home',
                        'Constraint',
                        'View',
                        'RUN',
                        'Misc',
                        'Schedule 1',
                        'Schedule 2',
                        'Schedule 3',
                        'Schedule 4',
                        'Schedule 5',
                        'Add Course Constraint',
                        'Add Instructor Constraint',
                        'Add Constraint']
        
        # button name paired with tool tip description
        self.tips = {self.buttons[0] : 'Return home.',
                     self.buttons[1] : 'Make a custom schedule.',
                     self.buttons[2] : 'View the schedules.',
                     self.buttons[3] : 'Generate schedules.',
                     self.buttons[4] : 'Misc'}

        # x position of a tool tip
        self.tip_x_pos = {self.buttons[0] : 150,
                        self.buttons[1] : 150,
                        self.buttons[2] : 150,
                        self.buttons[3] : 150,
                        self.buttons[4] : 150}
        
        # y position of a tool tip
        self.tip_y_pos = {self.buttons[0] : 2,
                        self.buttons[1] : 107,
                        self.buttons[2] : 212,
                        self.buttons[3] : 317,
                        self.buttons[4] : 422}

        # create event listeners
        self.root.bind('<Enter>', self.__hover_on)
        self.root.bind('<Leave>', self.__hover_off)
        self.root.bind('<Button-1>', self.__on_click)

    def __hover_on(self, event):
        """ Changes the button color and displays tool tip """
        try:
            button = event.widget
            self.btn_name = button['text']
            if self.btn_name in self.buttons:
                
                if not (self.btn_name == 'RUN') and \
                   not (button in self.buttons_clicked):
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
                
                if not (self.btn_name == 'RUN') and \
                   not (button in self.buttons_clicked):
                       button['bg'] = 'SystemButtonFace'
                    
                # cancel queued call to self.__animate
                self.root.after_cancel(self._animation)
                self.tip.destroy()  # destroy tool tip label
        except:
            pass

    def __on_click(self, event):
        """ Changes button color back to normal and deletes tool tip """
        try:
            button = event.widget
            self.btn_name = button['text']
            if self.btn_name.split(' ')[0] == 'Schedule':
                if len(self.buttons_clicked) > 0:
                    self.buttons_clicked[0]['bg'] = 'SystemButtonFace'
                    del self.buttons_clicked[:]
                
                button['bg'] = 'green'
                self.buttons_clicked.append(button)

            if self.btn_name == 'RUN':
                self.buttons_clicked[0]['bg'] = 'SystemButtonFace'
        except:
            pass

    def __tool_tip(self):
        """ Creates a tool tip label """
        self.tip = Label(self.root, width = 0, height = 2, padx = 10, text = '', bg = 'green')
        self.tip['text'] = self.tips[self.btn_name]
        self.tip.pack()
        # initially hide the tool tip label off the screen at a -x position
        self.tip.place(x = -(self.tip_x_pos[self.btn_name]), \
                       y = self.tip_y_pos[self.btn_name])
        self.__animate()

    def __animate(self):
        """ Animates the width of a tool tip label """
        try:
            if self.tip['width'] == 0:
                self._animation = self.root.after(self.animation_delay, self.__animate)
            elif self.tip['width'] == 1:
                self.tip.place(x = self.tip_x_pos[self.btn_name])
                self._animation = self.root.after(self.animation_speed, self.__animate)
            elif self.tip['width'] <= 25:
                self._animation = self.root.after(self.animation_speed, self.__animate)
                
            self.tip['width'] += 1
        except:
            pass
