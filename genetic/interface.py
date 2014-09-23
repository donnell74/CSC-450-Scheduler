


import csv




def csv_dict_reader(file_obj):
    """
    Read CSV file using csv.Dictreader
    """
    reader =csv.DictReader(file_obj,delimiter=',')
    for line in reader:
        print(line["Courses"], line["Credit"])
        
if __name__ == "__main__":
    with open("Scheduler.csv") as f_obj:
        csv_dict_reader(f_obj)

