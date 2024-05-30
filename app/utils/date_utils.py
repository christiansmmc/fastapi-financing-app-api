import calendar
import locale
from datetime import datetime


def get_formatted_date(year_month: str):
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    date = datetime.strptime(year_month + "-01", "%Y-%m-%d")
    return date.strftime("%B %Y")


def get_first_late_date_from_year_month(year_month: str):
    year_month_formatted = datetime.strptime(year_month, "%Y-%m")

    first_day_of_month = year_month_formatted.replace(day=1).date()
    last_day_of_month = year_month_formatted.replace(
        day=calendar.monthrange(year_month_formatted.year, year_month_formatted.month)[
            1
        ]
    ).date()

    return first_day_of_month, last_day_of_month
