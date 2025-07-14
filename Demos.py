from UserCreator import UserCreator
from Meetings import MeetingCreator


def run_demo1_1():  # Create Student Accounts
    creator = UserCreator()
    creator.delete_by_email(["Nick@testing.com", "Noah@testing.com"])
    print(creator.create_student_user(
        "Nick Bonilla",
        "Nick@testing.com",
        "psw123",
        "Student"
    ))

    print(creator.create_student_user(
        "Noah McClish",
        "Noah@testing.com",
        "psw123",
        "Student"
    ))

    print(creator.create_student_user(
        "Other Bonilla",
        "Nick@testing.com",
        "psw321",
        "Student"
    ))


def run_demo1_2():  # Create Tutor Account
    demo_dict = {
        'sunday': ["07:00", "09:00"],
        'monday': ["17:00", "19:00"],
        'tuesday': ["07:00", "09:00"],
        'wednesday': ["17:00", "19:00"],
        'thursday': ["00:00", "01:00"],
        'friday': ["05:00", "09:45"],
        'saturday': ["07:10", "09:50"]
    }

    creator = UserCreator()
    creator.delete_by_email(["Moises@testing.com"])
    print(creator.create_tutor_user(
        "Moises Sanchez",
        "Moises@testing.com",
        "123Password",
        "Tutor",
        ["computer science"],
        "5",
        demo_dict
    ))


def run_demo2_1():
    pass
