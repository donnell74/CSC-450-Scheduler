import sys
from Tkinter import *
from guiClasses import *

# Functions for placing content
def load_base_content():
    content_frame = Frame(main_window)
    content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)

    top_label = Label(content_frame, textvariable = top_label_text)
    top_label.pack(side = TOP)
    return content_frame

def clear_content():
    content_frame.destroy()
    new_frame = Frame(main_window)
    new_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)
    #content_frame.pack_forget()
    #content_frame.grid_forget()
    return

def place_home_screen():
    content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)
    top_label_text.set("Home Screen")
    top_label.pack()
    return

def place_constraint_screen():
    content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)
    top_label_text.set("Constraint Screen")
    top_label.pack()
    add_course_con_btn.pack(side = LEFT, padx = 2, pady = 2)
    add_instructor_con_btn.pack(side = LEFT, padx = 5, pady = 2)
    return

def place_view_screen():
    content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)
    top_label_text.set("View Screen")
    top_label.pack()
    return

def place_misc_screen():
    content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)
    top_label_text.set("Misc Screen")
    top_label.pack()
    return

def run_scheduler():
    content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)
    top_label_text.set("Scheduler should be running...")
    top_label.pack()
    return


# Define click functions
def click_home():
    temp_frame = clear_content()
    content_frame = load_base_content()
    place_home_screen()
    return

def click_constraint():
    clear_content()
    place_constraint_screen()
    return

def click_view():
    clear_content()
    place_view_screen()
    return

def click_misc():
    clear_content()
    place_misc_screen()
    return

def click_run():
    # run the scheduler
    run_scheduler()
    return

def add_course_con():
    return

def add_instructor_con():
    return


main_window = Tk()

window_width = 850
window_height = 600
screen_x_pos = (main_window.winfo_screenwidth() / 2) - (window_width / 2)
screen_y_pos = (main_window.winfo_screenheight() / 2) - (window_height / 2)

main_window.geometry(str(window_width) + 'x' + str(window_height) +\
                    '+' + str(screen_x_pos) + '+' + str(screen_y_pos))

# Next two lines are using guiClasses.py and TopLevel for sub-windows
##main = MainWindow(main_window)
##main.pack()

# Following section places everything on one windowFO301028

main_window.title('CSC Scheduler')

top_label_text = StringVar()
top_label_text.set("You have just begun!")

# MENU SECTION
menu_frame = Frame(main_window, bg = 'red')
menu_frame.grid(row = 0, column = 0, rowspan = 6, columnspan = 2)

# MENU btnS
home_btn = Button(menu_frame, text = "Home", width = 15, height = 5, command = click_home)
home_btn.pack()

constraint_btn = Button(menu_frame, text = "Constraint", width = 15, height = 5, command = click_constraint)
constraint_btn.pack()

view_btn = Button(menu_frame, text = "View", width = 15, height = 5, command = click_view)
view_btn.pack()

misc_btn = Button(menu_frame, text = "...", width = 15, height = 5, command = click_misc)
misc_btn.pack()

run_btn = Button(menu_frame, text = "RUN", width = 15, height = 10, bg = "green", command = click_run)
run_btn.pack()


# CONTENT SECTION
##content_frame = Frame(main_window)
##content_frame.grid(row = 0, column = 2, rowspan = 6, columnspan = 5)
##
##top_label = Label(content_frame, textvariable = top_label_text)
##top_label.pack(side = TOP)
content_frame = load_base_content()

# CONSTRAINT SCREEN STUFF
add_course_con_btn = Button(content_frame, text = "add course constraint", width =15, height =5, command = add_course_con)
add_instructor_con_btn = Button(content_frame, text = "add instructor constraint", width =15, height =5, command = add_instructor_con )



main_window.mainloop()   # NEED FOR MAC OSX AND WINDOWS

