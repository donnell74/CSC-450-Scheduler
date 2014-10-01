import csv
from structures import *
import os

def csv_dict_reader(file_obj):
    """
    Read CSV file using csv.Dictreader
    """
    reader =csv.DictReader(file_obj,delimiter=',')
    for line in reader:
        print(line["Courses"], line["Credit"])
        
        
def export_schedules(weeks, export_dir = "./", debug = False):
    counter = 0
    for each_week in weeks:
        counter += 1
        filename = "schedule_" + str(counter) + ".csv"
        with open(os.path.join(export_dir, filename), 'w') as out:
            out.write(each_week.print_concise())
        
if __name__ == "__main__":
    with open("Scheduler.csv") as f_obj:
        csv_dict_reader(f_obj)

