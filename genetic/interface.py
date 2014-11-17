import csv
from structures import *
import os
import yaml
import xml.etree.ElementTree as ET
from scheduler import *
from time import strftime, gmtime

def create_xml_from_yaml(path_to_yaml):
    try:
        def course_object_to_xml_string(code, credit, instructor, prereq,
                                        capacity, needs_computers, is_lab):
            # since "prereq='{}'".format('') -> "prereq=''''", we need an ugly conditional
            if prereq:
                unformatted_xml_string =  ("<item code='{0}' credit='{1}' instructor='{2}' prereq='{3}' "
                                           "capacity='{4}' needs_computers='{5}' is_lab='{6}'></item>")
                return unformatted_xml_string.format(code, credit, instructor,
                                                     prereq, capacity, needs_computers, is_lab)
            else: # prereq == None
                unformatted_xml_string =  ("<item code='{0}' credit='{1}' instructor='{2}' prereq='' "
                                           "capacity='{3}' needs_computers='{4}' is_lab='{5}'></item>")
                return unformatted_xml_string.format(code, credit, instructor,
                                                     capacity, needs_computers, is_lab)

        def room_object_to_xml_string(building, number, capacity, has_computers):
            unformatted_xml_string = ("<item building='{0}' number='{1}' capacity='{2}' "
                                      "has_computers='{3}'></item>")
            return unformatted_xml_string.format(building, number, capacity, has_computers)

        def print_number_spaces(num):
            return " " * num

        def print_indent(num):
            return print_number_spaces(2 * num)

        def schedule_tag(name):
            return "<schedule name='{0}'>".format(name)

        def tag(name, closing = False):
            if closing == True:
                return "</{0}>".format(name)
            else:
                return "<{0}>".format(name)

        def newline():
            return "\n"

        def xml_header():
            return "<?xml version='1.0'?>"

        yaml_file = open(path_to_yaml, 'r')
        yaml_dict = yaml.load(yaml_file)
        yaml_file.close()

        yaml_data_object = yaml_dict['data']['schedule']
        schedule_name = yaml_data_object['name']
        course_list = yaml_data_object['course_list']
        time_list_tr = yaml_data_object['time_list_tr']
        time_list_mwf = yaml_data_object['time_list_mwf']
        room_list = yaml_data_object['room_list']

        xml_file = open('./genetic/seeds/Input.xml', 'w')
        indent_level = 0

        xml_file.write(print_indent(indent_level) + xml_header() + newline())
        xml_file.write(print_indent(indent_level) + tag("data") + newline())
        indent_level += 1

        xml_file.write(print_indent(indent_level) + schedule_tag(schedule_name) + newline())
        indent_level += 1

        xml_file.write(print_indent(indent_level) + tag("courseList") + newline())
        indent_level += 1

        for course in course_list:
            if course['prereq'] == None:
                course_prereq = ""
            else:
                course_prereq = course['prereq']
            course_xml_string = course_object_to_xml_string(code = course['code'],
                                                            credit = course['credit'],
                                                            instructor = course['instructor'],
                                                            prereq = course_prereq,
                                                            capacity = course['capacity'],
                                                            needs_computers = course['needs_computers'],
                                                            is_lab = course['is_lab'])
            xml_file.write(print_indent(indent_level) + course_xml_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("courseList", closing = True) + newline())
        xml_file.write(print_indent(indent_level) + tag("roomList") + newline())
        indent_level += 1

        for room in room_list:
            room_xml_string = room_object_to_xml_string(building = room['building'],
                                                        number = room['number'],
                                                        capacity = room['capacity'],
                                                        has_computers = room['has_computers'])
            xml_file.write(print_indent(indent_level) + room_xml_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("roomList", closing = True) + newline())
        xml_file.write(print_indent(indent_level) + tag("timeListMWF") + newline())
        indent_level += 1

        for time_slot in time_list_mwf:
            xml_time_slot_string = "{0}{1}{2}".format(tag("item"), time_slot, tag("item", closing = True))
            xml_file.write(print_indent(indent_level) + xml_time_slot_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("timeListMWF", closing = True) + newline())
        xml_file.write(print_indent(indent_level) + tag("timeListTR") + newline())
        indent_level += 1

        for time_slot in time_list_tr:
            xml_time_slot_string = "{0}{1}{2}".format(tag("item"), time_slot, tag("item", closing = True))
            xml_file.write(print_indent(indent_level) + xml_time_slot_string + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("timeListTR", closing = True) + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("schedule", closing = True) + newline())
        indent_level -= 1

        xml_file.write(print_indent(indent_level) + tag("data", closing = True) + newline())

        xml_file.close()

    except Exception as exception_instance:
        print(exception_instance)
        return None

def create_scheduler_from_file_test(path_to_xml, slot_divide = 2):
    """Reads in an xml file and schedules all courses found in it
    IN: path to xml file as string
    OUT: scheduler object with one week based on the xml input"""
    tree = ET.parse(path_to_xml)
    root = tree.getroot()
    instructors = create_instructors_from_courses(path_to_xml)
    instructors_dict = dict(zip([inst.name for inst in instructors],
                           [inst for inst in instructors]))
    courses = create_course_list_from_file(path_to_xml, instructors_dict)
    rooms = create_room_list_from_file(path_to_xml)
    time_slots_mwf, time_slots_tr = create_time_slot_list_from_file(path_to_xml)
    time_slot_divide = slot_divide
    course_titles = [course.code for course in courses]
    setCourses = [i.attrib for i in root.findall("course")]
    return_schedule = Scheduler(courses, rooms, time_slots_mwf, time_slots_tr,
                                int(time_slot_divide), test = True)
    return_schedule.weeks[0].fill_week(setCourses)
    return return_schedule


def create_weeks_from_seeds(list_of_weeks_to_schedule_on, path_to_seeds):
    """Reads 5 XML files and creates week objects for these seeds
    path_to_seeds should look like directory/seed
    Seed number and .xml will be appended to it"""
    counter = 0
    for each_week in list_of_weeks_to_schedule_on[:5]:
        counter += 1
        tree = ET.parse(path_to_seeds + str(counter) + '.xml')
        root = tree.getroot()
        setCourses = [i.attrib for i in root.findall("course")]
        each_week.fill_week(setCourses)
    return list_of_weeks_to_schedule_on


def create_course_list_from_file_test(path_to_xml):
    """For testing purposes.  Creates a list of course objects without an instructors_dict
    IN: path to xml file as string
    OUT: list of course objects based on xml"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructors = create_instructors_from_courses(path_to_xml)
        instructors_dict = dict(zip([inst.name for inst in instructors],
                                    [inst for inst in instructors]))
        courses = create_course_list_from_file(path_to_xml, instructors_dict)
        return courses
    except Exception as inst:
        print(inst)
        return None


def create_course_list_from_file(path_to_xml, instructors_dict):
    """Reads an xml file and creates a list of course objects from it
    IN: xml path and an instructors_dict (instructor name, instructor object)
    OUT: list of course objects; courses are assigned to instructors"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructor_strings = [c.attrib["instructor"] for c in
                              root.find("schedule").find("courseList").getchildren()]
        courses = []
        for c in root.find("schedule").find("courseList").getchildren():
            instructor = instructors_dict[c.attrib["instructor"]]
            course = Course(code = c.attrib["code"],
                            credit = int(c.attrib["credit"]),
                            instructor = instructor,
                            capacity = int(c.attrib["capacity"]),
                            needs_computers = bool(int(c.attrib["needs_computers"])),
                            is_lab = bool(int(c.attrib["is_lab"])))
            instructor.add_course(course)
            courses.append(course)
        return courses
    except Exception as inst:
        print(inst)
        return None


def create_room_list_from_file(path_to_xml):
    """Reads an xml file and creates a list of rooms (strings) from it
    IN: path to xml file
    OUT: list of rooms as strings"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        # rooms will be list of tuples
        rooms = []
        for r in root.find("schedule").find("roomList").getchildren():
            # Make tuple with (building, number, capacity, has_computers)
            room = (r.attrib["building"], r.attrib["number"], r.attrib["capacity"], r.attrib["has_computers"])
            rooms.append(room)
        return rooms
    except Exception as inst:
        print(inst)
        return None


def create_time_slot_list_from_file(path_to_xml):
    """Reads an xml file and creates lists of time slots (strings) from it for mwf and tr
    IN: path to xml file
    OUT: tuple of 2 lists of time slots as strings (mwf and tr)"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        time_slots_mwf = [r.text for r in root.find("schedule").find("timeListMWF").getchildren()]
        time_slots_tr = [r.text for r in root.find("schedule").find("timeListTR").getchildren()]
        return (time_slots_mwf, time_slots_tr)
    except Exception as inst:
        print(inst)
        return None


def create_extras_list_from_file(path_to_xml):
    """Reads an xml file and creates a dictionary of extras
    IN: path to xml file
    OUT: dictionary of extras"""
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        extras = {}
        extras["input"] = dict([(parent.tag, [child.text for child in parent\
                    .getchildren()]) for parent in \
                    root.find("extra").find("input").getchildren()])
        extras["expected"] = dict([(parent.tag, [child.text for child in\
                    parent.getchildren()]) for parent in \
                    root.find("extra").getchildren()])["expected"]
        return extras
    except Exception as inst:
        print(inst)
        return None


def create_instructors_from_courses(path_to_xml):
    """Reads an xml file and creates a list of unique instructor objects
    IN: path to xml file
    OUT: list of instructor objects"""
    instructors = []
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()
        instructors_unique = []
        instructors_raw = [course.attrib["instructor"] for course in
                           root.find("schedule").find("courseList").getchildren()]
        for each_instructor in instructors_raw:
            if each_instructor not in instructors_unique:
                instructors_unique.append(each_instructor)
        instructors_unique = map(lambda i: Instructor(i), instructors_unique)
        return instructors_unique
    except Exception as inst:
        print(inst)
        return None


# should be updated to final object attributes (pr)
def export_schedule_xml(week, extras="", prefix="", export_dir="./tests/schedules/"):
    """Exports given week as xml for testing purposes
    IN: week object, extras string, prefix string, export directory
    OUT: creates an xml file for the given input"""
    timestr = strftime("%Y%m%d-%H%M%S", gmtime())
    filename = os.path.join(export_dir, prefix + timestr + ".xml")
    with open(filename, 'w') as out:
        out.write("<?xml version='1.0'?>\n<data>\n")
        out.write("<schedule name='" + timestr + "'>\n")

        out.write("<courseList>\n")
        for each_course in week.schedule.courses:
            out.write("<item code='%s' credit='%d' instructor='%s' capacity='%d' needs_computers='%s'></item>\n"\
                  % (each_course.code, each_course.credit, each_course.instructor, \
                    each_course.capacity, each_course.needs_computers))

        out.write("</courseList>\n")

        out.write("<roomList>\n")
        for each_room in week.days[0].rooms:
            out.write("<item building='%s' number='%d' capacity='%d' has_computers='%s'\n" \
                    % (each_room.building, each_room.number, each_room.capacity, \
                        each_room.has_computers))

        out.write("</roomList>\n")

        out.write("<timeList>\n")
        for each_slot in week.schedule.time_slots:
            out.write("<item>%s</item>\n" % (each_slot))
        out.write("</timeList>\n")

        out.write("<timeSlotDivide>" + str(week.schedule.slot_divide) + "</timeSlotDivide>\n")
        out.write("</schedule>\n")

        # create the all the courses
        courses_dyct = {
        }  # structure of {course_code : (day_code, room, start_time, end_time)}
        instructors = []
        for each_slot in week.list_time_slots():
            if each_slot.course != None:
                if courses_dyct.has_key(each_slot.course.code):
                    courses_dyct[each_slot.course.code][3] += each_slot.day
                else:
                    courses_dyct[each_slot.course.code] = \
                        [each_slot.course.credit, \
                         each_slot.start_time, each_slot.end_time, \
                         each_slot.day, each_slot.room.building + " " + each_slot.room.number, \
                         each_slot.instructor]
                    if each_slot.instructor not in instructors:
                        instructors.append(each_slot.instructor)

        for instructor in instructors:
            for key in instructor.courses:
                # course / credit / startTime / endTime / room number / instructor
                out.write("""<course
code="%s"
credit="%s"
startTime="%s"
endTime="%s"
days="%s"
room="%s"
instructor="%s">
</course>\n""" % (str(key), str(courses_dyct[key.code][0]),\
                str(courses_dyct[key.code][1])[:-3], str(courses_dyct[key.code][2])[:-3], courses_dyct[key.code][3],\
                courses_dyct[key.code][4], courses_dyct[key.code][5]))

        out.write("<extra>\n%s</extra>\n" % (extras))
        out.write("</data>")


def export_schedules(weeks, export_dir="./"):
    """Exports top 5 valid schedules to csv
    IN: list of week objects, export directory
    OUT: up to 5 csv files for top 5 valid schedules"""
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
    """Determine first-level prereqs from xml and list of all courses
    IN: path to xml file, list of course objects
    OUT: list of prereq objects"""
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
    """Extends prereqs for prereq of each prereq
    IN: list of prereq objects, list of all course objects
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
