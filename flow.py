def main():
    subject = raw_input("Which type of constraint? [instructor / course] ").lower() #button
    while (1):
        if subject in ["instructor", "course"]:
            break
        else:
            subject = raw_input("Invalid input. [instructor / course] ").lower()
    if subject == "instructor":
        instructor = raw_input("Which instructor? ").lower()
    elif subject == "course":
        course = "CSC" # not sure if this should be assumed or an option?
        num = int(raw_input("Which course number (e.g. 450)? "))
    const_type = raw_input("Which type of constraint [time / location / lab]? ").lower() #button
    while (1):
        if const_type in ["time", "location", "lab"]:
            break
        else:
            const_type = raw_input("Invalid input. [time / location / lab] ").lower()
    if const_type == "time":
        time_type = raw_input("Before or after? ").lower() #dropdown
        while (1):
            if time_type in ["before", "after"]:
                break
            else:
                time_type = raw_input("Invalid input. [before / after] ").lower()
        time = raw_input("What time in military time (e.g. 13:00)? ")
    elif const_type == "location":
        building = raw_input("Which building code (e.g. CHK)? ") #dropdown
        room = int(raw_input("Which room (e.g. 204)? ")) #dropdown
    elif const_type == "lab":
        lab = raw_input("Should the course / instructor be in a lab [yes / no]? ").lower() #dropdown
        while (1):
            if lab in ["yes", "y"]:
                lab = True
                break
            elif lab in ["no", "n"]:
                lab = False
                break
            else:
                lab = raw_input("Invalid input. [yes / no] ").lower()


if __name__ == "__main__":
    main()