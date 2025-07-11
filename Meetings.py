from db import db                      # import the shared db
from datetime import datetime

import bcrypt
from bson import ObjectId

FORMAT = '%Y-%m-%d %I:%M %p'  # constant

"""
date string is in the format "year-month-day hour:minute am/pm"
an example string is "2004-05-02 09:43 pm" for 9:43 PM on the 2nd of May, 2004
Strings in this format can easily be parsed to and from a datetime object.
datetime object to string via "datetime.strftime(FORMAT)" the 'f' in the function name is important
and string to datetime object via "datetime.strptime(datetime_object, FORMAT)" the 'p' is important
datetime objects store time in 24 hour time, but we can input and output in AM/PM time
"""


class MeetingObj:
    def __init__(self, meeting_id):
        self.meetings = db["meetings"]
        self.meetingID = meeting_id

        doc = self.meetings.find_one({"_id": self.meetingID})
        self.tutorID = doc["tutorID"]
        self.studentID = doc["studentID"]
        self.rating = doc["rating"]
        self.comment = doc["comment"]

        scheduled_raw = doc["scheduledTime"]
        self.scheduledTime = datetime.strptime(scheduled_raw, FORMAT)

        created_raw = doc["createdAt"]
        self.createdAt = datetime.strptime(created_raw, FORMAT)

    def print_details(self):  # debug function
        print(f"Meeting between {self.tutorID} and {self.studentID} on {self.scheduledTime.strftime(FORMAT)}")
        # additional debug info can be added here if needed


# stray debug print removed (would raise NameError)
# print(f"Meeting between {self.tutorID} and {self.studentID} on {self.scheduledTime.strftime(FORMAT)}")


def break_time(dictionary, day):
    """
        given a dictionary and a day,
        returns a list of all possible start times for 30 minute meetings in 24-hour string format
        EX: "19:21" for 7:21 pm, and "00:01" for 12:01 am.
    """
    times_list = []
    start, end = dictionary[day]
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


class MeetingCreator:
    def __init__(self):
        self.meetings = db["meetings"]

    def create_meeting(self, tutor_id, student_id, rating, comment, created_at, scheduled_time):
        meeting_doc = {
            "tutorID": tutor_id,
            "studentID": student_id,
            "scheduledTime": scheduled_time,
            "rating": rating,
            "comment": comment,
            "createdAt": created_at
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
