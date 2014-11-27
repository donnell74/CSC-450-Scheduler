from Tkinter import Frame, Label, Button, Scrollbar, Listbox, HORIZONTAL
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

        self.delete_all = Button(buttons_frame, text="Delete all",\
                                 command=self.delete_all_constraints)
        self.delete_all.pack(side=RIGHT, pady = 10)

        self.delete_selection = Button(buttons_frame, text="Delete", command=self.delete_selection)
        self.delete_selection.pack(side = RIGHT, padx = 20)

        self.yScroll = Scrollbar(self, orient=VERTICAL)
        self.yScroll.pack(side=RIGHT, fill = Y)
        
        self.xScroll = Scrollbar(self, orient=HORIZONTAL)
        self.xScroll.pack(side=BOTTOM, fill = X)
        
        self.listbox = Listbox(self, xscrollcommand = self.xScroll.set,\
                               yscrollcommand = self.yScroll.set,\
                               selectmode = MULTIPLE,\
                               width = 45, height = 20)

        self.xScroll['command'] = self.listbox.xview
        self.yScroll['command'] = self.listbox.yview
    
        self.listbox.pack(side=LEFT, fill=X, expand=1)

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
        selected_indices = list(selection)
        selected_indices.reverse()  # go over the indices backward to prevent mistakes
        
        if len(selection) > 0:
            #clear constraints selected from list box
            for i in selected_indices:
                self.listbox.delete(i)

            # clear constraints from the class
            deletion_list =[]
            for j in selected_indices:
                #print(self.constraint_name_list)
                #print(self.constraints_output)
                deletion_list.append(self.constraint_name_list.pop(j))
                print(deletion_list[-1])
                self.constraints_output.pop(j)
            # clear selected constraints from the scheduler object
            globs.mainScheduler.delete_list_constraints(deletion_list)
