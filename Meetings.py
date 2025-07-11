from datetime import datetime

import bcrypt
from bson import ObjectId

import db

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


class MeetingCreator:

    def __init__(self):
        self.meetings = db["meetings"]  # Access the 'meetings' collection from the database

    def create_meeting(self, tutor_id, student_id, rating, comment, created_at, scheduled_time):
        # Create a dictionary containing the meetings information
        meeting_doc = {
            "tutorID": tutor_id,               # ID of the tutor involved in the meeting
            "studentID": student_id,           # ID of the student involved in the meeting
            "scheduledTime": scheduled_time,   # Time when the meeting is scheduled how
            "rating": rating,                  # Rating given to the tutor
            "comment": comment,                # Comments or feedback from the meeting
            "createdAt": created_at            # The time the meeting was created
        }
        self.meetings.insert_one(meeting_doc)  # Insert the meeting document into the 'meetings' collection
        return "Meeting Created"               #

    def tutor_rating(self, tutor_id): # get the average rating of each tutor
        meetings = self.meetings.find({"tutorID": tutor_id})
        total = 0
        count = 0
        for m in meetings:
            if "rating" in m:
                total += m["rating"]
                count += 1
            if count == 0:
                return "No meetings found"
            return round(total / count, 2)

    def update_rating(self, meeting_id, new_rating, new_comment=None): # user can update the rating after the meeting
        update_fields = {"rating": new_rating}
        if new_comment is not None:
            update_fields["comment"] = new_comment

        result = self.meetings.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            return "Meeting not found"
        return "Rating updated"





