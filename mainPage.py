from Tkinter import *
from guiClasses import *

root = Tk()
root.title('CSC Scheduler')
main = MainWindow(root)

window_width = 850
window_height = 600
screen_x_pos = (root.winfo_screenwidth() / 2) - (window_width / 2)
screen_y_pos = (root.winfo_screenheight() / 2) - (window_height / 2)

root.geometry(str(window_width) + 'x' + str(window_height) +\
                    '+' + str(screen_x_pos) + '+' + str(screen_y_pos))

main.pack()
root.mainloop()
