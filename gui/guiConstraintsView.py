from Tkinter import Frame, Label, Button, Scrollbar, Listbox
from Tkconstants import RIGHT, LEFT, YES, BOTTOM, NW, VERTICAL, MULTIPLE, X, Y, END
import globs

class ConstraintsView(Frame):
    "Presents all constraints created by user"

    def __init__(self, parent):
        Frame.__init__(self, parent)
        # holds all constraints
        self.constraint_name_list = []

        # holds the scrollbox output text for the added constraints
        self.constraints_output = []

        text_label = "Constraints Added:"
        self.text = Label(self, text = text_label)
        self.text.pack(anchor = NW, expand = YES)

        buttons_frame = Frame(self)
        buttons_frame.pack(side = BOTTOM)

        self.delete_all = Button(buttons_frame,
                                 text="Delete all",
                                 command=self.delete_all_constraints)
        self.delete_all.pack(side=RIGHT)

        self.delete_selection = Button(buttons_frame,
                                       text="Delete",
                                       command=self.delete_selection)
        self.delete_selection.pack(side = RIGHT, padx = 20)

        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.listbox = Listbox(self,
                               yscrollcommand = self.scrollbar.set,
                               selectmode = MULTIPLE,
                               width = 40, height = 15)
        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.pack(side=LEFT, fill=X, expand=1)
        self.scrollbar.pack(side=LEFT, fill=Y)

    def add_constraint_listbox(self, constraint_name, priority):
        "Updates the list box with the new constraint created"
        output = constraint_name + " Priority = "
        
        self.constraint_name_list.append(constraint_name)
        
        if priority == 10:
            output += 'Low'
        elif priority == 25:
            output += 'Medium'
        elif priority == 50:
            output += 'High'
        elif priority == 0: # mandatory has a 0 priority
            output += 'Mandatory'

        self.constraints_output.append(output)

        # clear listbox
        self.listbox.delete(0, END)

        for item in self.constraints_output:
            self.listbox.insert(END, item)

    def delete_all_constraints(self):
        "Deletes all constraints from the listbox and the mainScheduler"
        # clear all constraints from list box
        if self.constraint_name_list:
            self.listbox.delete(0, END)

            # clear all output constraints
            self.constraints_output = []

            # clear all constraints from the scheduler object
            globs.mainScheduler.delete_list_constraints(self.constraint_name_list)

            #clear all constraints
            self.constraint_name_list = []

    def delete_selection(self):
        selection = self.listbox.curselection()
        if len(selection) > 0:
            #clear constraints selected from list box
            pos = 0
            for i in selection :
                real_position = int(i) - pos
                self.listbox.delete(real_position, real_position)
                pos = pos + 1

            # clear constraints from the class
            deletion_list =[]
            for j in selection:
                deletion_list.append(self.constraint_name_list.pop(j))
                self.constraints_output.pop(j)
            # clear selected constraints from the scheduler object
            globs.mainScheduler.delete_list_constraints(deletion_list)