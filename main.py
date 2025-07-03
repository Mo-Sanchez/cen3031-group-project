from meetings import *
from month import Month
if __name__ == '__main__':
    student1 = StudentAcc("james")
    student2 = StudentAcc("john")
    student3 = StudentAcc("lucas")

    tutor1 = TutorAcc("bond")

    testMeet = Meeting(tutor1, 1, 2, 2025, 7, 30)
    testMeet.add_student(student1)
    testMeet.add_student(student2)
    testMeet.add_student(student3)
    testMeet.remove_student(student1)

    testMeet.print_details()

    testMonth = Month(6, 2025)
    testMonth.print_self()

    # just a testing file for now, will eventually house more functions relating to html
