import bcrypt

from db import db  # import the shared db

# Provided methods to create, modify, and delete student or tutor accounts in the database
class UserCreator:

    def __init__(self):
        self.users = db["users"]

#Creates a new student user if the email does not exist, hashing their password
    def create_student_user(self, name, email, password, role):
        if self.users.find_one({"email": email}):
            return False, "User already exists"

        doc = {
            "name": name,
            "email": email,
            "pwdHash": bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode(),
            "role": role
        }
        self.users.insert_one(doc)
        return True, "Student created"

    # Creates a new tutor user if the email does not exist, hashing their password

    def create_tutor_user(self, name, email, password, role,
                          subjects, start_avail, end_avail):
        if self.users.find_one({"email": email}):
            return False, "User already exists"

        doc = {
            "name": name,
            "email": email,
            "pwdHash": bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode(),
            "role": role,
            "subjects": subjects,
            "start_availability": start_avail,
            "end_availability": end_avail
        }

        self.users.insert_one(doc)
        return True, "Tutor created"


#deletes users whose emails are in the provided list
    def delete_by_email(self, email_list):
        for item in email_list:
            self.users.delete_one({"email" : item})

#changes the name field for a user with the specified email
    def change_name(self, email, name):
        self.users.update_one(
            {"email": email},
            {"$set": {"name": name}}
        )

# Updates the availability field for a tutor with the specified email
    def change_availability(self, email, availability):
        self.users.update_one(
            {"email": email, "role": "Tutor"},
            {"$set": {"availability": availability}}
        )
