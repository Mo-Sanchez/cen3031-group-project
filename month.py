import calendar
from datetime import datetime
from meetings import Meeting


class Month:
    def __init__(self, month, year):
        self.year = year
        self.month = month

        temp = datetime(year, month, 1)
        self.first_day = temp.weekday()
        # 0 = Monday, 1 = Tuesday, 6 = Sunday
        # may be needed for an offset when drawing calendar in html

    def print_self(self):
        print(calendar.month(self.year, self.month))

    # will house functions useful for searching, currently a skeleton
