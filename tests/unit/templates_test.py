import datetime
import pytest

import composer.backend.filesystem.templates as templates
from composer.utils import PlannerPeriod

from .fixtures import planner


class TestNewTemplateIntegrity(object):
    """ Check that new templates generated by the planner are as expected """

    def test_month_template(self, planner):
        """ Test that month template is generated correctly by integrating checkpoints, periodic, etc."""
        now = datetime.datetime(2012, 12, 4, 18, 50, 30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)

        (date, month, year) = (
            next_day.day,
            next_day.strftime('%B'),
            next_day.year,
        )
        monthtemplate = "= %s %d =\n" % (month.upper(), year)
        monthtemplate += "\n"
        monthtemplate += "\t* [[Week of %s %d, %d]]\n" % (month, date, year)
        monthtemplate += "\n"
        monthtemplate += "CHECKPOINTS:\n"
        monthtemplate += planner.checkpoints_month_file.getvalue()
        monthtemplate += "\n"
        monthtemplate += "AGENDA:\n\n"
        monthtemplate += "MONTHLYs:\n"
        monthtemplate += planner.periodic_month_file.getvalue()
        monthtemplate += "\n"
        monthtemplate += "NOTES:\n\n\n"
        monthtemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, PlannerPeriod.Month, next_day)

        assert planner.monthfile.read() == monthtemplate

    def test_week_template(self, planner):
        """ Test that week template is generated correctly by integrating checkpoints, periodic, etc."""
        now = datetime.datetime(2012, 12, 4, 18, 50, 30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)

        (date, month, year) = (
            next_day.day,
            next_day.strftime('%B'),
            next_day.year,
        )
        weektemplate = (
            "= WEEK OF %s %d, %d =\n" % (month, date, year)
        ).upper()
        weektemplate += "\n"
        weektemplate += "\t* [[%s %d, %d]]\n" % (month, date, year)
        weektemplate += "\n"
        weektemplate += "CHECKPOINTS:\n"
        weektemplate += planner.checkpoints_week_file.getvalue()
        weektemplate += "\n"
        weektemplate += "AGENDA:\n\n"
        weektemplate += "WEEKLYs:\n"
        weektemplate += planner.periodic_week_file.getvalue()
        weektemplate += "\n"
        weektemplate += "NOTES:\n\n\n"
        weektemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, PlannerPeriod.Week, next_day)

        assert planner.weekfile.read() == weektemplate

    @pytest.mark.parametrize("offset", range(7))
    def test_daily_templates(self, planner, offset):
        """ Test that templates for each day are generated correctly by integrating checkpoints, periodic, etc.
        Currently only 2 templates - weekday, and weekend are used. TODO: Add individual templates for each day of the week """
        now = datetime.datetime(2012, 12, 7, 18, 50, 30)

        tasklist_nextday = (
            "TOMORROW:\n"
            "\n"
            "THIS WEEK:\n"
            "[\\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
            "[ ] help meags set up planner\n"
            "\t[x] create life mindmap with meags\n"
            "\t[x] incorporate life mindmap into planner with meags\n"
            "\t[x] swap meags' Esc and CapsLock on personal laptop\n"
            "\t[x] vim education and workflow\n"
            "\t[x] help meags build a routine of entering data for the day\n"
            "\t[ ] meags to schedule all activities (currently unscheduled)\n"
            "\t[ ] set up meags work laptop with vim/planner/truecrypt/dropbox\n"
            "\t[-] set up git access on your domain\n"
            "\t[ ] set up dropbox+truecrypt planner access for meags\n"
            "\n"
            "THIS MONTH:\n"
            "[ ] get India Tour reimbursement\n"
            "\t[x] resend all receipts and info to Amrit\n"
            "\t[x] send reminder email to Amrit\n"
            "\t[x] coordinate with amrit to go to stanford campus\n"
            "\t[x] remind amrit if no response\n"
            "\t[x] check Stanford calendar for appropriate time\n"
            "\t[x] email amrit re: thursday?\n"
            "\t[x] email amrit re: monday [$FRIDAY MORNING$]\n"
            "\t[x] wait for response\n"
            "\t[-] send reminder on Wed night\n"
            "\t[x] respond to amrit's email re: amount correction\n"
            "\t[x] wait to hear back [remind $MONDAY$]\n"
            "\t[-] followup with ASSU on reimbursement [$TUESDAY$]\n"
            "\t[x] pick up reimbursement, give difference check to raag\n"
            "\t[x] cash check\n"
            "\t[x] confirm deposit\n"
            "\t[ ] confirm debit of 810 by raag [$DECEMBER 10$]\n"
            "[ ] do residual monthlys\n"
            "[ ] get a good scratchy post for ferdy (fab?)\n"
            "\n"
            "UNSCHEDULED:\n"
            "\n"
            "SCHEDULED:\n"
        )

        now = now + datetime.timedelta(days=offset)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (
            next_day.day,
            next_day.strftime('%A'),
            next_day.strftime('%B'),
            next_day.year,
        )

        daythemes = (
            "SUNDAY: Groceries Day\n"
            "MONDAY: \n"
            "TUESDAY:Cleaning Day\n"
            "WEDNESDAY:\n"
            "THURSDAY:\n"
            "FRIDAY:\n"
            "SATURDAY: LAUNDRY DAY\n"
        )
        dailythemes = daythemes.lower()
        theme = dailythemes[dailythemes.index(day.lower()) :]
        theme = theme[theme.index(':') :].strip(': ')
        theme = theme[: theme.index('\n')].strip().upper()
        theme = "*" + theme + "*"

        daytemplate = ""
        daytemplate += "= %s %s %d, %d =\n" % (
            day.upper(),
            month[:3].upper(),
            date,
            year,
        )
        daytemplate += "\n"
        if len(theme) > 2:
            daytemplate += "Theme: %s\n" % theme
            daytemplate += "\n"
        daytemplate += "CHECKPOINTS:\n"
        if day.lower() in ('saturday', 'sunday'):
            daytemplate += planner.checkpoints_weekend_file.getvalue()
        else:
            daytemplate += planner.checkpoints_weekday_file.getvalue()
        daytemplate += "\n"
        daytemplate += "AGENDA:\n"
        daytemplate += "[ ] s'posed to do\n"
        daytemplate += "[\\] kinda did\n"
        daytemplate += "[ ] contact dude\n"
        daytemplate += "[\\] make X\n"
        daytemplate += "[ ] call somebody\n"
        daytemplate += "[ ] finish project\n"
        daytemplate += "\n"
        daytemplate += "DAILYs:\n"
        daytemplate += planner.periodic_day_file.getvalue()
        daytemplate += "\n"
        daytemplate += "NOTES:\n\n\n"
        daytemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, PlannerPeriod.Day, next_day)

        assert planner.dayfile.read() == daytemplate
        assert planner.tasklistfile.read() == tasklist_nextday


class TestExistingTemplateUpdateIntegrity(object):
    """ Check that updates on existing templates modifies the file as expected - does the right thing, does only that thing """

    def test_update_existing_month_template(self, planner):
        """ Check that writing over an existing month template adds the new week, and that there are no other changes """
        now = datetime.datetime(2012, 12, 4, 18, 50, 30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)

        monthtemplate_updated = (
            "= DECEMBER 2012 =\n"
            "\t* [[Week of December 5, 2012]]\n"
            "\t* [[Week of December 1, 2012]]\n"
            "\n"
            "CHECKPOINTS:\n"
            "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
            "\n"
            "AGENDA:\n"
            "\n"
            "MONTHLYs:\n"
            "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
            "\n"
            "NOTES:\n"
            "\n\n"
            "TIME SPENT ON PLANNER: "
        )

        templates.write_existing_template(
            planner, PlannerPeriod.Month, next_day
        )
        assert planner.monthfile.read() == monthtemplate_updated

    def test_update_existing_week_template(self, planner):
        """ Check that writing over an existing week template adds the new day, and that there are no other changes """
        now = datetime.datetime(2012, 12, 4, 18, 50, 30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)

        weektemplate_updated = (
            "= WEEK OF DECEMBER 1, 2012 =\n"
            "\n"
            "Theme: *WEEK OF THEME*\n"
            "\n"
            "\t* [[December 5, 2012]]\n"
            "\t* [[December 4, 2012]]\n"
            "\t* [[December 3, 2012]]\n"
            "\t* [[December 2, 2012]]\n"
            "\t* [[December 1, 2012]]\n"
            "\n"
            "CHECKPOINTS:\n"
            "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
            "\n"
            "AGENDA:\n"
            "\n"
            "WEEKLYs:\n"
            "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
            "\n"
            "NOTES:\n"
            "\n\n"
            "TIME SPENT ON PLANNER: "
        )

        templates.write_existing_template(
            planner, PlannerPeriod.Week, next_day
        )
        assert planner.weekfile.read() == weektemplate_updated
