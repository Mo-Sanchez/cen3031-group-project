class StudentAcc:
    def __init__(self, last_name):
        self.lastName = last_name


class TutorAcc:
    subjectList = []  # subjects (as strings probably, could be stored in a constant dict) they are proficient in

    def __init__(self, last_name, subjects=[]):
        self.lastName = last_name
        for item in subjects:
            self.subjectList.append(item)

# file needs heavy work in regard to user data/passwords/login implementation
