import calendar
from datetime import datetime
from meetings import Meeting

const_months = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
const_days = {
    0 : "monday",
    1 : "tuesday",
    2 : "wednesday",
    3 : "thursday",
    4 : "friday",
    5 : "saturday",
    6 : "sunday"
}


class Day:
    def __init__(self, year, month, day, of_week):
        self.dtObj = datetime(year, month, day)
        self.meetingList = []
        self.dayOfWeek = const_days[of_week]


class Month:
    def __init__(self, month, year):
        self.year = year
        self.month = month
        self.dayList = []

        temp = datetime(year, month, 1)
        self.first_day = temp.weekday()
        # 0 = Monday, 1 = Tuesday, 6 = Sunday
        # may be needed for an offset when drawing calendar in html

        # Fill out dayList
        day_count = const_months[month]
        if year % 4 == 0 and month == 2:
            day_count = 29
        temp = self.first_day
        for i in range(1, day_count+1):
            self.dayList.append(Day(year, month, i, temp))
            temp += 1
            if temp == 7:
                temp = 0

    def print_self(self):
        print(calendar.month(self.year, self.month))
        temp = self.first_day
        for item in self.dayList:
            print(item.dtObj, end=" ")
            print(item.dayOfWeek)