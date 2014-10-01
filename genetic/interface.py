import csv
from structures import *

def csv_dict_reader(file_obj):
    """
    Read CSV file using csv.Dictreader
    """
    reader =csv.DictReader(file_obj,delimiter=',')
    for line in reader:
        print(line["Courses"], line["Credit"])
        
        
def export_schedules(weeks, debug = False):
    for each_week in weeks:
        str(each_week)
        if debug:
            print(each_week.fitness)
        
if __name__ == "__main__":
    with open("Scheduler.csv") as f_obj:
        csv_dict_reader(f_obj)

