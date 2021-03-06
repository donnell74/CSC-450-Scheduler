from __future__ import print_function
# reorganize!
from Tkinter import *
from guiConstraints import *
from toolTips import *
from readFile import *
import sys
sys.path.append("../")
import globs
from threading import Thread
from time import time
from genetic import constraint, interface
import tkMessageBox

font_style = "Helvetica"
size_h1 = 20
size_h2 = 18
size_p = 14
size_l = 12

class Page(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)

    def show(self):
        self.lift()

class HomePage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="CSC Department Scheduler", font=(font_style, size_h1))
        self.head_label.pack(pady = (20, 10))

        semester_info = "Semester to schedule: {0} {1}".format(globs.semester_to_schedule[0],
                                                               globs.semester_to_schedule[1])
        self.semester_label = Label(self, text = semester_info, font = (font_style, size_p))
        self.semester_label.pack()

        semester_additional_info = "(If this is incorrect, please specify in the override file.)"
        self.semester_additional_label = Label(self, text = semester_additional_info, font = (font_style, size_l))
        self.semester_additional_label.pack(pady = (0, 15))

        
        guide_title_text = "User Guide: step-by-step"
        paragraph_text = "1.) Click RUN to begin generating CSC schedules.\n\n" +\
                         "a.) OPTIONAL: Click the Constraint button to \ngenerate custom schedules.\n\n" +\
                         "2.) After the scheduling is finished click on the View \nbutton" +\
                         " to view the schedules."
        self.guide_title_heading = Label(self, text = guide_title_text, font = (font_style, size_p))
        self.guide_title_heading.pack(pady = (0, 5))
        self.description_label = Label(self, text = paragraph_text, font = (font_style, size_l))
        self.description_label.pack(pady = (0, 15))


        runtime_option_text = "Choose a run speed:"
        self.runtime_label = Label(self, text = runtime_option_text, font = (font_style, size_p))
        self.runtime_label.pack()
        self.runtime_disclaimer = Label(self, text = "The scheduler may finish earlier"\
                                        " if it finds 5 valid schedules.", font = (font_style, 10))
        self.runtime_disclaimer.pack(pady = (0, 5))

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
            b = Radiobutton(self, text = mode, variable = self.runtime_selected_var,
                            value = val, font = (font_style, size_l))
            b.pack(anchor = W, padx = 225)

        self.custom_input = Frame(self, width = 50, height = 20)
        self.input_label = Label(self.custom_input, text = "Insert a time (in minutes):",
                                 font = (font_style, size_l))
        self.input_label.pack()

        self.runtime_custom_input = StringVar() #will be converted to int later, prevents type errors
        self.runtime_custom_input.set("5")
        self.runtime_custom_input.trace("w", self.check_if_digit)

        self.input_box = Entry(self.custom_input, textvariable = self.runtime_custom_input)
        self.input_box.pack()
        # self.custom_input.pack() # uncomment to show this by default


    def check_if_digit(self, *args):
        self.input_box.config(state = DISABLED) # disabled so tkMessageBox doesn't corrupt input field
        entered_value = self.runtime_custom_input.get()
        for c in entered_value:
            if not c.isdigit():
                self.runtime_custom_input.set(entered_value[:-1]) # remove the non-digit character
                tkMessageBox.showerror(title = "Error", message = "Time must only contain numbers.")
                self.input_box.config(state = NORMAL)
                return 0
        self.input_box.config(state = NORMAL)
        return 1


    def check_if_custom(self, *args):
        runtime_var_value = self.runtime_selected_var.get()
        if runtime_var_value == 0: # custom is selected
            self.custom_input.pack()
        else:
            self.custom_input.pack_forget()

# Constraint page is located in guiConstraints.py
class ViewPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)

        head_text = "Schedules for {0} {1}".format(globs.semester_to_schedule[0],
                                                   globs.semester_to_schedule[1])
        self.head_label = Label(self, text = head_text,
                                font = (font_style, size_h2))
        self.head_label.pack(pady = (10, 0))

        self.is_run_clicked = False
        self.cached_constraints = None
        self.cache_flag = True

        # holds the room names that are in the drop down selection
        self.drop_down_items = []
        # holds canvas items
        self.canvas_items = []

        self.last_viewed_schedule = 0
        self.toggle_schedules_flag = False

        self.canvas_created = False

        self.toggle_constraint_acceptance_flag = True
        # holds the rooms
        self.rooms = []

        # current selection
        self.room_selection_option = 0  # default to 0
        # dict to hold selection option + room name/number
        self.selections = {}

        self.table_labels = []  # holds the labels for the schedules

        # dict to hold constraints and fitness score
        self.constraint_bag = {}

        # display schedules
        self.toggle_schedules()


    def create_display_toggle_buttons(self):
        """Creates the buttons for toggling views"""
        # button to allow user to toggle between old and new style of graphical schedules
        self.toggle_graphics = Button(self,
                                      command = lambda : self.toggle_schedules(),
                                      text = 'Toggle View',
                                      padx = 28, pady = 5,
                                      cursor = 'hand2')

        #button to show if constraints were accepted or rejected
        self.constraint_acceptance = Button(self,
                                            command = lambda : self.toggle_constraint_acceptance(),
                                            text = 'Toggle Constraints',
                                            padx = 10, pady = 10,
                                            cursor = 'hand2')


    def place_display_toggle_buttons(self):
        """Places the toggle constraint view button and the toggle view button in the viewpage"""
        self.constraint_acceptance.place(x = 519, y = 47)
        self.toggle_graphics.place(x = 518, y = 10)


    def hide_nav(self):
        """Removes all buttons from the view page; undoes show_nav"""
        attributes = ['constraint_acceptance', 'toggle_graphics', 'drop_down_items', 's0', 's1',
        's2', 's3', 's4']
        for each_attribute in attributes:
            if hasattr(self, each_attribute):
                if isinstance(getattr(self, each_attribute), list):
                    for each_sub_attr in getattr(self, each_attribute):
                        each_sub_attr.destroy()
                else:
                    getattr(self, each_attribute).destroy()


    def toggle_schedules(self):
        """ Switch between the compact or graphical schedule """

        # delete drop downs
        self.delete(self.drop_down_items)

        # delete previous canvas
        #self.delete(self.canvas_items)

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

    def toggle_constraint_acceptance(self):
        """ Switch between the acceptance and rejected constraints """

        if self.canvas_created:

            # delete old labels to make room for new ones
            self.delete(self.table_labels)

            # delete drop downs
            self.delete(self.drop_down_items)

            # default is to display accepted constraints first
            if not self.toggle_constraint_acceptance_flag:

                if self.is_run_clicked:
                    self.toggle_constraint_acceptance_flag = True
                    #self.create_graphical_constraints()
                    #self.insert_schedule(self.last_viewed_schedule)
                    self.canv.delete(ALL)
                    self.create_compact_schedules()
            else:
                if self.is_run_clicked:
                    self.toggle_constraint_acceptance_flag = True

                # delete previous canvas
                self.canv.delete(ALL)

                self.create_compact_constraint()

    def show_nav(self):
        """ show buttons so user can click toggle between schedules """

        if self.is_run_clicked:
            self.create_buttons()
            self.place_buttons()
            self.create_display_toggle_buttons()
            self.place_display_toggle_buttons()

    def create_compact_schedules(self, none_to_show = False):
        """ Creates a more compact graphical schedule
            respresentation of the valid schedules """

        if none_to_show:
            text_to_show = 'No valid schedules were generated within the time limit.\n' +\
                'You may try running again, but if the problem persists, please consider\n' + \
                'trying one of the following solutions:\n\n' + \
                '1. Increase the maximum runtime on the main screen\n' + \
                '2. Decrease the number of mandatory constraints\n' + \
                '3. Increase the number of time slots and/or rooms (or decrease the number\n' + \
                'of courses) in the input\n' + \
                '4. Ensure that no two mandatory constraints conflict such that they cannot\n' + \
                'both be fulfilled at the same time'
            size_to_show = 12
            width_to_show = 66
            height_to_show = 23
            if hasattr(self, 'bg_label'):
                self.bg_label.destroy()
            self.hide_nav()

            if hasattr(self, 'canv'):
                self.canv.destroy()
                self.canvas_created = False
        else:
            text_to_show = 'Click RUN to generate schedules.'
            size_to_show = size_h1
            width_to_show = 37
            height_to_show = 13
        # background place holder for the schedules
        self.bg_label = Label(self, width = width_to_show, height = height_to_show,
                              font=(font_style, size_to_show),
                              text = text_to_show,
                              bg = 'white')
        self.bg_label.place(x = 50, y = 107)

        if self.is_run_clicked and not none_to_show:
            self.bg_label.destroy()
            self.insert_schedule(self.last_viewed_schedule)

    def create_compact_constraint(self):
        """ Creates a more compact graphical schedule
            respresentation of the valid schedules """

        # background place holder for the schedules
        """self.bg_label = Label(self, width = 37, height= 13,
                              font=(font_style, size_h1),
                              text = 'Click RUN to generate schedules.',
                              bg = 'white')
        self.bg_label.place(x = 50, y = 107)"""

        # initial color of the schedule labels
        #self.color = [255, 255, 255]
        self.delete([self.bg_label])
        if self.is_run_clicked:
            self.insert_constraint(self.last_viewed_schedule)

    def create_room_selection(self):
        """ Creates a drop down menu for room selection """

        self.room_label = Label(self, text = 'Room: ',
                            font = (font_style, 10))
        self.room_label.place(x = 47, y = 18)

        self.selected_option = StringVar(self)
        self.selected_option.set(self.rooms[self.room_selection_option]) # default value

        self.menu_select = apply(OptionMenu,
                            (self, self.selected_option) + tuple(self.rooms))
        self.menu_select.place(x = 94, y = 10)

        self.selected_option.trace('w', lambda *args: self.get_selected(self.selected_option))

        self.drop_down_items.append(self.menu_select)
        self.drop_down_items.append(self.room_label)

    def get_selected(self, selected):
        """ Updates the room when user selects
            an option from the the room drop down menu """

        option = selected.get()
        for i in xrange(len(self.selections)):

            if option in self.selections[i]:
                self.room_selection_option = i

        # update schedule
        self.insert_schedule(self.last_viewed_schedule)

    def sort_selections(self):
        """ Sorts self.selections """

        # sort selections
        sorted_selections = []
        for key in self.selections:
            sorted_selections.append(self.selections[key])

        self.selections = {}
        sorted_selections.sort()

        key = 0
        for room in sorted_selections:
            self.selections[key] = room
            key += 1

    def create_graphical_schedules(self):
        """ Creates a graphical respresentation of the valid schedules """

        if not self.canvas_created:
            # create new canvas to hold the schedules
            self.canv = Canvas(self, bg = 'white')
            self.canv.config(scrollregion = (0, 0, 600, 1050))
            self.canv.pack(expand = TRUE,
                           fill = BOTH,
                           padx = 50,
                           pady = 70)

            # vertical scrollbar
            vbar = Scrollbar(self.canv,
                             orient = VERTICAL,
                             command = self.canv.yview)
            vbar.pack(side = RIGHT,
                      fill = Y)

            # horizontal scrollbar
            hbar = Scrollbar(self.canv,
                             orient = HORIZONTAL,
                             command = self.canv.xview)
            hbar.pack(side = BOTTOM,
                      fill = X)

            self.canv.config(yscrollcommand = vbar.set,
                        xscrollcommand = hbar.set)

            # keep track of canvas object so it can be deleted
            self.canvas_items.append(self.canv)

            # listen for mouse wheel
            self.canv.bind_all("<MouseWheel>", self.on_mouse_wheel)

            self.canvas_created = True

    def on_mouse_wheel(self, event):
        """ Update the canvas vertical scrollbar """

        try:
            self.canv.yview_scroll(-1 * (event.delta/120), "units")
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

        self.s0 = Button(self, command = lambda n = 0: self.insert_schedule(0),
                    text = self.schedules[0],
                    padx = 10, pady = 10,
                    cursor = 'hand2')

        self.s1 = Button(self, command = lambda n = 1: self.insert_schedule(1),
                    text = self.schedules[1],
                    padx = 10, pady = 10,
                    cursor = 'hand2')

        self.s2 = Button(self, command = lambda n = 2: self.insert_schedule(2),
                    text = self.schedules[2],
                    padx = 10, pady = 10,
                    cursor = 'hand2')

        self.s3 = Button(self, command = lambda n = 3: self.insert_schedule(3),
                    text = self.schedules[3],
                    padx = 10, pady = 10,
                    cursor = 'hand2')

        self.s4 = Button(self, command = lambda n = 4: self.insert_schedule(4),
                    text = self.schedules[4],
                    padx = 10, pady = 10,
                    cursor = 'hand2')

    def place_buttons(self):
        """ Place the View Schedule Buttons on the view page """

        # get valid weeks so we know how many view schedule buttons to show
        weeks = self.get_valid_weeks() - 1

        if 0 <= weeks:
            self.s0.pack()
            self.s0.place(x = 50, y = 47)
        else:
            self.delete([self.s0])

        if 1 <= weeks:
            self.s1.pack()
            self.s1.place(x = 138, y = 47)
        else:
            self.delete([self.s1])

        if 2 <= weeks:
            self.s2.pack()
            self.s2.place(x = 226, y = 47)
        else:
            self.delete([self.s2])

        if 3 <= weeks:
            self.s3.pack()
            self.s3.place(x = 314, y = 47)
        else:
            self.delete([self.s3])

        if 4 <= weeks:
            self.s4.pack()
            self.s4.place(x = 402, y = 47)
        else:
            self.delete([self.s4])

    def get_valid_weeks(self):
        """ Returns the number of valid weeks that were generated """

        weeks = 0
        for week in globs.mainScheduler.weeks:
            if week.valid:
                weeks += 1

        return weeks

    def insert_schedule(self, n):
        """ Inserts schedule n into the textarea/scrollbox of the View page """

        self.toggle_constraint_acceptance_flag = True

        self.last_viewed_schedule = n

        # delete drop downs
        self.delete(self.drop_down_items)

        # format the schedules
        if not self.toggle_schedules_flag:

            # delete previous canvas
            #self.delete(self.canvas_items)

            self.create_graphical_schedules()

            # delete previous canvas items
            self.canv.delete(ALL)

            if self.is_run_clicked:
                self.format_graphical_schedule(globs.mainScheduler.weeks[n].print_concise())

            #self.bg_label['fg'] = 'white'

        else:
            # hide bg_label text
            #self.bg_label['fg'] = 'white'

            # delete previous canvas items
            self.canv.delete(ALL)

            self.format_compact_schedule(globs.mainScheduler.weeks[n].print_concise())

    def insert_constraint(self, n):
        """Insert constraints on the view page"""

        self.last_viewed_schedule = n

        self.delete(self.drop_down_items)
        self.delete([self.bg_label])
        if self.toggle_constraint_acceptance_flag:
            self.format_compact_constraint(globs.mainScheduler.weeks[n].constraints)
            #self.bg_label['fg'] = 'white'

        else:
            # destroy old labels to make room for new ones
            self.delete(self.table_labels)

            # hide bg_label text
            #self.bg_label['fg'] = 'white'

        self.toggle_constraint_acceptance_flag = not self.toggle_constraint_acceptance_flag


    def format_graphical_schedule(self, schedule_text):
        """ Formats the graphical schedules """

        schedule_text = schedule_text.split('\n')

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

        ypos_times = {}
        y_times = []
        times = {}

        instructor = ''

        del self.rooms[:]       # empty previous rooms

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

        self.rooms.sort()
        self.sort_selections()

        # calculate what time to begin showing courses on the graphical schedule
        for i in xrange(len(schedule_text) - 1):
            s = schedule_text[i].split(' ')

            if (' ' in schedule_text[i]) and len(schedule_text[i]) > 0:
                # len(s) < 7, then course does not have a section (001, 002, etc.)
                if len(s) < 7:
                    if s[3] + " " + s[4] in self.rooms[self.room_selection_option]:
                        temp = schedule_text[i].split(' ')
                        temp = temp[len(temp) - 1].split('-')[0].split(':')[0]
                        temp = int(temp)
                        if not temp in y_times:
                            y_times.append(temp)
                # course has a section number (001, 002, etc.)
                else:
                    if s[4] + " " + s[5] in self.rooms[self.room_selection_option]:
                        temp = schedule_text[i].split(' ')
                        temp = temp[len(temp) - 1].split('-')[0].split(':')[0]
                        temp = int(temp)
                        if not temp in y_times:
                            y_times.append(temp)


        y_times.sort()

        if len(y_times) == 0:
            return

        a = y_times[0]
        b = y_times[len(y_times) - 1]
        n = 0
        if (b - a) < 7:
            n = 7 - (b - a)

        for i in xrange(a, b + 1 + n):
            if not i in y_times:
                y_times.append(i)

        y_times.sort()

        for i in xrange(len(y_times)):
            ypos_times[y_times[i]] = (ypad + 50 + 100 + (i * 100))

        # Build y-axis
        if (y_times[0] - 1) > 13:
            times[y_times[0] - 1] = str(y_times[0] - 13) + 'pm'
        elif (y_times[0] - 1) == 13 or (y_times[0] - 1) == 12:
            times[y_times[0] - 1] = str(12) + 'pm'
        else:
            times[y_times[0] - 1] = str(y_times[0] - 1) + 'am'

        for i in xrange(len(y_times)):
            n = y_times[i]
            if n > 12:
                times[n] = str(n - 12) + 'pm'
            elif n == 12:
                times[n] = str(n) + 'pm'
            else:
                times[n] = str(n) + 'am'

        if (y_times[len(y_times)-1] + 1) > 12:
            times[y_times[len(y_times)-1] + 1] = str(y_times[len(y_times)-1] + 1 - 12) + 'pm'
        elif (y_times[len(y_times)-1] + 1) == 12 or (y_times[len(y_times)-1] + 1) == 11:
            times[y_times[len(y_times)-1] + 1] = str(y_times[len(y_times)-1] + 1) + 'pm'
        else:
            times[y_times[len(y_times)-1] + 1] = str(y_times[len(y_times)-1] + 1) + 'am'

        # draw y-axis values to the canvas
        incr = 0
        for i in times:
            self.canv.create_text(xstart + xpad - 25,
                                  ystart + ypad + 40 + (incr * 100),
                                  text = times[i],
                                  font = (font_style, size_l))
            incr += 1

        # populate graphical schedule with course data
        for i in xrange(len(schedule_text) - 1):

            txt = ''                # holds the course data
            schedule_days = ''      # holds the course days
            schedule_time = ''      # holds the course start time
            start_time = ''
            end_time = ''

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
                                       ' ' + temp[1] + '\n'

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
                                       '\n' + 'Sec. ' + temp[2] + '\n'

                # convert military time to 12 oclock time
                start = start_time.split(':')[0]
                end = end_time.split(':')[0]
                if start > '12':
                    start = str(int(start) - 12)
                    start_time = start + start_time[2:]
                if end  > '12':
                    end = str(int(end) - 12)
                    end_time = end + end_time[2:]

                course_info += start_time + "-" + end_time

                # txt is the text value in canv.create_text
                txt = instructor + '\n' + course_info

                for day in schedule_days:

                    n = int(schedule_time.split(':')[0])

                    # Monday
                    if day == 'm' or day == 'M':
                        self.canv.create_text(xpos_days['Monday'],
                                              ypos_times[n],
                                              text = txt,
                                              width = 100,
                                              font = (font_style, size_l))
                    # Tuesday
                    elif day == 't' or day == 'T':
                        self.canv.create_text(xpos_days['Tuesday'],
                                              ypos_times[int(schedule_time.split(':')[0])],
                                              text = txt,
                                              width = 100,
                                              font = (font_style, size_l))
                    # Wednesday
                    elif day == 'w' or day == 'W':
                        self.canv.create_text(xpos_days['Wednesday'],
                                              ypos_times[int(schedule_time.split(':')[0])],
                                              text = txt,
                                              width = 100,
                                              font = (font_style, size_l))
                    # Thursday
                    elif day == 'r' or day == 'R':
                        self.canv.create_text(xpos_days['Thursday'],
                                              ypos_times[int(schedule_time.split(':')[0])],
                                              text = txt,
                                              width = 100,
                                              font = (font_style, size_l))
                    # Friday
                    elif day == 'f' or day == 'F':
                        self.canv.create_text(xpos_days['Friday'],
                                              ypos_times[int(schedule_time.split(':')[0])],
                                              text = txt,
                                              width = 100,
                                              font = (font_style, size_l))

        # background for the days of the week
        self.canv.create_rectangle(0, 0, 1050, 30, fill = 'cyan', outline = '')

        # draw days of the week across the x-axis of the canvas
        self.canv.create_text(xpad + 55,
                              ypad,
                              text = days[0],
                              font = (font_style, size_l))
        self.canv.create_text(xpad + 54 + 100,
                              ypad,
                              text = days[1],
                              font = (font_style, size_l))
        self.canv.create_text(xpad + 57 + 200,
                              ypad,
                              text = days[2],
                              font = (font_style, size_l))
        self.canv.create_text(xpad + 53 + 300,
                              ypad,
                              text = days[3],
                              font = (font_style, size_l))
        self.canv.create_text(xpad + 48 + 400,
                              ypad,
                              text = days[4],
                              font = (font_style, size_l))

        if self.is_run_clicked:
            self.create_room_selection()

        # reset
        self.room_selection_option = 0

    def format_compact_schedule(self, schedule_text):
        """ Formats the compact schedules """

        schedule_text = schedule_text.split('\n')

        yt = 12
        for i in xrange(len(schedule_text) - 1):
            # teacher labels
            if not (' ' in schedule_text[i]) and len(schedule_text[i]) > 0:
                self.canv.create_rectangle(0, yt-12, 1050, yt + 12,
                                           fill = 'black',
                                           outline = '')
                self.canv.create_text(10, yt, anchor = 'w',
                                      text = schedule_text[i],
                                      font = (font_style, size_l),
                                      fill = 'white')

            else:   # course info labels
                self.canv.create_text(10, yt, anchor = 'w',
                                      text = schedule_text[i],
                                      font = (font_style, size_l))

            yt += 29

    def format_compact_constraint(self, constraints_dict):
        """ Formats the compact schedules """

        # cache constraints
        if self.cached_constraints != globs.mainScheduler.constraints and self.cache_flag == True:
            for constraint in globs.mainScheduler.constraints:
                self.cached_constraints.append(constraint)

            self.cache_flag = False

        #----------------------------------------------#
        # sort constraints by universal and user-added #
        #----------------------------------------------#

        # lists for two types of constranits (universal and user-added)
        universal_constraints = []
        user_added_constraints = []

        for constraint in self.cached_constraints:
            if constraint.universal:
                universal_constraints.append(constraint.name)
            else:
                user_added_constraints.append(constraint.name)

        universal_constraints.sort()
        user_added_constraints.sort()

        # sort constraints and prep constraint data for canvas display
        universal_sorted_constraints = []
        user_added_sorted_constraints = []
        for key in constraints_dict.keys():
            if key in universal_constraints:
                universal_sorted_constraints.append([key,
                                                     constraints_dict[key][0],
                                                     constraints_dict[key][1]])
            elif key in user_added_constraints:
                user_added_sorted_constraints.append([key,
                                                     constraints_dict[key][0],
                                                     constraints_dict[key][1]])
        universal_sorted_constraints.sort()
        user_added_sorted_constraints.sort()

        #---------------------------------------#
        # display constraint data on the canvas #
        #---------------------------------------#

        # legend bullet: univeral constraints
        self.canv.create_rectangle(20, 25, 40, 45, fill = 'cyan', outline = '')
        self.canv.create_text(125, 35,
                              text = 'Universal Constraints',
                              font = (font_style, size_l))

        # legend bullet: user-added constraints
        self.canv.create_rectangle(250, 25, 231, 45, width = 3, fill = 'yellow', outline = '')
        self.canv.create_text(345, 35,
                              text = 'User Added Constraints',
                              font = (font_style, size_l))

        y = 75
        self.canv.create_text(20, y, anchor = 'w',
                                  text = 'Constraint Name',
                                  font = (font_style, size_h2))
        self.canv.create_text(430, y, anchor = 'w',
                                  text = 'Passes',
                                  font = (font_style, size_h2))

        y += 40

        universal_constraints_length = len(universal_sorted_constraints)
        user_added_constraints_length = len(user_added_constraints)

        # increase canvas scrollregion size if too many user added constraints
        if user_added_constraints_length > 20:
            self.canv.config(scrollregion = (0, 0, 600,
                                             1050 + user_added_constraints_length * 24))

        count = 0

        # background color for universal constraints
        self.canv.create_rectangle(15, 99, 518,
                                   104 + (universal_constraints_length * 24),
                                   width = 3, outline = 'cyan')

        # create text to display on the canvas
        for constraints in [universal_sorted_constraints, user_added_sorted_constraints]:
            for constraint in constraints:

                # show constraint name
                self.canv.create_text(25, y, anchor = 'w',
                                      text = constraint[0],
                                      font = (font_style, size_l))

                passes = ''
                numerator = constraint[1]
                denominator = constraint[2]

                # determine if pass or fail
                if (numerator == 0 or numerator == 1) and (denominator == 1):
                    if numerator == 0:
                        passes = 'Fail'
                    else:
                        passes = 'Pass'

                    # show pass or fail
                    self.canv.create_text(440, y, anchor = 'w',
                                          text = passes,
                                          font = (font_style, size_l))
                # calculate percent
                else:
                    percent = (float(numerator) / float(denominator)) * 100
                    percent = round(percent, 2)

                    # show percent
                    self.canv.create_text(440, y, anchor = 'w',
                                          text = str(percent) + '%',
                                          font = (font_style, size_l))

                count += 1
                if count == universal_constraints_length:
                    y += 6

                    # background color for user-added constraints
                    length = user_added_constraints_length
                    if length == 0:
                        length = 1

                    self.canv.create_rectangle(15, y + 13, 518,
                                               y + 19 + (length * 24),
                                               width = 3, outline = 'yellow')
                    y += 3

                y += 24

        if user_added_constraints_length == 0:
                self.canv.create_text(25, y, anchor = 'w',
                                      text = "No user-added constraints.",
                                      font = (font_style, size_l))

    def delete(self, labels):
        """ Delete dynamically created objects from memory """

        for i in xrange(len(labels)):
            labels[i].destroy()     # destroy old labels

        del labels[:]

class MiscPage(Page):

    def __init__(self, root):
        Frame.__init__(self, root)
        self.head_label = Label(self, text="Generating schedules...",
                                font = (font_style, size_h2))
        self.head_label.pack(pady = 80)

        self.load_bar_bg = Label(self, width = 40, height = 2)
        self.load_bar_bg['bg'] = 'gray'
        self.load_bar_bg.place(x = 207, y = 120)

        self.load_bar = Label(self, width = 0, height = 2)
        self.load_bar['bg'] = 'gray'
        self.load_bar.place(x = 207, y = 120)

        self.info_label = Label(self, text='', \
                          font =(font_style, size_l))
        self.info_label.pack()

        self.labels = []
        for i in xrange(3):
            self.labels.append(Label(self, text='', font =(font_style, size_l)))
            self.labels[i].place(x = 203, y = ((i + 1) * 20) + 100)

        self.is_loading = False
        self.prev_text = ''
        self.past = ""

    def update_loading_bar(self):
        self.update()

        if not self.is_loading:
            self.load_bar['bg'] = 'green'
            self.is_loading = True

        # print(self.load_bar['width'])
        # Stop at "almost done" status; will jump to 100% when finished
        if self.load_bar['width'] <= 39:
            self.load_bar['width'] += 1
        else:
            # print("bar is overflowing! this shouldn't be happening!")
            pass
        # part 1 of the genetic algorithm

        # if self.past == "":
        #     info = globs.mainScheduler.gui_loading_info
        #     self.info_label['text'] = info

        #     if not self.is_loading:
        #         if info.split(' ')[0] == "Schedule" and info.split(' ')[2] == "generated":
        #             self.load_bar['bg'] = 'green'
        #             self.is_loading = True
        #         else:
        #             self.load_bar_bg['bg'] = 'gray'
        #             self.load_bar['bg'] = 'gray'
        #     else:
        #         if info != self.prev_text:
        #             self.load_bar['width'] += 2
        #             self.prev_text = info
        # # part 2 of the genetic algorithm
        # else:
        #     info1 = globs.mainScheduler.gui_loading_info1
        #     #info2 = globs.mainScheduler.gui_loading_info2
        #     #info3 = globs.mainScheduler.gui_loading_info3
        #     info2 = info3 = ''

        #     temp = [info1, info2, info3]

        #     if info1 != self.prev_text:
        #         self.load_bar['width'] += 2
        #         self.prev_text = info1

        #         for i in xrange(3):
        #             self.labels[i]['text'] = temp[i]

        # self.past = globs.mainScheduler.gui_loading_info1

    def finish_loading(self):
        self.load_bar['width'] = 40
        self.update()

class MainWindow(Frame):

    def __init__(self, root):
        self.root = root

        globs.init()
        Frame.__init__(self, root)
        self.pack(side = TOP, fill = "both")

        # ToolTips does not work well on non-Windows platforms
        if sys.platform.startswith('win'):
            ToolTips(root)

        self.run_finished = False
        self.run_clicked = False

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

#         self.misc_btn = Button(self.menu, text='Splash', command=self.show_misc, \
#                                width="10", height="3", font=(font_style, size_h2), cursor = 'hand2')
#         self.misc_btn.pack(fill=X, side="top", pady=2)
#editing renato
        self.run_btn = Button(self.menu, text='RUN', bg='green', command=self.run_scheduler, \
                               width="10", height="3", font=(font_style, size_h2), cursor = 'hand2')
        self.run_btn.pack(fill = X, side = "top", pady=2)

        # PAGES
        self.home_page = HomePage(self.content_container)
        self.home_page.place(in_=self.content_container, x=0, y=0, relwidth=1, relheight=1)

        self.constraint_page = ConstraintPage(self.content_container, globs.mainScheduler.constraints)
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

    def disable_buttons(self):
        self.home_btn.config(state=DISABLED)
        self.constraint_btn.config(state=DISABLED)
        self.view_btn.config(state=DISABLED)
        self.run_btn.config(state=DISABLED)

    def enable_buttons(self):
        self.home_btn.config(state=NORMAL)
        self.constraint_btn.config(state=NORMAL)
        self.view_btn.config(state=NORMAL)
        self.run_btn.config(state=NORMAL)

    def thread_run_scheduler(self):
        instructors = globs.instructors
        self.misc_page.load_bar['width'] = 0 # make sure loading bar starts at 0 each run
        # RUN SCHEDULER METHOD
        # Add hard/obvious constraints before running
        runtime_var = self.home_page.runtime_selected_var.get()
        if runtime_var not in [1, 10, 60, 480]:
            runtime_var = int(self.home_page.runtime_custom_input.get()) # convert from DoubleVar
            if runtime_var < 1:
                runtime_var = 1
            print(runtime_var)

        self.disable_buttons()

        globs.mainScheduler.evolution_loop(self, runtime_var)

        self.enable_buttons()

        self.run_finished = True
        return

    def finished_running(self):
        """ Display view_page after run_scheduler is finished running. """
        self.misc_page.finish_loading()

        self.view_page.is_run_clicked = True
        self.view_page.cached_constraints = []
        self.view_page.cache_flag = True

        self.view_page.is_constraints_set = True
        if globs.mainScheduler.weeks[0].valid:
            self.view_page.insert_schedule(0)  # show the first schedule in the view page
            self.view_page.show_nav()
            if hasattr(self.view_page, 'bg_label'):
                self.view_page.bg_label.destroy()
        else:
            self.view_page.create_compact_schedules(none_to_show = True) # tell user no schedules

        # DISPLAY VIEW PAGE
        self.show_view()

        self.run_clicked = False
        return

    def setup_loading_screen(self):
        total_runtime = self.home_page.runtime_selected_var.get()

        runtime_sec = total_runtime * 60
        bar_width = 40.0

        #seconds_per_update = runtime_sec / bar_width
        print("runtime_sec", runtime_sec)
        print("bar_width", bar_width)
        #print("seconds_per_update", seconds_per_update)

        return

    def go_to_loading_screen(self):
        #self.root.after(250, self.show_misc)
        self.show_misc()
        self.update()

        return


    def go_to_constraints_screen(self):
        self.show_constraint()
        self.update()

        return

    def run_scheduler(self):

        if not self.run_clicked:
            self.view_page.is_constraints_set = False
            self.run_clicked = True
            self.view_page.is_run_clicked = False
            self.run_finished = False

            instructors = globs.instructors
            # RUN SCHEDULER METHOD
            # Add hard/obvious constraints before running
            self.thread_run_scheduler()

            # only export schedules if it is possible
            try:
                if not globs.mainScheduler.paused:
                    interface.export_schedules(globs.mainScheduler.weeks)
            except:
                print("Could not export schedules")

        return

    def ask_to_keep_running(self):
        if tkMessageBox.askyesno("Continue?", "It is possible you have conflicting " + \
                                 "constraints, do you want to stop schedule generation to check your constraints?"):
            return True
        return False
