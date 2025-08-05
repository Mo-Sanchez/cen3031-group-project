import bcrypt
from db import db                      # same shared db


#Handles user authentication by verifying email and password against stored user data
class UserLogin:
    def __init__(self):
        self.users = db["users"]
# Checks if user exists and verifies their password using bcrypt, returning the user document
    def login(self, email, password):
        user = self.users.find_one({"email": email})
        if not user:
            print("User Not Found")
            return None
        if bcrypt.checkpw(password.encode(), user["pwdHash"].encode()):
            return user
        else:
            print("Password Does Not Match")
        return None

