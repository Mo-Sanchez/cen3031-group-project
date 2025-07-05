from UserLogin import UserLogin
from meetings import *
from month import Month
from UserCreator import UserCreator


if __name__ == '__main__':
    student1 = StudentAcc("james")
    student2 = StudentAcc("john")
    student3 = StudentAcc("lucas")

    tutor1 = TutorAcc("bond", ["algebra", "c++", "python"])

    tempString = "2025-07-04 8:01 pm"

    testMeet = Meeting(tutor1, tempString)
    testMeet.add_student(student1)
    testMeet.add_student(student2)
    testMeet.add_student(student3)
    testMeet.remove_student(student1)

    testMeet.print_details()

    testMonth = Month(7, 2025)
    testMonth.print_self()


# Create user
creator = UserCreator()
print(creator.create_user(
    "Moises Sanchez",
    "Moises@testing.com",
    "Password123",
    "Student",
    ["Computer Science"]
))

# User Login
login = UserLogin()
user_doc = login.login("Moises@testing.com", "Password123")

# If logged in, print name and role
if user_doc:
    print(user_doc["name"])
    print(user_doc["role"])
else:
    print("Invalid Credentials")
    # just a debug file for now, will eventually house more functions connecting to html
