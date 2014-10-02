from Tkinter import *

class Page(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

    def show(self):
        self.lift()

class HomePage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text = "Home Page")
        self.head_label.pack(side = "bottom")


class ConstraintPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text = "Constraint Page")
        self.head_label.pack()

class ViewPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text = "View Page")
        self.head_label.pack()

class MiscPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text = "Misc Page")
        self.head_label.pack()

class MainWindow(Frame):

    def __init__(self, root):
        Frame.__init__(self, root)

        # MENU AND CONTENT SECTIONS
        self.menu = Frame(self)
        self.menu.grid(row = 0, column = 0)
        #self.menu.pack(side = 'left', fill = 'y')

        self.content_container = Frame(self)
        self.content_container.grid(row = 1, column = 0)
        #self.content_container.pack(fill = 'both')

        # MENU BUTTONS
        self.home_btn = Button(self.menu, text = 'Home', command = self.show_home)
        self.home_btn.pack(side = "left")
        
        self.constraint_btn = Button(self.menu, text = 'Constraint', command = self.show_constraint)
        self.constraint_btn.pack(side = "left")
        
        self.view_btn = Button(self.menu, text = 'View', command = self.show_view)
        self.view_btn.pack(side = "left")
        
        self.misc_btn = Button(self.menu, text = 'Misc', command = self.show_misc)
        self.misc_btn.pack(side = "left")
        
        self.run_btn = Button(self.menu, text = 'RUN', bg = 'green', command = self.run_scheduler)
        self.run_btn.pack(side = "left")

        # PAGES
        self.home_page = HomePage(self.content_container)
        self.home_page.place(in_=self.content_container, x = 0, y = 0, relwidth = 1, relheight = 1)
        
        self.constraint_page = ConstraintPage(self.content_container)
        self.constraint_page.place(in_=self.content_container, x = 0, y = 0, relwidth = 1, relheight = 1)
        
        self.view_page = ViewPage(self.content_container)
        self.view_page.place(in_=self.content_container, x = 0, y = 0, relwidth = 1, relheight = 1)
        
        self.misc_page = MiscPage(self.content_container)
        self.misc_page.place(in_=self.content_container, x = 0, y = 0, relwidth = 1, relheight = 1)

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
        return
