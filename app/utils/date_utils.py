import calendar
from datetime import datetime


class DateUtils:
    months_pt = {
        "January": "Janeiro",
        "February": "Fevereiro",
        "March": "Março",
        "April": "Abril",
        "May": "Maio",
        "June": "Junho",
        "July": "Julho",
        "August": "Agosto",
        "September": "Setembro",
        "October": "Outubro",
        "November": "Novembro",
        "December": "Dezembro",
    }

    @staticmethod
    def get_formatted_date(year_month: str) -> str:
        date = datetime.strptime(year_month + "-01", "%Y-%m-%d")
        month_english = date.strftime("%B")
        month_portuguese = DateUtils.months_pt[month_english]
        return f"{month_portuguese} {date.year}"

    @staticmethod
    def get_first_last_date_from_year_month(year_month: str):
        year_month_formatted = datetime.strptime(year_month, "%Y-%m")

        first_day_of_month = year_month_formatted.replace(day=1).date()
        last_day_of_month = year_month_formatted.replace(
            day=calendar.monthrange(
                year_month_formatted.year, year_month_formatted.month
            )[1]
        ).date()

        return first_day_of_month, last_day_of_month
