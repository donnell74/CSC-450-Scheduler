import csv
from structures import *
import os

def csv_dict_reader(file_obj):
    """
    Read CSV file using csv.Dictreader
    Return dictionary of course keys and detail values in a tuple
    """
    courses_and_details = {}
    reader = csv.DictReader(file_obj,delimiter=',')
    for line in reader:
        courses_and_details[line["Course"]] = \
        (int(line["Credit"]), line["Instructor"])
    return courses_and_details

def get_instructors(courses_and_details):
    """
    Gets list of unique instructors from courses dictionary
    """
    instructors = []
    for each_detail in courses_and_details.values():
        instructor_object = Instructor(each_detail[1])
        if instructor_object not in instructors:
            instructors.append(instructor_object)
    return instructors

def include_instructors_in_dict(courses_and_details, instructors):
    """
    Gets a new dict based off courses_and_details, but with unique
    instructor objects rather than instructor strings
    """
    courses_credits_and_instructors = {}
    for course, details in courses_and_details.iteritems():
        for each_instructor in instructors:
            if str(each_instructor) == details[1]:
                courses_credits_and_instructors[course] = (details[0], each_instructor)
    return courses_credits_and_instructors
        
def export_schedules(weeks, export_dir = "./", debug = False):
    counter = 0
    for each_week in weeks:
        counter += 1
        filename = "schedule_" + str(counter) + ".csv"
        with open(os.path.join(export_dir, filename), 'w') as out:
            out.write(each_week.print_concise())

def get_courses(courses_credits_and_instructors):
    """
    Gets list of course objects affiliated with instructors
    """
    courses = []
    for course, details in courses_credits_and_instructors.iteritems():
        courses.append(Course(course, details[0], details[1]))
        details[1].add_course(course)
    return courses
