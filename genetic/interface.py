import csv
from structures import *
import os
import xml.etree.ElementTree as ET

def create_scheduler_from_file(path_to_xml):
    """Reads in an xml file and schedules all courses found in it"""
    #CHANGE TO PASS IN OBJECTS WHERE NECESSARY RATHER THAN STRINGS...instructor
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        courses = [Course(c.attrib["code"], c.attrib["credit"], c.attrib["instructor"]) for c in root.find("schedule").find("courseList").getchildren()]
        rooms = [r.text for r in root.find("schedule").find("roomList").getchildren()]
        time_slots = [ t.text for t in root.find("schedule").find("timeList").getchildren()]
        time_slot_divide = root.find("schedule").find("timeSlotDivide").text
        setCourses = [i.attrib for i in root.findall("course")]
        return_schedule = Scheduler(courses, rooms, time_slots, int(time_slot_divide))
        return_schedule.weeks[0].fill_week(setCourses)
        return return_schedule
    except Exception as inst:
        print(inst)
        return None


def create_course_list_from_file(path_to_xml, instructors_dict):
    """Reads an xml file and creates a list of course objects from it and the list of unique instructors in a dict"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructor_strings = [c.attrib["instructor"] for c in root.find("schedule").find("courseList").getchildren()]
        courses = [Course(c.attrib["code"], c.attrib["credit"], instructors_dict[c.attrib["instructor"]]) \
            for c in root.find("schedule").find("courseList").getchildren()]
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
    print("\nExporting " + str(num_to_export) + " schedules")
    for each_week in weeks:
        if each_week.valid:
            counter += 1
            filename = os.path.join(
                export_dir, "schedule_" + str(counter) + ".csv")
            if os.path.isfile(filename):
                os.remove(filename)
            with open(filename, 'w') as out:
                out.write(each_week.print_concise())

    counter += 1
    while counter <= 5:
        filename = os.path.join(
            export_dir, "schedule_" + str(counter) + ".csv")
        if os.path.isfile(filename):
            os.remove(filename)
        counter += 1
