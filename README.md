CSC-450-Scheduler
=================
Schedule all of the classes in the department for a given semester: specify the time and room for each class. The general constraint is that two classes should not be scheduled at the same time if they are likely to be taken concurrently. For example, CSC electives should not be scheduled concurrently if at all possible. And obviously the same instructor can't teach two different classes at the same time.

There will be additional constraints. For example, Dr. Shade does not like TR classes, classes that meet early in the morning, classes that meet in the late afternoon, or lecture classes that are held in a computer lab. A class may be partially specified: for example, CSC 131 must be a TR class in Cheek 209 or Cheek 210. No instructor should have more than two classes in a row. No instructor should have consecutive classes in different buildings.

The program must analyze the prerequisite structure of classes (including required MTH and PHY classes) to determine which classes can be scheduled concurrently. There should be a way to add additional constraints.
