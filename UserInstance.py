from db import db                      # import the shared db
from meetings import MeetingObj


class UserInstance:
    def __init__(self, user_id):
        self.users = db["users"]
        self.userID = user_id
        self.meetingList = []

        doc = self.users.find_one({"_id": self.userID})
        self.email = doc["email"]
        self.name = doc["name"]
        self.userType = doc["role"]
        if self.userType == "Student":  # Student account specific processes
            new_cursor = db.meetings.find({"studentID": self.userID})
        else:                           # Tutor account specific processes
            self.subjectList = doc["subjects"]
            self.availability = doc["availability"]
            new_cursor = db.meetings.find({"tutorID": self.userID})
        if new_cursor:  # only if meetings.find found anything
            for item in list(new_cursor):
                self.meetingList.append(MeetingObj(item))

    def update_meetings(self):
        self.meetingList = []
        if self.userType == "Student":
            new_cursor = db.meetings.find({"studentID": self.userID})
        else:
            new_cursor = db.meetings.find({"tutorID": self.userID})
        if new_cursor:  # only if meetings.find found anything
            for item in list(new_cursor):
                self.meetingList.append(MeetingObj(item["_id"]))

    def print_details(self):
        print(self.name)
        print(self.email)
        print(self.userType)
        for item in self.meetingList:
            print(item.scheduledTime)
        if self.userType == "Tutor":
            print(self.subjectList)
            print(self.availability)


    def get_user_information(self, user_email):
        user_info = self.users.find({"email": user_email})
        user_name = user_info["name"]
        user_role = user_info["role"]

        if user_role == "Tutor":
            user_availability = user_info["availability"]