class StudentAcc:
    meetingList = []  # meetings they are leading (doesn't work with current meeting object implementation)

    def __init__(self, last_name):
        self.lastName = last_name


class TutorAcc:
    meetingList = []  # meetings they are leading (doesn't work with current meeting object implementation)
    subjectList = []  # subjects (as strings) they are proficient in

    def __init__(self, last_name, subjects=[]):
        self.lastName = last_name
        for item in subjects:
            self.subjectList.append(item)

# This entire file is likely going to be rewritten with proper logic for storing/retrieving user info
