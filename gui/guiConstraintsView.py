from Tkinter import *
import globs

class ConstraintsView(Frame):
    
    def __init__(self, parent):
        Frame.__init__(self, parent)
        
        # holds the scrollbox output text for the added constraints
        self.constraints_output = []
         
        textL = "Constraints Added:"
        self.text = Label(self, text = textL)
        self.text.pack(anchor = NW, expand = YES)
        
        buttons_frame = Frame(self)
        buttons_frame.pack(side = BOTTOM)
        
        self.delete_all = Button(buttons_frame, text="Delete all", command=self.delete_all_constraints)
        self.delete_all.pack(side=RIGHT)
        
        self.delete_selection = Button(buttons_frame, text="Delete", command=self.delete_selection)
        self.delete_selection.pack(side = RIGHT, padx = 20)
        
        self.scrollbar = Scrollbar(self, orient=VERTICAL)
        self.listbox = Listbox(self, yscrollcommand = self.scrollbar.set, selectmode = MULTIPLE,\
                                width = 40, height = 15)
        self.scrollbar.config(command=self.listbox.yview)
        
        self.listbox.pack(side=LEFT, fill=X, expand=1)
        self.scrollbar.pack(side=LEFT, fill=Y)
        
    def view_constraints(self, constraint):
        output = constraint[0]
        #output = output.strip("Constraint Conflict")
        
        if constraint[1] == 10:
            output += 'Low'
        elif constraint[1] == 25:
            output += 'Medium'
        elif constraint[1] == 50:
            output += 'High'
        elif constraint[1] == 0: # mandatory has a 0 priority
            output += 'Mandatory'
            
        self.constraints_output.append(output)

        # clear listbox
        self.listbox.delete(0, END)
        
        for item in self.constraints_output:
            self.listbox.insert(END, item)

    def delete_all_constraints(self):
        #clear all constraints from list box
        self.listbox.delete(0, END)
        # clear constraints from the class
        self.constraints_output = []
        # clear all constraints from the scheduler object
        globs.mainScheduler.clear_constraints()
        
    def delete_selection(self) :
        
        items = self.listbox.curselection()
        if len(items) > 0: 
            #clear constraints selected from list box
            pos = 0
            for i in items :
                idx = int(i) - pos
                self.listbox.delete( idx,idx )
                pos = pos + 1
            
            # clear constraints from the class
            for j in range(len(sorted(items, reverse=True))):
                del self.constraints_output[j]
            
            # clear selected constraints from the scheduler object
            globs.mainScheduler.delete_list_constraints(items)