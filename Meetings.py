from db import db                      # import the shared db
from datetime import datetime

FORMAT = '%Y-%m-%d %I:%M %p'  # important constant
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

        meeting_count = (2 * (int_end[0] - int_start[0]))

        diff = int_end[1] - int_start[1]
        if diff < -30:
            meeting_count -= 2
        elif diff < 0:
            meeting_count -= 1
        elif diff >= 30:
            meeting_count += 1

        for i in range(meeting_count):
            temp = "Null"
            temp = str(int_start[0]).zfill(2) + ':' + str(int_start[1]).zfill(2)
            int_start[1] += 30
            if int_start[1] >= 60:
                int_start[0] += 1
                int_start[1] -= 60
            times_list.append(temp)
        return times_list
