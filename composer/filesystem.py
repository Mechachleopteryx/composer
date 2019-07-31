import datetime
import os

from . import utils
from . import scheduling
from . import advanceplanner
from .planner import Planner
from .errors import (
    PlannerStateError,
    SimulationPassedError)


try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


PLANNERTASKLISTFILE = 'TaskList.wiki'
PLANNERDAYTHEMESFILELINK = 'DayThemes.wiki'
PLANNERDAYFILELINK = 'currentday'
PLANNERWEEKFILELINK = 'currentweek'
PLANNERMONTHFILELINK = 'currentmonth'
PLANNERQUARTERFILELINK = 'currentquarter'
PLANNERYEARFILELINK = 'currentyear'
CHECKPOINTSWEEKDAYFILE = 'Checkpoints_Weekday.wiki'
CHECKPOINTSWEEKENDFILE = 'Checkpoints_Weekend.wiki'
CHECKPOINTSWOLFFILE = 'Checkpoints_Wolf.wiki'
CHECKPOINTSTHEMANFILE = 'Checkpoints_TheMan.wiki'
CHECKPOINTSWEEKFILE = 'Checkpoints_Week.wiki'
CHECKPOINTSMONTHFILE = 'Checkpoints_Month.wiki'
CHECKPOINTSQUARTERFILE = 'Checkpoints_Quarter.wiki'
CHECKPOINTSYEARFILE = 'Checkpoints_Year.wiki'
PERIODICYEARLYFILE = 'Periodic_Yearly.wiki'
PERIODICQUARTERLYFILE = 'Periodic_Quarterly.wiki'
PERIODICMONTHLYFILE = 'Periodic_Monthly.wiki'
PERIODICWEEKLYFILE = 'Periodic_Weekly.wiki'
PERIODICDAILYFILE = 'Periodic_Daily.wiki'


def get_planner_date_from_string(datestr):
    return datetime.datetime.strptime(datestr, '%B %d, %Y').date()


def get_planner_date(plannerlocation):
    """ get planner date, currently looks for the file 'currentday', if dne throw exception """
    plannerdatelink = '%s/%s' % (plannerlocation, PLANNERDAYFILELINK)
    plannerdatefn = os.readlink(plannerdatelink)
    pathidx = plannerdatefn.rfind('/')
    datestr = plannerdatefn[pathidx + 1:-5]  # trim path from beginning and '.wiki' from end
    plannerdate = get_planner_date_from_string(datestr)
    return plannerdate


def construct_planner_from_filesystem(plannerpath):
    """ Construct a planner object from a filesystem representation."""
    # CURRENT planner date used here
    planner = Planner()
    planner.date = get_planner_date(plannerpath)
    tasklistfn = '%s/%s' % (plannerpath, PLANNERTASKLISTFILE)
    f = open(tasklistfn, 'r')
    planner.tasklistfile = StringIO(f.read())
    f.close()
    daythemesfn = '%s/%s' % (plannerpath, PLANNERDAYTHEMESFILELINK)
    f = open(daythemesfn, 'r')
    planner.daythemesfile = StringIO(f.read())
    f.close()
    dayfn_pre = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
    dayfn_pre = '%s/%s' % (plannerpath, os.readlink(dayfn_pre))
    f = open(dayfn_pre, 'r')
    planner.dayfile = StringIO(f.read())
    f.close()
    weekfn_pre = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
    weekfn_pre = '%s/%s' % (plannerpath, os.readlink(weekfn_pre))
    f = open(weekfn_pre, 'r')
    planner.weekfile = StringIO(f.read())
    f.close()
    monthfn_pre = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
    monthfn_pre = '%s/%s' % (plannerpath, os.readlink(monthfn_pre))
    f = open(monthfn_pre, 'r')
    planner.monthfile = StringIO(f.read())
    f.close()
    quarterfn_pre = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
    quarterfn_pre = '%s/%s' % (plannerpath, os.readlink(quarterfn_pre))
    f = open(quarterfn_pre, 'r')
    planner.quarterfile = StringIO(f.read())
    f.close()
    yearfn_pre = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
    yearfn_pre = '%s/%s' % (plannerpath, os.readlink(yearfn_pre))
    f = open(yearfn_pre, 'r')
    planner.yearfile = StringIO(f.read())
    f.close()

    # daily, weekly, monthly checkpoints, periodic items
    if utils.PlannerConfig.ScheduleMode == utils.PlannerConfig.Standard:
        fn = '%s/%s' % (plannerpath, CHECKPOINTSWEEKDAYFILE)
    elif utils.PlannerConfig.ScheduleMode == utils.PlannerConfig.TheMan:
        fn = '%s/%s' % (plannerpath, CHECKPOINTSTHEMANFILE)
    else:
        fn = '%s/%s' % (plannerpath, CHECKPOINTSWOLFFILE)
    f = open(fn, 'r')
    planner.checkpoints_weekday_file = StringIO(f.read())
    f.close()
    if utils.PlannerConfig.ScheduleMode == utils.PlannerConfig.Wolf:
        fn = '%s/%s' % (plannerpath, CHECKPOINTSWOLFFILE)
    else:
        fn = '%s/%s' % (plannerpath, CHECKPOINTSWEEKENDFILE)
    f = open(fn, 'r')
    planner.checkpoints_weekend_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, PERIODICDAILYFILE)
    f = open(fn, 'r')
    planner.periodic_day_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, CHECKPOINTSWEEKFILE)
    f = open(fn, 'r')
    planner.checkpoints_week_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, PERIODICWEEKLYFILE)
    f = open(fn, 'r')
    planner.periodic_week_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, CHECKPOINTSMONTHFILE)
    f = open(fn, 'r')
    planner.checkpoints_month_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, PERIODICMONTHLYFILE)
    f = open(fn, 'r')
    planner.periodic_month_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, CHECKPOINTSQUARTERFILE)
    f = open(fn, 'r')
    planner.checkpoints_quarter_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, PERIODICQUARTERLYFILE)
    f = open(fn, 'r')
    planner.periodic_quarter_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, CHECKPOINTSYEARFILE)
    f = open(fn, 'r')
    planner.checkpoints_year_file = StringIO(f.read())
    f.close()
    fn = '%s/%s' % (plannerpath, PERIODICYEARLYFILE)
    f = open(fn, 'r')
    planner.periodic_year_file = StringIO(f.read())
    f.close()

    return planner


def write_planner_to_filesystem(planner, plannerpath):
    """ Write the planner object to the filesystem at the given path."""
    pathspec = '{}/{}'
    tasklist_filename = pathspec.format(plannerpath, PLANNERTASKLISTFILE)
    day_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERDAYFILELINK))
    week_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERWEEKFILELINK))
    month_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERMONTHFILELINK))
    quarter_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERQUARTERFILELINK))
    year_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERYEARFILELINK))

    f = open(tasklist_filename, 'w')
    f.write(planner.tasklistfile.read())
    f.close()
    f = open(year_filename, 'w')
    f.write(planner.yearfile.read())
    f.close()
    f = open(quarter_filename, 'w')
    f.write(planner.quarterfile.read())
    f.close()
    f = open(month_filename, 'w')
    f.write(planner.monthfile.read())
    f.close()
    f = open(week_filename, 'w')
    f.write(planner.weekfile.read())
    f.close()
    f = open(day_filename, 'w')
    f.write(planner.dayfile.read())
    f.close()

    utils.reset_heads_on_planner_files(planner)


def advance_filesystem_planner(plannerpath, now=None, simulate=False):
    # use a bunch of StringIO buffers for the Planner object
    # populate them here from real files
    # after the advance() returns, the handles will be updated to the (possibly new) buffers
    # save to the known files here

    planner = construct_planner_from_filesystem(plannerpath)

    status = scheduling.schedule_tasks(planner, now)
    status = advanceplanner.advance_planner(planner, now)

    tasklistfn = '%s/%s' % (plannerpath, PLANNERTASKLISTFILE)
    dayfn_pre = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
    dayfn_pre = '%s/%s' % (plannerpath, os.readlink(dayfn_pre))
    weekfn_pre = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
    weekfn_pre = '%s/%s' % (plannerpath, os.readlink(weekfn_pre))
    monthfn_pre = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
    monthfn_pre = '%s/%s' % (plannerpath, os.readlink(monthfn_pre))
    quarterfn_pre = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
    quarterfn_pre = '%s/%s' % (plannerpath, os.readlink(quarterfn_pre))
    yearfn_pre = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
    yearfn_pre = '%s/%s' % (plannerpath, os.readlink(yearfn_pre))

    next_day = planner.date
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    # check for possible errors in planner state before making any changes
    if status >= utils.PlannerPeriod.Year:
        yearfn_post = '%s/%d.wiki' % (plannerpath, year)
        if os.path.isfile(yearfn_post): raise PlannerStateError("New year logfile already exists!")
    if status >= utils.PlannerPeriod.Quarter:
        quarterfn_post = '%s/%s %d.wiki' % (plannerpath, utils.quarter_for_month(month), year)
        if os.path.isfile(quarterfn_post): raise PlannerStateError("New quarter logfile already exists!")
    if status >= utils.PlannerPeriod.Month:
        monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
        if os.path.isfile(monthfn_post): raise PlannerStateError("New month logfile already exists!")
    if status >= utils.PlannerPeriod.Week:
        weekfn_post = '%s/Week of %s %d, %d.wiki' % (plannerpath, month, date, year)
        if os.path.isfile(weekfn_post): raise PlannerStateError("New week logfile already exists!")
    if status >= utils.PlannerPeriod.Day:
        dayfn_post = '%s/%s %d, %d.wiki' % (plannerpath, month, date, year)
        if os.path.isfile(dayfn_post): raise PlannerStateError("New day logfile already exists!")

    # if this is a simulation, we're good to go - let's break out of the matrix
    if status >= utils.PlannerPeriod.Day and simulate:
        raise SimulationPassedError('All systems GO', status)

    if status >= utils.PlannerPeriod.Year:
        # extract new year filename from date
        # write buffer to new file
        # update currentyear symlink
        yearfn_post = '%s/%d.wiki' % (plannerpath, year)
        f = open(yearfn_post, 'w')
        f.write(planner.yearfile.read())
        f.close()
        filelinkfn = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(yearfn_post[yearfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
    if status >= utils.PlannerPeriod.Quarter:
        # extract new quarter filename from date
        # write buffer to new file
        # update currentquarter symlink
        quarterfn_post = '%s/%s %d.wiki' % (plannerpath, utils.quarter_for_month(month), year)
        f = open(quarterfn_post, 'w')
        f.write(planner.quarterfile.read())
        f.close()
        filelinkfn = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(quarterfn_post[quarterfn_post.rfind('/') + 1:], filelinkfn) # remove path from filename so it isn't "double counted"
    if status == utils.PlannerPeriod.Quarter:
        # write year buffer to existing file
        f = open(yearfn_pre, 'w')
        f.write(planner.yearfile.read())
        f.close()
    if status >= utils.PlannerPeriod.Month:
        # extract new month filename from date
        # write buffer to new file
        # update currentmonth symlink
        monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
        f = open(monthfn_post, 'w')
        f.write(planner.monthfile.read())
        f.close()
        filelinkfn = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(monthfn_post[monthfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
    if status == utils.PlannerPeriod.Month:
        # write quarter buffer to existing file
        f = open(quarterfn_pre, 'w')
        f.write(planner.quarterfile.read())
        f.close()
    if status >= utils.PlannerPeriod.Week:
        # extract new week filename from date
        # write buffer to new file
        # update currentweek symlink
        weekfn_post = '%s/Week of %s %d, %d.wiki' % (plannerpath, month, date, year)
        f = open(weekfn_post, 'w')
        f.write(planner.weekfile.read())
        f.close()
        filelinkfn = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(weekfn_post[weekfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
    if status == utils.PlannerPeriod.Week:
        # write month buffer to existing file
        f = open(monthfn_pre, 'w')
        f.write(planner.monthfile.read())
        f.close()
    if status >= utils.PlannerPeriod.Day:
        # extract new day filename from date
        # write buffer to new file
        # update currentday symlink
        dayfn_post = '%s/%s %d, %d.wiki' % (plannerpath, month, date, year)
        f = open(dayfn_post, 'w')
        f.write(planner.dayfile.read())
        f.close()
        filelinkfn = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(dayfn_post[dayfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        # in any event if day was advanced, update tasklist
        f = open(tasklistfn, 'w')
        f.write(planner.tasklistfile.read())
        f.close()
    if status == utils.PlannerPeriod.Day:
        # write week buffer to existing file
        f = open(weekfn_pre, 'w')
        f.write(planner.weekfile.read())
        f.close()

    return status