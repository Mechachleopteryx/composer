import datetime


class PlannerPeriod(object):
    (Zero, Day, Week, Month, Quarter, Year) = (0, 1, 2, 3, 4, 5)


class PlannerUserSettings(object):
    # TODO: put this on the Planner instance
    WeekTheme = None


def get_next_day(date):
    """ Given a date, return the next day by consulting the python date module """
    next_day = date + datetime.timedelta(days=1)
    return next_day
