from .... import utils  # TODO: eliminate this dependency?
from .day import DayTemplate
from .week import WeekTemplate
from .month import MonthTemplate
from .quarter import QuarterTemplate
from .year import YearTemplate


# Get the high level thing working first ("black box abstraction") and then improve it
# if necessary even consult the original interfaces and pass those args in, redundant though they may be
# do black formatting sooner rather than later, to minimize noise in spotting legitimate errors

def _get_template(planner, period, next_day):
    if period == utils.PlannerPeriod.Day:
        template = DayTemplate(planner, next_day)
    elif period == utils.PlannerPeriod.Week:
        template = WeekTemplate(planner, next_day)
    elif period == utils.PlannerPeriod.Month:
        template = MonthTemplate(planner, next_day)
    elif period == utils.PlannerPeriod.Quarter:
        template = QuarterTemplate(planner, next_day)
    elif period == utils.PlannerPeriod.Year:
        template = YearTemplate(planner, next_day)
    return template


def write_new_template(planner, period, next_day):
    template = _get_template(planner, period, next_day)
    template.write_new()


def write_existing_template(planner, period, next_day):
    template = _get_template(planner, period, next_day)
    template.write_existing()
