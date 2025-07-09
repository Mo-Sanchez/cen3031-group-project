class UserAcc:
    def __init__(self, debug_flag, email, name=None, user_type=None, meeting_list=None, subject_list=None):
        self.email = email
        if debug_flag:  # Assigns these variables manually for testing purposes
            self.name = name  # simple "first last", we might need to prevent spaces in names in user creation
            self.user_type = user_type
            self.meeting_list = meeting_list
            self.subject_list = subject_list
        elif not debug_flag:
            print(end="")
            """
            Access database user storage to:
            1: find name
            2: find usertype
            3: find subject_list
            
            Access database meetings storage to:
            4: fill out meeting_list
            """
