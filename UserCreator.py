import bcrypt
from db import db                      # import the shared db
#testing
class UserCreator:
    def __init__(self):
        self.users = db["users"]

    def create_user(self, name, email, password, role, subjects):
        if self.users.find_one({"email": email}):
            return "User already exists"

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
        doc = {
            "name": name,
            "email": email,
            "pwdHash": hashed,
            "role": role,
            "subjects": subjects
        }
        self.users.insert_one(doc)
        return "User created successfully"
