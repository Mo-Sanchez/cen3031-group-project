from datetime import datetime

FORMAT = '%Y-%m-%d %I:%M %p'  # constant

"""
meeting objects are composed of a meeting leader (as a TutorAcc object), a datetime object, and a list of 
StudentAcc objects.
"""


class Meeting:
    def __init__(self, leader, date_string, duration, max_attendance, subject_list):
        self.leader = leader  # email address as a string
        self.meetTime = datetime.strptime(date_string, FORMAT)  # date string is in the format "year-month-day hour:minute am/pm"
        self.duration = duration
        self.max_attendance = max_attendance
        self.subject_list = subject_list

        self.studentList = []
        self.currCount = 0

    def add_student(self, to_append):
        if self.currCount >= self.max_attendance:
            return False
        for i in range(len(self.studentList)):
            if self.studentList[i] == to_append:
                return False
        self.studentList.append(to_append)
        self.currCount += 1
        return True

    def remove_student(self, to_remove):
        for i in range(len(self.studentList)):
            if self.studentList[i] == to_remove:
                self.studentList.pop(i)
                self.currCount -= 1
                return True
        return False

    def print_details(self):  # debug function
        print(f"Meeting led by {self.leader} on {self.meetTime.strftime(FORMAT)}")
        print("Students Attending:")
        for item in self.studentList:
            print(item)
            