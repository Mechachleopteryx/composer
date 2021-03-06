import datetime
import re

from ...errors import RelativeDateError
from ...timeperiod import (
    get_next_day,
    get_next_month,
    Day,
    Week,
    Month,
    Quarter,
    Year,
    Eternity,
    month_for_quarter,
    quarter_for_month,
    get_month_name,
    get_month_number,
    day_of_week,
    upcoming_dow_to_date,
)

# TODO: change these to annotated regex's

# MONTH DD, YYYY (w optional space or comma or both)
dateformat1 = re.compile(r"^([^\d ]+) (\d\d?)[, ] ?(\d{4})$", re.IGNORECASE)
# DD MONTH, YYYY (w optional space or comma or both)
dateformat2 = re.compile(r"^(\d\d?) ([^\d,]+)[, ] ?(\d{4})$", re.IGNORECASE)
# MONTH DD
dateformat3 = re.compile(r"^([^\d ]+) (\d\d?)$", re.IGNORECASE)
# DD MONTH
dateformat4 = re.compile(r"^(\d\d?) ([^\d]+)$", re.IGNORECASE)
# WEEK OF MONTH DD, YYYY (w optional space or comma or both)
dateformat5 = re.compile(
    r"^WEEK OF ([^\d ]+) (\d\d?)[, ] ?(\d{4})$", re.IGNORECASE
)
# WEEK OF DD MONTH, YYYY (w optional space or comma or both)
dateformat6 = re.compile(
    r"^WEEK OF (\d\d?) ([^\d,]+)[, ] ?(\d{4})$", re.IGNORECASE
)
# WEEK OF MONTH DD
dateformat7 = re.compile(r"^WEEK OF ([^\d ]+) (\d\d?)$", re.IGNORECASE)
# WEEK OF DD MONTH
dateformat8 = re.compile(r"^WEEK OF (\d\d?) ([^\d,]+)$", re.IGNORECASE)
# MONTH YYYY (w optional space or comma or both)
dateformat9 = re.compile(r"^([^\d, ]+)[, ] ?(\d{4})$", re.IGNORECASE)
# MONTH
dateformat10 = re.compile(r"^([^\d ]+)$", re.IGNORECASE)
# MM/DD/YYYY
dateformat11 = re.compile(r"^(\d\d)/(\d\d)/(\d\d\d\d)$", re.IGNORECASE)
# MM-DD-YYYY
dateformat12 = re.compile(r"^(\d\d)-(\d\d)-(\d\d\d\d)$", re.IGNORECASE)
# TOMORROW
dateformat13 = re.compile(r"^TOMORROW$", re.IGNORECASE)
# TODO: need a function to test date boundary status and return
# monthboundary, weekboundary, or dayboundary (default)
# NEXT WEEK
dateformat14 = re.compile(r"^NEXT WEEK$", re.IGNORECASE)
# NEXT MONTH
dateformat15 = re.compile(r"^NEXT MONTH$", re.IGNORECASE)
# <DOW>
dateformat16 = re.compile(
    r"^(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)$",
    re.IGNORECASE,
)
# <DOW> (abbrv.)
dateformat17 = re.compile(r"^(MON|TUE|WED|THU|FRI|SAT|SUN)$", re.IGNORECASE)
# QN YYYY
dateformat18 = re.compile(r"^(Q\d) (\d{4})$", re.IGNORECASE)
# NEXT YEAR
dateformat19 = re.compile(r"^NEXT YEAR$", re.IGNORECASE)
# YYYY
dateformat20 = re.compile(r"^(\d\d\d\d)$", re.IGNORECASE)
# THIS WEEKEND
dateformat21 = re.compile(r"^THIS WEEKEND$", re.IGNORECASE)
# NEXT WEEKEND
dateformat22 = re.compile(r"^NEXT WEEKEND$", re.IGNORECASE)
# NEXT QUARTER
dateformat23 = re.compile(r"^NEXT QUARTER$", re.IGNORECASE)
# QN
dateformat24 = re.compile(r"^(Q\d)$", re.IGNORECASE)
# DAY AFTER TOMORROW
dateformat25 = re.compile(r"^DAY AFTER TOMORROW$", re.IGNORECASE)
# SOMEDAY
dateformat26 = re.compile(r"^SOMEDAY$", re.IGNORECASE)
# WEEK AFTER NEXT
dateformat27 = re.compile(r"^WEEK AFTER NEXT$", re.IGNORECASE)
# <NTH> WEEK OF <MONTH>
dateformat28 = re.compile(
    r"^(FIRST|SECOND|THIRD|FOURTH|LAST) WEEK OF ([^\d]+)$", re.IGNORECASE
)


def get_appropriate_year(month, day, reference_date):
    """For date formats where the year is unspecified, determine the
    appropriate year by ensuring that the resulting date is in the future.

    :param int month: Indicated month
    :param int day: Indicated day
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns int: The appropriate year for the date
    """
    # if current year would result in negative, then use next year,
    # otherwise current year
    date_thisyear = datetime.date(reference_date.year, month, day)
    if date_thisyear < reference_date:
        return reference_date.year + 1
    else:
        return reference_date.year


def parse_dateformat1(date_string, reference_date=None):
    """Parse date format
        MONTH DD, YYYY (w optional space or comma or both)
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    (month, day, year) = dateformat1.search(date_string).groups()
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat2(date_string, reference_date=None):
    """Parse date format
        DD MONTH, YYYY (w optional space or comma or both)
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    (day, month, year) = dateformat2.search(date_string).groups()
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat3(date_string, reference_date=None):
    """Parse date format
        MONTH DD
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (month, day) = dateformat3.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    year = str(get_appropriate_year(monthn, dayn, reference_date))
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat4(date_string, reference_date=None):
    """Parse date format
        DD MONTH
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (day, month) = dateformat4.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    year = str(get_appropriate_year(monthn, dayn, reference_date))
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat5(date_string, reference_date=None):
    """Parse date format
        WEEK OF MONTH DD, YYYY (w optional space or comma or both)
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    # std = Week of Month dd(sunday/1), yyyy
    (month, day, year) = dateformat5.search(date_string).groups()
    (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat6(date_string, reference_date=None):
    """Parse date format
        WEEK OF DD MONTH, YYYY (w optional space or comma or both)
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    (day, month, year) = dateformat6.search(date_string).groups()
    (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat7(date_string, reference_date=None):
    """Parse date format
        WEEK OF MONTH DD
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (month, day) = dateformat7.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    yearn = get_appropriate_year(monthn, dayn, reference_date)
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat8(date_string, reference_date=None):
    """Parse date format
        WEEK OF DD MONTH
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (day, month) = dateformat8.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    yearn = get_appropriate_year(monthn, dayn, reference_date)
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat9(date_string, reference_date=None):
    """Parse date format
        MONTH YYYY (w optional space or comma or both)
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    (month, year) = dateformat9.search(date_string).groups()
    day = str(1)
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Month
    return date, period


def parse_dateformat10(date_string, reference_date=None):
    """Parse date format
        MONTH
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    month = dateformat10.search(date_string).groups()[0]
    (monthn, dayn) = (get_month_number(month), 1)
    (day, year) = (
        str(dayn),
        str(get_appropriate_year(monthn, dayn, reference_date)),
    )
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Month
    return date, period


def parse_dateformat11(date_string, reference_date=None):
    """Parse date format
        MM/DD/YYYY
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    (monthn, dayn, yearn) = map(int, dateformat11.search(date_string).groups())
    date = datetime.date(yearn, monthn, dayn)
    period = Day
    return date, period


def parse_dateformat12(date_string, reference_date=None):
    """Parse date format
        MM-DD-YYYY
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    (monthn, dayn, yearn) = map(int, dateformat12.search(date_string).groups())
    date = datetime.date(yearn, monthn, dayn)
    period = Day
    return date, period


def parse_dateformat13(date_string, reference_date=None):
    """Parse date format
        TOMORROW
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = get_next_day(reference_date)
    period = Day
    return date, period


def _weeks_from(how_many, reference_date):
    date = reference_date
    while how_many > 0:
        week_end_date = Week.get_end_date(date)
        if week_end_date == date:
            # on Saturday, "next week" means a week later
            week_end_date = Week.get_end_date(
                date + datetime.timedelta(days=1)
            )
        date = week_end_date + datetime.timedelta(days=1)
        how_many -= 1
    return date


def parse_dateformat14(date_string, reference_date=None):
    """Parse date format
        NEXT WEEK
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = _weeks_from(1, reference_date)
    period = Week
    return date, period


def parse_dateformat15(date_string, reference_date=None):
    """Parse date format
        NEXT MONTH
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    month_end = Month.get_end_date(reference_date)
    date = month_end + datetime.timedelta(days=1)
    if month_end == reference_date:
        # on the last day of the month, we mean the following month,
        # not tomorrow. although, maybe we should broaden this handling
        # to the last week of the month and not just the last day
        date = Month.get_end_date(date) + datetime.timedelta(days=1)
    period = Month
    return date, period


def parse_dateformat16(date_string, reference_date=None):
    """Parse date format
        <DOW>
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    dowToSchedule = dateformat16.search(date_string).groups()[0]
    upcomingweek = [
        reference_date + datetime.timedelta(days=d) for d in range(1, 8)
    ]
    dow = [d.strftime("%A").upper() for d in upcomingweek]
    date = upcomingweek[dow.index(dowToSchedule)]
    period = Day
    return date, period


def parse_dateformat17(date_string, reference_date=None):
    """Parse date format
        <DOW> (abbrv.)
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    dowToSchedule = dateformat17.search(date_string).groups()[0]
    upcomingweek = [
        reference_date + datetime.timedelta(days=d) for d in range(1, 8)
    ]
    dow = [d.strftime("%a").upper() for d in upcomingweek]
    date = upcomingweek[dow.index(dowToSchedule)]
    period = Day
    return date, period


def parse_dateformat18(date_string, reference_date=None):
    """Parse date format
        QN YYYY
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    (quarter, year) = dateformat18.search(date_string).groups()
    month = month_for_quarter(quarter)
    month = get_month_name(month)
    day = str(1)
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Quarter
    return date, period


def parse_dateformat19(date_string, reference_date=None):
    """Parse date format
        NEXT YEAR
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = Year.get_end_date(reference_date) + datetime.timedelta(days=1)
    period = Year
    return date, period


def parse_dateformat20(date_string, reference_date=None):
    """Parse date format
        YYYY
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    year = int(dateformat20.search(date_string).groups()[0])
    date = datetime.date(year, 1, 1)
    period = Year
    return date, period


def parse_dateformat21(date_string, reference_date=None):
    """Parse date format
        THIS WEEKEND
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    if day_of_week(reference_date).lower() == 'saturday':
        date = reference_date
    else:
        date = upcoming_dow_to_date('saturday', reference_date)
    period = Day
    return date, period


def parse_dateformat22(date_string, reference_date=None):
    """Parse date format
        NEXT WEEKEND
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = upcoming_dow_to_date("saturday", reference_date)
    if day_of_week(reference_date).lower() != 'saturday':
        date = upcoming_dow_to_date("saturday", date)
    period = Day
    return date, period


def parse_dateformat23(date_string, reference_date=None):
    """Parse date format
        NEXT QUARTER
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = Quarter.get_end_date(reference_date) + datetime.timedelta(days=1)
    period = Quarter
    return date, period


def parse_dateformat24(date_string, reference_date=None):
    """Parse date format
        QN
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    quarter = dateformat24.search(date_string).groups()[0]
    # start date of next quarter
    date = Quarter.get_end_date(reference_date) + datetime.timedelta(days=1)
    next_quarter = quarter_for_month(date.month)
    # find the specified quarter
    while next_quarter != quarter:
        date = Quarter.get_end_date(date) + datetime.timedelta(days=1)
        next_quarter = quarter_for_month(date.month)
    period = Quarter
    return date, period


def parse_dateformat25(date_string, reference_date=None):
    """Parse date format
        DAY AFTER TOMORROW
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = get_next_day(get_next_day(reference_date))
    period = Day
    return date, period


def parse_dateformat26(date_string, reference_date=None):
    """Parse date format
        SOMEDAY
    This is a special date format indicating a "suspended" task. For the
    task scheduling logic to handle it appropriately we return a date in
    the distant future.

    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    date = Eternity.get_end_date()
    period = Eternity
    return date, period


def parse_dateformat27(date_string, reference_date=None):
    """Parse date format
        WEEK AFTER NEXT
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    week_end_date = Week.get_end_date(reference_date)
    if week_end_date == reference_date:
        # on Saturday, "next week" means a week later
        week_end_date = Week.get_end_date(
            reference_date + datetime.timedelta(days=1)
        )
    next_week_start = week_end_date + datetime.timedelta(days=1)
    date = Week.get_end_date(next_week_start) + datetime.timedelta(days=1)
    period = Week
    return date, period


def parse_dateformat28(date_string, reference_date=None):
    """Parse date format
        (FIRST|SECOND|THIRD|FOURTH|LAST) WEEK OF <MONTH|THE MONTH>
    :param str date_string: The string representation of the date
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns tuple: The parsed date, together with the relevant time period.
    """
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    which_week = dateformat28.search(date_string).groups()[0]
    month_string = dateformat28.search(date_string).groups()[1]
    if month_string == "THE MONTH":
        (monthn, dayn) = (reference_date.month, 1)
        month = get_month_name(monthn)
    else:
        month = month_string
        (monthn, dayn) = (get_month_number(month), 1)
    (day, year) = (
        str(dayn),
        str(get_appropriate_year(monthn, dayn, reference_date)),
    )
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    if (
        month_string == "THE MONTH"
        and date - reference_date > datetime.timedelta(weeks=5)
    ):
        # eg. "first week of the month" in the last week
        # of the month means the following month
        date = get_next_month(reference_date)
    if which_week == "FIRST":
        how_many_weeks = 0
    elif which_week == "SECOND":
        how_many_weeks = 1
    elif which_week == "THIRD":
        how_many_weeks = 2
    elif which_week == "FOURTH":
        how_many_weeks = 3
    elif which_week == "LAST":
        how_many_weeks = 3
    date = _weeks_from(how_many_weeks, date)
    if which_week == "LAST":
        following_week_start = _weeks_from(1, date)
        if following_week_start.month == date.month:
            date = following_week_start
    period = Week
    return date, period
