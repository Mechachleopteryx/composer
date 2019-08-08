#!/usr/bin/env python

import datetime
import calendar

from ... import config
from ... import templates
from ... import utils
from ...errors import (
    DayStillInProgressError,
    LogfileLayoutError,
    LogfileNotCompletedError,
    PlannerIsInTheFutureError)
from ...utils import SECTION_HEADER_PATTERN


try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


MIN_WEEK_LENGTH = 5


class PeriodAdvanceCriteria(object):
    (Satisfied, DayStillInProgress, PlannerInFuture) = (1, 2, 3)


def check_logfile_completion(logfile):
    """ Check the logfile's NOTES section as a determination of whether the log has been completed """
    completed = False
    notes = ''
    ss = logfile.readline()
    while ss != '' and ss[:len('notes')].lower() != 'notes':
        ss = logfile.readline()
    if ss == '':
        raise LogfileLayoutError("Error: No 'NOTES' section found in your log file: " + ss)
    ss = logfile.readline()
    while ss != '' and not SECTION_HEADER_PATTERN.search(ss):
        notes += ss
        ss = logfile.readline()
    if notes.strip('\n ') != '':
        completed = True
    logfile.seek(0)
    return completed


def extract_agenda_from_logfile(logfile):
    """ Go through logfile and extract all tasks under AGENDA """
    agenda = ''
    ss = logfile.readline()
    while ss != '' and ss[:len('agenda')].lower() != 'agenda':
        ss = logfile.readline()
    if ss == '': raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
    ss = logfile.readline()
    while ss != '' and not SECTION_HEADER_PATTERN.search(ss):
        agenda += ss
        ss = logfile.readline()
    logfile.seek(0)
    agenda = agenda.strip('\n')
    return agenda


def update_logfile_agenda(logfile, agenda):
    logfile_updated = StringIO()
    ss = logfile.readline()
    while ss != '' and ss[:len('agenda')].lower() != 'agenda':
        logfile_updated.write(ss)
        ss = logfile.readline()
    if ss == '':
        raise LogfileLayoutError("No AGENDA section found in today's log file! Add one and try again.")
    logfile_updated.write(ss)
    ss = logfile.readline()
    while ss != '' and not SECTION_HEADER_PATTERN.search(ss):
        logfile_updated.write(ss)
        ss = logfile.readline()
    # don't leave newlines between previous tasks and latest additions
    logfile_updated.seek(logfile_updated.tell() - 2)
    if logfile_updated.read(2) == '\n\n':
        logfile_updated.seek(logfile_updated.tell() - 1)
    logfile_updated.write(agenda)
    logfile_updated.write('\n\n')
    while ss != '':
        logfile_updated.write(ss)
        ss = logfile.readline()

    logfile_updated.seek(0)
    return logfile_updated


def new_day_criteria_met(currentdate, now):
    today = now.date()
    if currentdate < today:
        return PeriodAdvanceCriteria.Satisfied
    if currentdate == today:
        if now.hour >= 18:
            return PeriodAdvanceCriteria.Satisfied
        else:
            # current day still in progress
            return PeriodAdvanceCriteria.DayStillInProgress
    else:
        # planner is in the future
        return PeriodAdvanceCriteria.PlannerInFuture


def new_month_criteria_met(currentdate, now):
    next_day = utils.get_next_day(currentdate)
    day_criteria_met = new_day_criteria_met(currentdate, now)
    if day_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
        return PeriodAdvanceCriteria.PlannerInFuture
    elif next_day.day == 1 and day_criteria_met == PeriodAdvanceCriteria.Satisfied:
        return PeriodAdvanceCriteria.Satisfied


def new_week_criteria_met(currentdate, now):
    # note that these dates are ~next~ day values
    dow = currentdate.strftime('%A')
    year = currentdate.year
    day_criteria_met = new_day_criteria_met(currentdate, now)
    if day_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
        return PeriodAdvanceCriteria.PlannerInFuture
    elif (new_month_criteria_met(currentdate, now) or
            (day_criteria_met == PeriodAdvanceCriteria.Satisfied
                and dow.lower() == 'saturday'
                and currentdate.day >= MIN_WEEK_LENGTH
                and calendar.monthrange(year, currentdate.month)[1] - currentdate.day >= MIN_WEEK_LENGTH)):
        return PeriodAdvanceCriteria.Satisfied


def new_quarter_criteria_met(currentdate, now):
    next_day = utils.get_next_day(currentdate)
    month = next_day.strftime('%B')
    day_criteria_met = new_day_criteria_met(currentdate, now)
    if day_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
        return PeriodAdvanceCriteria.PlannerInFuture
    elif new_month_criteria_met(currentdate, now) and month.lower() in ('january', 'april', 'july', 'october'):
        return PeriodAdvanceCriteria.Satisfied


def new_year_criteria_met(currentdate, now):
    next_day = utils.get_next_day(currentdate)
    month = next_day.strftime('%B')
    day_criteria_met = new_day_criteria_met(currentdate, now)
    if day_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
        return PeriodAdvanceCriteria.PlannerInFuture
    elif new_quarter_criteria_met(currentdate, now) and month.lower() == 'january':
        return PeriodAdvanceCriteria.Satisfied


def new_period_criteria_met(current_period, currentdate, now):
    if current_period == utils.PlannerPeriod.Day:
        return new_day_criteria_met(currentdate, now)
    if current_period == utils.PlannerPeriod.Week:
        return new_week_criteria_met(currentdate, now)
    if current_period == utils.PlannerPeriod.Month:
        return new_month_criteria_met(currentdate, now)
    if current_period == utils.PlannerPeriod.Quarter:
        return new_quarter_criteria_met(currentdate, now)
    if current_period == utils.PlannerPeriod.Year:
        return new_year_criteria_met(currentdate, now)


def advance_planner(planner, now=None):
    """ Advance planner state to next day, updating week and month info as necessary. 'now' arg used only for testing
    TODO: use function compositor thingies to de-duplify these
    """
    next_day = utils.get_next_day(planner.date)  # the new day to advance to
    # write_existing_week_template(next_day)
    # write_new_month_template(next_day)
    # sys.exit(0)
    # (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)

    if not now:
        now = datetime.datetime.now()

    def get_logfile(current_period):
        if current_period == utils.PlannerPeriod.Day:
            logfile = planner.dayfile
        elif current_period == utils.PlannerPeriod.Week:
            logfile = planner.weekfile
        elif current_period == utils.PlannerPeriod.Month:
            logfile = planner.monthfile
        elif current_period == utils.PlannerPeriod.Quarter:
            logfile = planner.quarterfile
        elif current_period == utils.PlannerPeriod.Year:
            logfile = planner.yearfile
        return logfile

    def get_period_name(current_period):
        periods = {utils.PlannerPeriod.Day: 'day', utils.PlannerPeriod.Week: 'week', utils.PlannerPeriod.Month: 'month',
                utils.PlannerPeriod.Quarter: 'quarter', utils.PlannerPeriod.Year: 'year'}
        return periods[current_period]

    def advance_period(current_period):
        """ Recursive function to advance planner by day, week, month, quarter, or year
        as the case may be.
        """
        period_criteria_met = new_period_criteria_met(current_period + 1, planner.date, now)
        if period_criteria_met == PeriodAdvanceCriteria.Satisfied:
            current_period += 1
            logfile = get_logfile(current_period)
            if config.PlannerConfig.LogfileCompletionChecking == config.LOGFILE_CHECKING['STRICT'] and not check_logfile_completion(logfile):
                periodstr = get_period_name(current_period)
                msg = "Looks like you haven't completed your %s's log. Would you like to do that now?" % periodstr
                raise LogfileNotCompletedError(msg, periodstr)
            templates.write_new_template(planner, current_period, next_day)

            if current_period < utils.PlannerPeriod.Year:
                return advance_period(current_period)
        elif period_criteria_met == PeriodAdvanceCriteria.DayStillInProgress:
            raise DayStillInProgressError("Current day is still in progress! Update after 6pm")
        elif period_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
            raise PlannerIsInTheFutureError("Planner is in the future!")
        else:
            templates.write_existing_template(planner, current_period + 1, next_day)
        return current_period

    status = advance_period(utils.PlannerPeriod.Zero)
    if status > utils.PlannerPeriod.Zero:
        planner.date = next_day

    return status


if __name__ == '__main__':
    pass