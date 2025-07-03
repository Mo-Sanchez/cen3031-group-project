from user_types import *
from datetime import datetime


class Meeting:
    studentList = []

    def __init__(self, leader, day, month, year, hour, minute):
        self.leader = leader
        self.meetTime = datetime(year, month, day, hour, minute)

    def add_student(self, to_append):
        self.studentList.append(to_append)

    def remove_student(self, to_remove):
        for i in range(len(self.studentList)):
            if self.studentList[i].lastName == to_remove:
                self.studentList.pop(i)
                return True
        return False

    def print_details(self):  # debug function
        print(f"Meeting led by: {self.leader.lastName.capitalize()} on {self.meetTime}")
        print("Students Attending:")
        for item in self.studentList:
            print(item.lastName.capitalize())

    # def send_to_database
    # for when it's clear how these are going to be stored.
