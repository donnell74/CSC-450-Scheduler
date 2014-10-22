import csv
from structures import *
import os
import xml.etree.ElementTree as ET
import interface
from scheduler import *

def create_scheduler_from_file(path_to_xml):
    """Reads in an xml file and schedules all courses found in it"""
#try:
    tree = ET.parse(path_to_xml)
    root = tree.getroot()
    instructors = interface.create_instructors_from_courses(path_to_xml)
    instructors_dict = dict(zip([inst.name for inst in instructors], [inst for inst in instructors]))
    courses = interface.create_course_list_from_file(path_to_xml, instructors_dict)
    rooms = interface.create_room_list_from_file(path_to_xml)
    time_slots = interface.create_time_slot_list_from_file(path_to_xml)
    time_slot_divide = root.find("schedule").find("timeSlotDivide").text
    course_titles = [course.code for course in courses]
    setCourses = [i.attrib for i in root.findall("course")]
    return_schedule = Scheduler(courses, rooms, time_slots, int(time_slot_divide), True)
    return_schedule.weeks[0].fill_week(setCourses)
    return return_schedule
#    except Exception as inst:
#        print(inst)
#        return None


def create_course_list_from_file_test(path_to_xml):
    """Same as create_course_list_from_file, but creates its own instructors_dict"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructors = interface.create_instructors_from_courses(path_to_xml)
        instructors_dict = dict(zip([inst.name for inst in instructors], [inst for inst in instructors]))
        courses = interface.create_course_list_from_file(path_to_xml, instructors_dict)
        return courses
    except Exception as inst:
        print(inst)
        return None


def create_course_list_from_file(path_to_xml, instructors_dict):
    """Reads an xml file and creates a list of course objects from it
    IN: xml path and the list of unique instructors in a dict
    OUT: list of course objects; courses are added to instructors"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructor_strings = [c.attrib["instructor"] for c in root.find("schedule").find("courseList").getchildren()]
        courses = []
        for c in root.find("schedule").find("courseList").getchildren():
            instructor = instructors_dict[c.attrib["instructor"]]
            course = Course(c.attrib["code"], int(c.attrib["credit"]), instructor)
            instructor.add_course(course)
            courses.append(course)
        return courses
    except Exception as inst:
        print(inst)
        return None


def create_room_list_from_file(path_to_xml):
    """Reads an xml file and creates a list of rooms (strings) from it"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        rooms = [r.text for r in root.find("schedule").find("roomList").getchildren()]
        return rooms
    except Exception as inst:
        print(inst)
        return None


def create_time_slot_list_from_file(path_to_xml):
    """Reads an xml file and creates a list of time slots (strings) from it"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        time_slots = [r.text for r in root.find("schedule").find("timeList").getchildren()]
        return time_slots
    except Exception as inst:
        print(inst)
        return None


def create_instructors_from_courses(path_to_xml):
    """Reads an xml file and creates a list of unique instructor objects"""
    instructors = []
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructors_unique = []
        instructors_raw = [course.attrib["instructor"] for course in root.find("schedule").find("courseList").getchildren()]
        for each_instructor in instructors_raw:
            if each_instructor not in instructors_unique:
                instructors_unique.append(each_instructor)
        instructors_unique = map(lambda i: Instructor(i), instructors_unique)
        return instructors_unique
    except Exception as inst:
        print(inst)
        return None


def export_schedules(weeks, export_dir="./", debug=False):
    counter = 0
    num_to_export = len(weeks)
    for each_week in weeks:
        if each_week.valid:
            counter += 1
            filename = os.path.join(export_dir, "schedule_" + str(counter) + ".csv")
            if os.path.isfile(filename):
                os.remove(filename)
            with open(filename, 'w') as out:
                out.write(each_week.print_concise().replace(' ', ','))
    print("\nExporting " + str(counter) + " schedules")

    counter += 1
    while counter <= 5:
        filename = os.path.join(
            export_dir, "schedule_" + str(counter) + ".csv")
        if os.path.isfile(filename):
            os.remove(filename)
        counter += 1


def get_prereqs(path_to_xml, courses):
    """Determine first-level prereqs from xml and list of all courses"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        list_of_prereqs = []
        for c in root.find("schedule").find("courseList").getchildren():
            #get strings
            prereq = c.attrib["prereq"]
            if not prereq: #if this course has no prereqs
                continue
            course_string = c.attrib["code"]
            #prepare for prereq operations
            prereq = prereq.split(' ')
            absolute_course = "".join(course_string.split(' ')[:2])
            #prereq operations
            prereq_obj = Prereq(absolute_course, courses)
            for each_prereq in prereq:
                prereq_obj.add_prereq(each_prereq, courses)
            list_of_prereqs.append(prereq_obj)
        return list_of_prereqs
    except Exception as inst:
        print(inst)
        return None


def get_extended_prereqs(prereqs, courses):
    """IN: list of prereq objects, list of all course objects
    OUT: list of prereq objects with extended prereqs accounted for"""
    def find_prereq(prereq_absolute_course, prereqs):
        for p in prereqs:
            if p.absolute_course == prereq_absolute_course:
                return p
        #if not found
        return None

    #courses with a prereq
    covered = [p.absolute_course for p in prereqs]
    for each_prereq in prereqs: #prereq object
        if len(each_prereq.absolute_prereqs) == 0:
            continue
        for each_absolute_prereq in covered:
            if each_absolute_prereq in each_prereq.absolute_prereqs:
                derived_prereq_obj = find_prereq(each_absolute_prereq, prereqs)
                derived_prereqs = derived_prereq_obj.absolute_prereqs
                #next(p for p in covered if each_absolute_prereq == p)
                for each_derived in derived_prereqs:
                    each_prereq.add_prereq(each_derived, courses)
    return prereqs
