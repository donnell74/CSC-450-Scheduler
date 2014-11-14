from Tkinter import *
from guiConstraints import *
from toolTips import *
from readFile import *
import sys
sys.path.append("../")
import globs
from genetic import constraint, interface
import tkMessageBox

font_style = "Helvetica"
size_h1 = 20
size_h2 = 18
size_p = 14
size_l = 12


class HomePage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="CSC Department Scheduler", font=(font_style, size_h1))
        self.head_label.pack(pady=10)

        paragraph_text = "User Guide: step-by-step\n\n" +\
                         "1.) Click RUN to begin generating CSC schedules.\n\n" +\
                         "a.) OPTIONAL: Click the Constraint button to \ngenerate custom schedules.\n\n" +\
                         "2.) After the scheduling is finished click on the View \nbutton" +\
                         " to view the schedules.\n"
        self.description_label = Label(self, text=paragraph_text, font=(font_style, size_p))
        self.description_label.pack()

        runtime_option_text = "Choose a run speed:"
        self.runtime_label = Label(self, text = runtime_option_text, font = (font_style, size_p))
        self.runtime_label.pack()
        self.runtime_disclaimer = Label(self, text = "The scheduler may finish earlier"\
                                        " if it finds 5 valid schedules.", font = (font_style, 10))
        self.runtime_disclaimer.pack(pady = 5)

        runtime_modes = [
            ("Quick (~1 minute)", 1),
            ("Moderate (~10 minutes)", 10),
            ("High (~1 hour)", 60),
            ("Overnight (~8 hours)", 480),
            ("Custom", 0)
            ]

        self.runtime_selected_var = IntVar()
        self.runtime_selected_var.set(1)
        self.runtime_selected_var.trace("w", self.check_if_custom)

        for mode, val in runtime_modes:
            radio_btn = Radiobutton(self,
                                    text = mode,
                                    variable = self.runtime_selected_var,
                                    value = val,
                                    font = (font_style, size_l))
            radio_btn.pack(anchor = W, padx = 225)


        self.custom_input = Frame(self, width = 50, height = 20)
        self.input_label = Label(self.custom_input,
                                 text = "Insert a time (in minutes):",
                                 font = (font_style, size_l))
        self.input_label.pack()

        # Will be type-checked for Int's, but init as Str for simplicity
        self.runtime_custom_input_value = StringVar()
        self.runtime_custom_input_value.set("0")
        self.runtime_custom_input_value.trace("w", self.check_if_digit)

        self.custom_runtime_input_box = Entry(self.custom_input, textvariable = self.runtime_custom_input_value)
        self.custom_runtime_input_box.pack()

    def check_if_digit(self, *args):
        # disabled so tkMessageBox doesn't corrupt input field
        self.custom_runtime_input_box.config(state = DISABLED)
        entered_value = self.runtime_custom_input_value.get()
        for c in entered_value:
            if not c.isdigit():
                self.runtime_custom_input_value.set(entered_value[:-1]) # remove the non-digit character
                tkMessageBox.showerror(title = "Error", message = "Time must only contain numbers.")
                self.custom_runtime_input_box.config(state = NORMAL)
                return 0
        self.custom_runtime_input_box.config(state = NORMAL)
        return 1


    def check_if_custom(self, *args):
        runtime_var_value = self.runtime_selected_var.get()
        if runtime_var_value == 0:
            # custom is selected
            self.custom_input.pack()
        else:
            self.custom_input.pack_forget()

# Constraint page is located in guiConstraints.py

class ViewPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)

        self.head_label = Label(self,
                                text = "View Schedules",
                                font = (font_style, size_h2))
        self.head_label.pack()

        self.is_run_clicked = False
        # holds canvas object
        self.canvases = []
        self.drop_downs = []

        # button to allow user to toggle between old and new style of graphical schedules
        self.toggle_graphics_btn = Button(self,
                                      command = lambda : self.toggle_schedules(),
                                      text = 'Toggle Graphics',
                                      padx = 10,
                                      pady = 10,
                                      cursor = 'hand2')
        self.toggle_graphics_btn.place(x = 533, y = 47)

        self.last_viewed_schedule = 0
        self.toggle_schedules_flag = False

        # holds the rooms
        self.rooms = []

        # Current selection
        # Default to 0
        self.room_selection_option = 0
        # dict to hold selection option + room name/number
        self.selections = {}
        # Holds the labels for the schedules
        self.table_labels = []
        # Display schedules
        self.toggle_schedules()

    def toggle_schedules(self):
        """ Switch between the compact or graphical schedule """
        # delete previous canvases
        self.delete_objects(self.canvases)
        # delete old labels to make room for new ones
        self.delete_objects(self.table_labels)
        # delete drop downs
        self.delete_objects(self.drop_downs)
        # default is to display graphical schedules first
        if not self.toggle_schedules_flag:
            if self.is_run_clicked:
                self.toggle_schedules_flag = True
                self.create_graphical_schedules()
                self.insert_schedule(self.last_viewed_schedule)
            else:
                self.create_compact_schedules()
        else:
            if self.is_run_clicked:
                self.toggle_schedules_flag = False
            self.create_compact_schedules()

    def show_nav(self):
        """ Show buttons so user can click toggle between schedules """
        if self.is_run_clicked:
            self.create_buttons()
            self.place_buttons()

    def create_compact_schedules(self):
        """ Creates a more compact graphical schedule
            respresentation of the valid schedules """
        # background place holder for the schedules
        self.bg_label = Label(self,
                              width = 37,
                              height= 13,
                              font=(font_style, size_h1),
                              text = 'Click RUN to generate schedules.',
                              bg = 'white')
        self.bg_label.place(x = 50, y = 107)

        # initial color of the schedule labels
        self.color = [255, 255, 255]

        if self.is_run_clicked:
            self.insert_schedule(self.last_viewed_schedule)

    def create_room_selection(self):
        """ Creates a drop down menu for room selection """
        self.room_label = Label(self,
                                text = 'Room: ',
                                font = (font_style, size_p))
        self.room_label.place(x = 50, y = 10)

        self.room_selection_var = StringVar(self)
        self.room_selection_var.set(self.rooms[self.room_selection_option]) # default value

        self.select = apply(OptionMenu,
                            (self, self.room_selection_var) + tuple(self.rooms))
        self.select.place(x = 115, y = 5)
        self.room_selection_var.trace('w', lambda *args: self.get_selected(self.room_selection_var))

        self.drop_downs.append(self.select)
        self.drop_downs.append(self.room_label)

    def get_selected(self, room_selection_var):
        """ Updates the room when user selects
            an option from the the room drop down menu """

        room_value = room_selection_var.get()
        for i in xrange(len(self.selections)):
            if room_value in self.selections[i]:
                self.room_selection_option = i

        # update schedule
        self.insert_schedule(self.last_viewed_schedule)

    def create_graphical_schedules(self):
        """ Creates a graphical respresentation of the valid schedules """
        # delete previous canvas
        self.delete_objects(self.canvases)

        # create new canvas to hold the schedules
        self.canvas = Canvas(self, bg = 'white')
        self.canvas.config(scrollregion = (0, 0, 600, 1050))    
        self.canvas.pack(expand = TRUE,
                         fill = BOTH,
                         padx = 50,
                         pady = 70)

        # vertical scrollbar
        vert_scroll_bar = Scrollbar(self.canvas,
                                    orient = VERTICAL,
                                    command = self.canvas.yview)
        vert_scroll_bar.pack(side = RIGHT,
                             fill = Y)

        # horizontal scrollbar
        horiz_scroll_bar = Scrollbar(self.canvas,
                                     orient = HORIZONTAL,
                                     command = self.canvas.xview)
        horiz_scroll_bar.pack(side = BOTTOM,
                              fill = X)

        self.canvas.config(yscrollcommand = vert_scroll_bar.set,
                           xscrollcommand = horiz_scroll_bar.set)

        # keep track of canvas object so it can be deleted
        self.canvases.append(self.canvas)

        # listen for mouse wheel
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_mouse_wheel(self, event):
        """ Update the canvas vertical scrollbar """
        try:
            self.canvas.yview_scroll(-1 * (event.delta/120), "units")
        except:
            pass

    def create_buttons(self):
        """ Create / initialize the 5 view schedule buttons """

        # text for schedule buttons
        self.schedules = ['Schedule 1',
                          'Schedule 2',
                          'Schedule 3',
                          'Schedule 4',
                          'Schedule 5']

        self.schedule_btn_0 = Button(self, command = lambda n = 0: self.insert_schedule(0),
                                     text = self.schedules[0],
                                     padx = 10, pady = 10,
                                     cursor = 'hand2')

        self.schedule_btn_1 = Button(self, command = lambda n = 1: self.insert_schedule(1),
                                     text = self.schedules[1],
                                     padx = 10, pady = 10,
                                     cursor = 'hand2')

        self.schedule_btn_2 = Button(self, command = lambda n = 2: self.insert_schedule(2),
                                     text = self.schedules[2],
                                     padx = 10, pady = 10,
                                     cursor = 'hand2')

        self.schedule_btn_3 = Button(self, command = lambda n = 3: self.insert_schedule(3),
                                     text = self.schedules[3],
                                     padx = 10, pady = 10,
                                     cursor = 'hand2')

        self.schedule_btn_4 = Button(self, command = lambda n = 4: self.insert_schedule(4),
                                     text = self.schedules[4],
                                     padx = 10, pady = 10,
                                     cursor = 'hand2')

    def place_buttons(self):
        """ Place the View Schedule Buttons on the view page """

        # get valid weeks so we know how many view schedule buttons to show
        weeks = self.get_valid_weeks() - 1

        if 0 <= weeks:
            self.schedule_btn_0.pack()
            self.schedule_btn_0.place(x = 50, y = 47)
        else:
            self.delete_objects([self.schedule_btn_0])

        if 1 <= weeks:
            self.schedule_btn_1.pack()
            self.schedule_btn_1.place(x = 138, y = 47)
        else:
            self.delete_objects([self.schedule_btn_1])

        if 2 <= weeks:
            self.schedule_btn_2.pack()
            self.schedule_btn_2.place(x = 226, y = 47)
        else:
            self.delete_objects([self.schedule_btn_2])

        if 3 <= weeks:
            self.schedule_btn_3.pack()
            self.schedule_btn_3.place(x = 314, y = 47)
        else:
            self.delete_objects([self.schedule_btn_3])

        if 4 <= weeks:
            self.schedule_btn_4.pack()
            self.schedule_btn_4.place(x = 402, y = 47)
        else:
            self.delete_objects([self.schedule_btn_4])

    def get_valid_weeks(self):
        """ Returns the number of valid weeks that were generated """

        weeks = 0
        for week in globs.mainScheduler.weeks:
            if week.valid:
                weeks += 1

        return weeks

    def insert_schedule(self, n):
        """ Inserts schedule n into the textarea/scrollbox of the View page """

        self.last_viewed_schedule = n

        # delete drop downs
        self.delete_objects(self.drop_downs)

        # format the schedules
        if not self.toggle_schedules_flag:
            self.create_graphical_schedules()
            self.format_graphical_schedule(globs.mainScheduler.weeks[n].print_concise())
            self.bg_label['fg'] = 'white'

        else:
            # destroy old labels to make room for new ones
            self.delete_objects(self.table_labels)

            # hide bg_label text
            self.bg_label['fg'] = 'white'

            self.format_compact_schedule(globs.mainScheduler.weeks[n].print_concise())

    def format_graphical_schedule(self, schedule_text):
        """ Formats the graphical schedules """

        xstart = 19
        ystart = 6
        xpad = xstart + 20
        ypad = ystart + 10

        days = ['Mon.',
                'Tue.',
                'Wed.',
                'Thu.',
                'Fri.']

        xpos_days = {'Monday' : xpad + 80 + (0 * 100),
                     'Tuesday' : xpad + 80 + (1 * 100),
                     'Wednesday' : xpad + 80 + (2 * 100),
                     'Thursday' : xpad + 80 + (3 * 100),
                     'Friday' : xpad + 80 + (4 * 100)}

        times = ['8am', '9am', '10am', '11am',
                 '12pm', '1pm', '2pm', '3pm', '4pm', '5pm']

        ypos_times = {8 : ypad + 50 + (0 * 100),
                      9 : ypad + 50 + (1 * 100),
                      10 : ypad + 50 + (2 * 100),
                      11 : ypad + 50 + (3 * 100),
                      12 : ypad + 50 + (4 * 100),
                      13 : ypad + 50 + (5 * 100),
                      14 : ypad + 50 + (6 * 100),
                      15 : ypad + 50 + (7 * 100),
                      16 : ypad + 50 + (8 * 100),
                      17 : ypad + 50 + (9 * 100)}

        schedule_text = schedule_text.split('\n')

        instructor = ''
        # Empty previous rooms
        del self.rooms[:]
        # empty selections
        self.selections.clear()

        # incremet option count when a room is added to drop down
        option = 0
        # populate self.rooms for drop down selection
        for i in xrange(len(schedule_text) - 1):

            if (' ' in schedule_text[i]) and len(schedule_text[i]) > 0:
                temp = schedule_text[i].split(' ')

                # len(temp) < 7, then course does
                # not have a section code; e.g. 001, 002, etc.
                if len(temp) < 7:
                    # prevent duplicate room entry into drop down
                    if not (temp[3] + " " + temp[4] in self.rooms):
                        self.rooms.append(temp[3] + " " + temp[4])
                        self.selections[option] = temp[3] + " " + temp[4]

                        option += 1
                else:
                    # prevent duplicate room entry into drop down
                    if not (temp[4] + " " + temp[5] in self.rooms):
                        self.rooms.append(temp[4] + " " + temp[5])
                        self.selections[option] = temp[4] + " " + temp[5]

                        option += 1

        option = 0 # reset

        # populate graphical schedule with course data
        for i in xrange(len(schedule_text) - 1):

            txt = ''                # holds the course data
            schedule_days = ''      # holds the course days
            schedule_time = ''      # holds the course start time

            if not (' ' in schedule_text[i]) and len(schedule_text[i]) > 0:
                # get instructor name
                instructor = schedule_text[i]
            else:
                temp = schedule_text[i].split(' ')
                course_info = ''

                # len(temp) < 7, then course does not have a section (001, 002, etc.)
                if len(temp) < 7:
                    if temp[3] + " " + temp[4] in self.rooms[self.room_selection_option]:
                        schedule_days = temp[2]
                        schedule_time = temp[5].split('-')[0]
                        start_time = temp[5].split('-')[0]
                        end_time = temp[5].split('-')[1]

                        # output string with course info
                        course_info += temp[0] + \
                                       ' ' + temp[1] + \
                                       '\n' + temp[5]

                # course has a section number (001, 002, etc.)
                else:
                    if temp[4] + " " + temp[5] in self.rooms[self.room_selection_option]:
                        schedule_days = temp[3]
                        schedule_time = temp[6].split('-')[0]
                        start_time = temp[6].split('-')[0]
                        end_time = temp[6].split('-')[1]

                        # output string with course info
                        course_info += temp[0] + \
                                       ' ' + temp[1] + \
                                       '\n' + 'Sec. ' + temp[2] + \
                                       '\n' + temp[6]

                # txt is the text value in canv.create_text       
                txt = instructor + '\n' + course_info

                for day in schedule_days:

                    # Monday
                    if day.lower() == 'm':
                        self.canvas.create_text(xpos_days['Monday'],
                                                ypos_times[int(schedule_time.split(':')[0])],
                                                text = txt,
                                                width = 100,
                                                font = (font_style, size_l))
                    # Tuesday
                    elif day.lower() == 't':
                        self.canvas.create_text(xpos_days['Tuesday'],
                                                ypos_times[int(schedule_time.split(':')[0])],
                                                text = txt,
                                                width = 100,
                                                font = (font_style, size_l))
                    # Wednesday
                    elif day.lower() == 'w':
                        self.canvas.create_text(xpos_days['Wednesday'],
                                                ypos_times[int(schedule_time.split(':')[0])],
                                                text = txt,
                                                width = 100,
                                                font = (font_style, size_l))
                    # Thursday
                    elif day.lower() == 'r':
                        self.canvas.create_text(xpos_days['Thursday'],
                                                ypos_times[int(schedule_time.split(':')[0])],
                                                text = txt,
                                                width = 100,
                                                font = (font_style, size_l))
                    # Friday
                    elif day.lower() == 'f':
                        self.canvas.create_text(xpos_days['Friday'],
                                                ypos_times[int(schedule_time.split(':')[0])],
                                                text = txt,
                                                width = 100,
                                                font = (font_style, size_l))

        # background for the days of the week
        self.canvas.create_rectangle(0, 0, 1050, 30, fill = 'cyan', outline = '')

        # draw days of the week across the x-axis of the canvas
        self.canvas.create_text(xpad + 55,
                                ypad,
                                text = days[0],
                                font = (font_style, size_l))
        self.canvas.create_text(xpad + 54 + 100,
                                ypad,
                                text = days[1],
                                font = (font_style, size_l))
        self.canvas.create_text(xpad + 57 + 200,
                                ypad,
                                text = days[2],
                                font = (font_style, size_l))
        self.canvas.create_text(xpad + 53 + 300,
                                ypad,
                                text = days[3],
                                font = (font_style, size_l))
        self.canvas.create_text(xpad + 48 + 400,
                                ypad,
                                text = days[4],
                                font = (font_style, size_l))

        # draw AM times down the y-axis of the canvas
        for i in xrange(len(times)):
            self.canvas.create_text(xstart + xpad - 25,
                                    ystart + ypad + 40 + (i * 100),
                                    text = times[i],
                                    font = (font_style, size_l))

        if self.is_run_clicked:
            self.create_room_selection()

        # reset
        self.room_selection_option = 0

    def format_compact_schedule(self, schedule_text):
        """ Formats the compact schedules """

        schedule_text = schedule_text.split('\n')

        for i in xrange(len(schedule_text) - 1):
            # teacher labels
            if not (' ' in schedule_text[i]) and len(schedule_text[i]) > 0:
                self.table_labels.append(Label(self, text = schedule_text[i],
                                               font = (font_style, size_l),
                                               width = 66,
                                               bg = 'black',
                                               fg = 'white',
                                               anchor = NW))
            else:   # course info labels
                self.table_labels.append(Label(self, text = schedule_text[i],
                                               font=(font_style, size_l),
                                               width = 66,
                                               bg = 'white',
                                               fg = 'black',
                                               anchor = NW))
        # position the labels
        yt = 103
        for i in xrange(len(self.table_labels)):
            self.table_labels[i].place(x = 50, y = yt)
            yt += 24

        # Set color to white for fade in
        self.color = [255, 255, 255]
        for i in xrange(len(self.table_labels)):
            # Begin fade-in animation
            self.fade_in(i)

    def delete_objects(self, objects):
        """ Delete dynamically created objects from memory """

        for i in xrange(len(objects)):
            objects[i].destroy()     # destroy old labels

        del objects[:]

    def fade_in(self, n):
        """ Fades a schedule in from white to a certain color """

        animation_speed = 50

        # convert rgb values to hex values
        color = ""  # holds the hex string
        for i in xrange(3):
            if i == 0:
                color += "#%02x" % self.color[i]
            else:
                color += ("#%02x" % self.color[i]).strip('#')

        # update rgb values
        for i in xrange(3):
            if (self.color[0] >= 0):
                self.color[i] -= 1
            else:
                return # stop recursive fade_in animation

        if len(self.table_labels[n]['text'].split(' ')) == 1:
            self.table_labels[n].configure(bg = color)
        else:
            self.table_labels[n].configure(fg = color)

        self.table_labels[n].after(animation_speed, self.fade_in, n)


class MiscPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self,
                                text="Misc Page",
                                font =(font_style, size_h2))
        self.head_label.pack()

class MainWindow(Frame):

    def __init__(self, root):
        globs.init()
        Frame.__init__(self, root)
        self.pack(side = TOP, fill = "both")

        if sys.platform.startswith('win'):
            ToolTips(root)

        # MENU AND CONTENT SECTIONS
        self.menu_frame = Frame(self,
                          width="500",
                          height="600")
        self.menu_frame.pack(side=LEFT, fill="both")

        self.content_container = Frame(self,
                                       width="800",
                                       height="600")
        self.content_container.pack(side=LEFT, fill="both")

        # MENU BUTTONS
        self.home_btn = Button(self.menu_frame,
                               text='Home',
                               command=self.show_home,
                               width="10",
                               height="3",
                               font=(font_style, size_h2),
                               cursor='hand2')
        self.home_btn.pack(fill=X, side="top", pady=2)

        self.constraint_btn = Button(self.menu_frame,
                                     text='Constraint',
                                     command=self.show_constraint,
                                     width="10",
                                     height="3",
                                     font=(font_style, size_h2),
                                     cursor='hand2')
        self.constraint_btn.pack(fill=X, side="top", pady=2)

        self.view_btn = Button(self.menu_frame,
                               text='View',
                               command=self.show_view,
                               width="10",
                               height="3",
                               font=(font_style, size_h2),
                               cursor='hand2')
        self.view_btn.pack(fill=X, side="top", pady=2)

        self.misc_btn = Button(self.menu_frame,
                               text='Misc',
                               command=self.show_misc,
                               width="10",
                               height="3",
                               font=(font_style, size_h2),
                               cursor='hand2')
        self.misc_btn.pack(fill=X, side="top", pady=2)

        self.run_btn = Button(self.menu_frame,
                              text='RUN',
                              bg='green',
                              command=self.run_scheduler,
                              width="10",
                              height="3",
                              font=(font_style, size_h2),
                              cursor='hand2')
        self.run_btn.pack(fill = X, side = "top", pady=2)

        # PAGES
        self.home_page = HomePage(self.content_container)
        self.home_page.place(in_=self.content_container,
                             x=0,
                             y=0,
                             relwidth=1,
                             relheight=1)

        self.constraint_page = ConstraintPage(root=self.content_container,
                                              constraints=globs.mainScheduler.constraints)
        self.constraint_page.place(in_=self.content_container,
                                   x=0,
                                   y=0,
                                   relwidth=1,
                                   relheight=1)

        self.view_page = ViewPage(self.content_container)
        self.view_page.place(in_=self.content_container,
                             x=0,
                             y=0,
                             relwidth=1,
                             relheight=1)

        self.misc_page = MiscPage(self.content_container)
        self.misc_page.place(in_=self.content_container,
                             x=0,
                             y=0,
                             relwidth=1,
                             relheight=1)

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
        instructors = globs.instructors
        # RUN SCHEDULER METHOD
        # Add hard/obvious constraints before running
        globs.mainScheduler.add_constraint("instructor conflict",
                                           0,
                                           constraint.instructor_conflict,
                                           [instructors])
        globs.mainScheduler.add_constraint("sequential_time_different_building_conflict",
                                           0,
                                           constraint.sequential_time_different_building_conflict,
                                           [instructors])
        globs.mainScheduler.add_constraint("subsequent courses",
                                           0,
                                           constraint.num_subsequent_courses,
                                           [instructors])
        globs.mainScheduler.add_constraint("capacity checking",
                                           0,
                                           constraint.ensure_course_room_capacity,
                                           [])
        globs.mainScheduler.add_constraint("no overlapping courses",
                                           0,
                                           constraint.no_overlapping_courses,
                                           [])
        globs.mainScheduler.add_constraint("computer requirement",
                                           0,
                                           constraint.ensure_computer_requirement,
                                           [])
        globs.mainScheduler.add_constraint("course sections at different times",
                                           0,
                                           constraint.course_sections_at_different_times,
                                           [globs.courses[:-1]])  # the last item is "All", ignore it

        runtime_var_choice = self.home_page.runtime_selected_var.get()
        if runtime_var_choice not in [1, 10, 60, 480]:
            # Ensure choice is Int
            runtime_var_choice = int(self.home_page.runtime_custom_input_value.get())
            if runtime_var_choice < 1:
                runtime_var_choice = 1
            print(runtime_var_choice)

        for each_course in globs.mainScheduler.courses:
            if each_course.is_lab:
                globs.mainScheduler.add_constraint("lab on tr: " + each_course.code,
                                                   0,
                                                   constraint.lab_on_tr,
                                                   [each_course])

        globs.mainScheduler.evolution_loop(runtime_var_choice)

        interface.export_schedules(globs.mainScheduler.weeks)
        self.view_page.is_run_clicked = True
        self.view_page.show_nav()
        self.view_page.insert_schedule(0)  # show the first schedule in the view page
        # DISPLAY VIEW PAGE
        self.view_page.lift()
        return
