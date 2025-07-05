from user_types import *
from datetime import datetime

FORMAT = '%Y-%m-%d %I:%M %p'  # constant

"""
meeting objects are composed of a meeting leader (as a TutorAcc object), a datetime object, and a list of 
StudentAcc objects.
"""


class Meeting:
    studentList = []

    def __init__(self, leader, date_string):  # date string is in the format "year-month-day hour:minute am/pm"
        self.leader = leader
        self.meetTime = datetime.strptime(date_string, FORMAT)

    def add_student(self, to_append):
        self.studentList.append(to_append)

    def remove_student(self, to_remove):
        for i in range(len(self.studentList)):
            if self.studentList[i].lastName == to_remove:
                self.studentList.pop(i)
                return True
        return False

    def print_details(self):  # debug function
        print(f"Meeting led by {self.leader.lastName.capitalize()} on {self.meetTime.strftime(FORMAT)}")
        print("Students Attending:")
        for item in self.studentList:
            print(item.lastName.capitalize())
