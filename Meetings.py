from db import db                      # import the shared db
from datetime import datetime

import bcrypt
from bson import ObjectId

FORMAT = '%Y-%m-%d %I:%M %p'  # constant

"""
date string is in the format "year-month-day hour:minute am/pm"
an example string is "2004-05-02 09:43 pm" for 9:43 PM on the 2nd of May, 2004
Strings in this format can easily be parsed to and from a datetime object.
datetime object to string via "datetime_object.strftime(FORMAT)" the 'f' in the function name is important
and string to datetime object via "datetime.strptime(datetime_object, FORMAT)" the 'p' is important
datetime objects store time in 24 hour format, but we can handle input and output in AM/PM time
"""


def break_time(start_time, end_time):
    """
        given a start and end time in 24h format,
        returns a list of all possible start times for 30 minute meetings in 24-hour string format
        EX: "19:21" for 7:21 pm, and "00:01" for 12:01 am.
    """
    times_list = []
    start, end = start_time, end_time
    start_parse_1, start_parse_2 = start.split(':')
    end_parse_1, end_parse_2 = end.split(':')

    int_start = [int(start_parse_1), int(start_parse_2)]
    int_end = [int(end_parse_1), int(end_parse_2)]

    meeting_count = 2 * (int_end[0] - int_start[0])

    diff = int_end[1] - int_start[1]
    if diff < -30:
        meeting_count -= 2
    elif diff < 0:
        meeting_count -= 1
    elif diff >= 30:
        meeting_count += 1

    for _ in range(meeting_count):
        times_list.append(f"{str(int_start[0]).zfill(2)}:{str(int_start[1]).zfill(2)}")
        int_start[1] += 30
        if int_start[1] >= 60:
            int_start[0] += 1
            int_start[1] -= 60
    return times_list


class MeetingObj:
    def __init__(self, meeting_id):
        self.meetings = db["meetings"]
        self.users = db["users"]
        self.meetingID = meeting_id

        # store basic information
        doc = self.meetings.find_one({"_id": self.meetingID})
        self.tutorID = doc["tutorID"]
        self.studentID = doc["studentID"]
        self.rating = doc["rating"]
        self.comment = doc["comment"]

        # store names for frontend purposes
        tutor_doc = self.users.find_one({"_id": self.tutorID})
        self.tutorName = tutor_doc["name"]

        student_doc = self.users.find_one({"_id": self.studentID})
        self.studentName = student_doc["name"]

        scheduled_raw = doc["scheduledTime"]
        self.scheduledTime = datetime.strptime(scheduled_raw, FORMAT)

        created_raw = doc["createdAt"]
        self.createdAt = datetime.strptime(created_raw, FORMAT)

    def print_details(self):
        print(f"Meeting between {self.tutorName} and {self.studentName} on {self.scheduledTime.strftime(FORMAT)}")


class MeetingCreator:
    def __init__(self):
        self.meetings = db["meetings"]
        self.users = db["users"]

    def create_meeting(self, tutor_email, student_email, scheduled_date,scheduled_time,subject):
        meeting_doc = {
            "tutorEmail": tutor_email,
            "studentEmail": student_email,
            "scheduledDate": scheduled_date,
            "scheduledTime": scheduled_time,
            "subject": subject
        }
        self.meetings.insert_one(meeting_doc)
        return "Meeting Created"

    def tutor_rating(self, tutor_id):
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

    def update_rating(self, meeting_id, new_rating, new_comment=None):
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

    def delete_by_tutorID(self, tutor_id):
        self.meetings.delete_many({"tutorID": tutor_id})

    def search_by_date_and_subject(self, date, subject):
        """
        filters by a subject, and checks if they have availability that day.
        Returns a list of tutors available tutors with their information accessible by dictionary
        """
        tutor_list = []
        temp_cursor = self.users.find({"subjects": {"$in": [subject]}})
        temp_list = list(temp_cursor)

        if temp_cursor:
            print(f"{len(temp_list)} tutors found!")
            for user in temp_list:
                # check if they're fully booked that day
                broken_time = break_time(user["start_availability"], user["end_availability"])
                fully_booked = True
                for time in broken_time:
                    clash = self.meetings.find_one({
                        "tutorEmail": user["email"],
                        "scheduledDate": date,
                        "scheduledTime": time
                    })
                    if not clash:
                        fully_booked = False
                if not fully_booked:
                    tutor_list.append(user)
                    print(user["name"], end="")
                    print(" added!")
                else:
                    print(user["name"], end="")
                    print(" was fully booked!")
        else:
            print("no tutors found")
        return tutor_list
