from Tkinter import *
from guiConstraints import *
from toolTips import *
from readFile import *

font_style = "Helvetica"
size_h1 = 20
size_h2 = 18
size_p = 14

class Page(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

    def show(self):
        self.lift()

class HomePage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="CSC-450-Scheduler", font=(font_style, size_h1))
        self.head_label.pack(pady=10)

        paragraph_text = "User Guide: step-by-step\n\n" +\
                         "1.) Click RUN to begin generating CSC schedules.\n\n" +\
                         "a.) OPTIONAL: Click the Constraint button to \ngenerate custom schedules.\n\n" +\
                         "2.) After the scheduling is finished click on the View \nbutton" +\
                         " to view the schedules.\n"
        self.description_label = Label(self, text=paragraph_text, font=(font_style, size_p))
        self.description_label.pack()

        self.version_label = Label(self, text="<version info?>")
        self.version_label.pack(side=BOTTOM, pady=5)


# class ConstraintPage(Page):
# 
#     def __init__(self, root):
#         Frame.__init__(self, root)
#         self.head_label = Label(self, text="Constraint Page")
#         self.head_label.pack()




        paragraph_text = "This is constraint"
        self.description_label = Label(self, text=paragraph_text, font=(font_style, size_p))
        self.description_label.pack()

        

        self.menu = Frame(self, background ="bisque", width="500", height="600")
        self.menu.pack(side="top", fill="both", expand=True)

        self.top_frame= Frame(self.menu, background="green")
        self.bottom_frame =Frame(self.menu, background="yellow")
        self.top_frame.pack(side="top", fill="x", expand=False)
        self.bottom_frame.pack(side="bottom", fill="both", expand=True)

##        self.top_left =Frame(self.menu, text="Top Left")
##        self.top_right =Frame(self.menu, text="Top Right")
        self.top_left =Frame(self.menu, background ="pink")
        self.top_right =Frame(self.menu, background="blue")
        self.top_left.pack(side="left", fill="x", expand =True)
        self.top_right.pack(side="right", fill="x", expand=True)

        self.top_left_label = Label(self.top_left, text="Top Left")
        self.top_right_label = Label(self.top_right, text="Top Right")
        self.top_left_label.pack(side="left")
        self.top_right_label.pack(side = "right")

        self.text_box =Text(self.bottom_frame, height=10, width=50, background="grey")
        self.text_box.pack(side="top", fill="both", expand=True)
        

        self.add_con_btn = Button(self.menu, text="add course constraint", width="20", height="5")
        self.add_con_btn.pack(fill =X, side="left", pady=50, padx=50)

        self.add_instructor_btn = Button(self.menu, text="add instructor constraint", width="20", height="5")
        self.add_instructor_btn.pack(fill =X, side="right", pady=50, padx=50)

        

class ViewPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="View Page")
        self.head_label.pack()

        self.output_text = StringVar()  # make variable, set text later
        
        self.output_label = Label(self, textvariable=self.output_text)
        self.output_label.pack()

        text = ''
        num_of_schedules_to_read = 5
        error_messages = '\n\n\n'
        for i in xrange(1, num_of_schedules_to_read + 1):
            file_name = 'genetic/schedule_' + str(i) + '.csv'
            try:
                text += readOutputCSV(file_name)
                text += '\n   ========================================='
            except:
                error_messages += 'Error trying to read: ' + file_name + '\n'
            
        self.output_text.set(text + error_messages)
        

class MiscPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="Misc Page")
        self.head_label.pack()

class MainWindow(Frame):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.pack(side = TOP, fill = "both")

        ToolTips(root)
        
        # MENU AND CONTENT SECTIONS
        self.menu = Frame(self, width="500", height="600")
        self.menu.pack(side=LEFT, fill="both")

        self.content_container = Frame(self, width="800", height="600")
        self.content_container.pack(side=LEFT, fill="both")

        # MENU BUTTONS
        self.home_btn = Button(self.menu, text='Home', command=self.show_home, \
                               width="10", height="3", font=(font_style, size_h2), cursor = 'hand2') # specified in characters?
        self.home_btn.pack(fill=X, side="top", pady=2)
        
        self.constraint_btn = Button(self.menu, text='Constraint', command=self.show_constraint, \
                               width="10", height="3", font=(font_style, size_h2), cursor = 'hand2')
        self.constraint_btn.pack(fill=X, side="top", pady=2)
        
        self.view_btn = Button(self.menu, text='View', command=self.show_view, \
                               width="10", height="3", font=(font_style, size_h2), cursor = 'hand2')
        self.view_btn.pack(fill=X, side="top", pady=2)
        
        self.misc_btn = Button(self.menu, text='Misc', command=self.show_misc, \
                               width="10", height="3", font=(font_style, size_h2), cursor = 'hand2')
        self.misc_btn.pack(fill=X, side="top", pady=2)
        
        self.run_btn = Button(self.menu, text='RUN', bg='green', command=self.run_scheduler, \
                               width="10", height="3", font=(font_style, size_h2), cursor = 'hand2')
        self.run_btn.pack(fill = X, side = "top", pady=2)

        # PAGES
        self.home_page = HomePage(self.content_container)
        self.home_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        
        self.constraint_page = ConstraintPage(self.content_container)
        self.constraint_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        
        self.view_page = ViewPage(self.content_container)
        self.view_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)
        
        self.misc_page = MiscPage(self.content_container)
        self.misc_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)

        # INITIALIZE WITH HOME PAGE
        self.home_page.lift()
        
    def show_home(self):
        self.home_page.lift()

    def show_constraint(self):
        self.constraint_page.lift()

    def show_view(self):
        self.view_page.lift()

    def show_misc(self):
        self.misc_page.lift()

    def run_scheduler(self):
        # RUN SCHEDULER METHOD
        # DISPLAY VIEW PAGE
        self.view_page.lift()
        return

