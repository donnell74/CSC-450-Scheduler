import csv
from structures import *
import os


def csv_dict_reader(file_obj):
    """
    Read CSV file using csv.Dictreader
    Return dictionary of course keys and detail values in a tuple
    """
    courses_and_details = {}
    reader = csv.DictReader(file_obj, delimiter=',')
    for line in reader:
        courses_and_details[line["Course"]] = \
            (int(line["Credit"]), line["Instructor"], line["Prereqs"])
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
                courses_credits_and_instructors[
                    course] = (details[0], each_instructor, details[2])
    return courses_credits_and_instructors


def export_schedules(weeks, export_dir="./", debug=False):
    counter = 0
    num_to_export = len(weeks)
    print("\nExporting " + str(num_to_export) + " schedules")
    for each_week in weeks:
        counter += 1
        filename = os.path.join(
            export_dir, "schedule_" + str(counter) + ".csv")
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, 'w') as out:
            out.write(each_week.print_concise())

    # delete past extra schedules
    counter += 1
    while counter <= 5:
        filename = os.path.join(
            export_dir, "schedule_" + str(counter) + ".csv")
        if os.path.isfile(filename):
            os.remove(filename)
        counter += 1


def get_courses(courses_credits_and_instructors):
    """
    Gets list of course objects affiliated with instructors
    """
    courses = []
    for course, details in courses_credits_and_instructors.iteritems():
        c = Course(course, details[0], details[1])
        courses.append(c)
        details[1].add_course(c)
    return courses


def get_prereqs(courses_credits_and_instructors, courses):
    """IN: courses_credits_and_instructors, list of courses
    OUT: list of prereq objects"""
    print "getting prereqs"
    out = []
    for course, details in courses_credits_and_instructors.iteritems():
        prereq = details[2]
        for each_course in courses:
            if each_course.code == course:
                course = each_course
                break
        prereq = prereq.split(' ')
        if len(prereq) == 0:
            continue
        else:
            covered = [p.absolute_course for p in out]
            if course.absolute_course not in covered:
                prereq_obj = Prereq(course.absolute_course, courses)
                for each_prereq in prereq:
                    prereq_obj.add_prereq(each_prereq, courses)
                out.append(prereq_obj)
    return out

def get_extended_prereqs(prereqs, courses):
    """IN: list of prereq objects, list of all course objects
    OUT: list of prereq objects with extended prereqs accounted for"""
    #courses with a prereq
    covered = [p.absolute_course for p in prereqs]
    for each_prereq in prereqs: #objects
        for each_absolute_prereq in each_prereq.absolute_prereqs: #the courses required
            if each_absolute_prereq in covered and each_absolute_prereq not in each_prereq.absolute_prereqs:
                derived_prereq = next(p for p in covered if each_absolute_prereq == p)
                each_prereq.add_prereq(derived_prereq, courses)
                print derived_prereq
    return prereqs
