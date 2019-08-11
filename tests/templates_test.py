import datetime
import unittest

import composer.backend.filesystem.templates as templates
from composer.utils import PlannerPeriod

from .fixtures import PlannerMock

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


class PlannerNewTemplateIntegrityTester(unittest.TestCase):
    """ Check that new templates generated by the planner are as expected """

    tasklist = ("TOMORROW:\n"
                    "[ ] contact dude\n"
                    "[\] make X\n"
                    "[ ] call somebody\n"
                    "[ ] finish project\n"
                    "\n"
                    "THIS WEEK:\n"
                    "[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
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
                    "SCHEDULED:\n")

    tasklist_nextday = ("TOMORROW:\n"
                    "\n"
                    "THIS WEEK:\n"
                    "[\] write a script to automatically pull from plan files into a current day in planner (replacing template files)\n"
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
                    "SCHEDULED:\n")

    monthtemplate = ("= DECEMBER 2012 =\n"
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
                    "TIME SPENT ON PLANNER: ")

    weektemplate = ("= WEEK OF DECEMBER 1, 2012 =\n"
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
                    "TIME SPENT ON PLANNER: ")

    daytemplate = ("CHECKPOINTS:\n"
                    "[x] 7:00am - wake up [9:00]\n"
                    "[x] 7:05am - brush + change [11:00]\n"
                    "[ ] 7:10am - protein []\n"
                    "[ ] 7:15am - gym []\n"
                    "[x] 8:00am - shower [11:10]\n"
                    "[ ] 11:05pm - $nasal irrigation$ []\n"
                    "[x] 11:10pm - update schedule [12:25]\n"
                    "[x] 11:15pm - get stuff ready for morning((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones) [8:45]\n"
                    "[x] 11:30pm - sleep [12:45]\n"
                    "\n"
                    "AGENDA:\n"
                    "[x] did do\n"
                        "\t[x] this\n"
                        "\t[x] and this\n"
                    "[ ] s'posed to do\n"
                    "[\] kinda did\n"
                    "[o] i'm waitin on you!\n"
                    "[x] take out trash\n"
                    "[x] floss\n"
                    "\n"
                    "DAILYs:\n"
                    "[ ] 40 mins gym\n"
                    "[x] Make bed\n"
                    "[x] 5 mins housework (dishes, clearing, folding, trash, ...)\n"
                    "\n"
                    "NOTES:\n"
                    "\n"
                    "\n"
                    "TIME SPENT ON PLANNER: 15 mins")

    checkpoints_month = "[ ] WEEK 1 - []\n[ ] WEEK 2 - []\n[ ] WEEK 3 - []\n[ ] WEEK 4 - []\n"
    checkpoints_week = "[ ] SUN - []\n[ ] MON - []\n[ ] TUE - []\n[ ] WED - []\n[ ] THU - []\n[ ] FRI - []\n[ ] SAT - []\n"
    checkpoints_weekday = ("[ ] 7:00am - wake up []\n[ ] 7:05am - brush + change []\n[ ] 7:10am - protein []\n"
            "[ ] 7:15am - gym []\n[ ] 8:00am - shower []\n[ ] 8:15am - dump []\n"
            "[ ] 11:00pm - (start winding down) brush []\n[ ] 11:05pm - $nasal irrigation$ []\n"
            "[ ] 11:10pm - update schedule []\n[ ] 11:15pm - get stuff ready for morning"
            "((1) clothes:shirt,underwear,jeans,jacket,belt; (2) laptop+charger; (3) binder+texts+pen+pencil; (4) headphones"
            ") []\n[ ] 11:30pm - sleep []\n")
    checkpoints_weekend = ("[ ] 8:00am - wake up []\n[ ] 8:05am - brush + change []\n[ ] 8:10am - protein []\n"
            "[ ] 8:15am - gym []\n[ ] 9:00am - shower []\n[ ] 9:15am - weigh yourself (saturday) []\n")

    periodic_month = "[ ] Read 1 book\n[ ] Complete 1 nontrivial coding objective\n[ ] publish 1 blog post\n[ ] backup laptop data\n[ ] update financials\n"
    periodic_week = "[ ] Complete 1 nontrivial research objective\n[ ] Meet+followup >= 1 person\n[ ] 6-10 hrs coding\n[ ] teach ferdy 1 trick\n"
    periodic_day = "[ ] 40 mins gym\n[ ] Make bed\n[ ] 3 meals\n[ ] $nasal spray$\n[ ] Update schedule\n"
    daythemes = "SUNDAY: Groceries Day\nMONDAY: \nTUESDAY:Cleaning Day\nWEDNESDAY:\nTHURSDAY:\nFRIDAY:\nSATURDAY: LAUNDRY DAY\n"

    def test_month_template(self):
        """ Test that month template is generated correctly by integrating checkpoints, periodic, etc."""
        now = datetime.datetime(2012,12,4,18,50,30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        tasklistfile = StringIO(self.tasklist)
        daythemesfile = StringIO(self.daythemes)
        checkpointsfile = StringIO(self.checkpoints_month)
        periodicfile = StringIO(self.periodic_month)
        monthfile = StringIO(self.monthtemplate)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_month_file=checkpointsfile,
            periodic_month_file=periodicfile,
            monthfile=monthfile)

        (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
        monthtemplate = "= %s %d =\n" % (month.upper(), year)
        monthtemplate += "\n"
        monthtemplate += "\t* [[Week of %s %d, %d]]\n" % (month, date, year)
        monthtemplate += "\n"
        monthtemplate += "CHECKPOINTS:\n"
        monthtemplate += self.checkpoints_month
        monthtemplate += "\n"
        monthtemplate += "AGENDA:\n\n"
        monthtemplate += "MONTHLYs:\n"
        monthtemplate += self.periodic_month
        monthtemplate += "\n"
        monthtemplate += "NOTES:\n\n\n"
        monthtemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, PlannerPeriod.Month, next_day)

        self.assertEqual(planner.monthfile.read(), monthtemplate)

    def test_week_template(self):
        """ Test that week template is generated correctly by integrating checkpoints, periodic, etc."""
        now = datetime.datetime(2012,12,4,18,50,30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        tasklistfile = StringIO(self.tasklist)
        daythemesfile = StringIO(self.daythemes)
        checkpointsfile = StringIO(self.checkpoints_week)
        periodicfile = StringIO(self.periodic_week)
        weekfile = StringIO(self.weektemplate)

        planner = PlannerMock(
            tasklistfile=tasklistfile,
            daythemesfile=daythemesfile,
            checkpoints_week_file=checkpointsfile,
            periodic_week_file=periodicfile,
            weekfile=weekfile)

        (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
        weektemplate = ("= WEEK OF %s %d, %d =\n" % (month, date, year)).upper()
        weektemplate += "\n"
        weektemplate += "\t* [[%s %d, %d]]\n" % (month, date, year)
        weektemplate += "\n"
        weektemplate += "CHECKPOINTS:\n"
        weektemplate += self.checkpoints_week
        weektemplate += "\n"
        weektemplate += "AGENDA:\n\n"
        weektemplate += "WEEKLYs:\n"
        weektemplate += self.periodic_week
        weektemplate += "\n"
        weektemplate += "NOTES:\n\n\n"
        weektemplate += "TIME SPENT ON PLANNER: "

        templates.write_new_template(planner, PlannerPeriod.Week, next_day)

        self.assertEqual(planner.weekfile.read(), weektemplate)

    def test_daily_templates(self):
        """ Test that templates for each day are generated correctly by integrating checkpoints, periodic, etc.
        Currently only 2 templates - weekday, and weekend are used. TODO: Add individual templates for each day of the week """
        now = datetime.datetime(2012,12,7,18,50,30)
        def increment_date():
            while True:
                newdt = now + datetime.timedelta(days=1)
                yield newdt
        for i in range(7):
            now = next(increment_date())
            today = now.date()
            next_day = today + datetime.timedelta(days=1)
            (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
            tasklistfile = StringIO(self.tasklist)
            daythemesfile = StringIO(self.daythemes)
            periodicfile = StringIO(self.periodic_day)
            dayfile = StringIO(self.daytemplate)

            planner = PlannerMock(
                tasklistfile=tasklistfile,
                daythemesfile=daythemesfile,
                periodic_day_file=periodicfile,
                dayfile=dayfile)

            if day.lower() in ('saturday', 'sunday'):
                planner.checkpoints_weekend_file = StringIO(self.checkpoints_weekend)
            else:
                planner.checkpoints_weekday_file = StringIO(self.checkpoints_weekday)

            dailythemes = self.daythemes.lower()
            theme = dailythemes[dailythemes.index(day.lower()):]
            theme = theme[theme.index(':'):].strip(': ')
            theme = theme[:theme.index('\n')].strip().upper()
            theme = "*" + theme + "*"

            daytemplate = ""
            daytemplate += "= %s %s %d, %d =\n" % (day.upper(), month[:3].upper(), date, year)
            daytemplate += "\n"
            if len(theme) > 2:
                daytemplate += "Theme: %s\n" % theme
                daytemplate += "\n"
            daytemplate += "CHECKPOINTS:\n"
            if day.lower() in ('saturday', 'sunday'):
                daytemplate += self.checkpoints_weekend
            else:
                daytemplate += self.checkpoints_weekday
            daytemplate += "\n"
            daytemplate += "AGENDA:\n"
            daytemplate += "[ ] s'posed to do\n"
            daytemplate += "[\] kinda did\n"
            daytemplate += "[ ] contact dude\n"
            daytemplate += "[\] make X\n"
            daytemplate += "[ ] call somebody\n"
            daytemplate += "[ ] finish project\n"
            daytemplate += "\n"
            daytemplate += "DAILYs:\n"
            daytemplate += self.periodic_day
            daytemplate += "\n"
            daytemplate += "NOTES:\n\n\n"
            daytemplate += "TIME SPENT ON PLANNER: "

            templates.write_new_template(planner, PlannerPeriod.Day, next_day)

            self.assertEqual(planner.dayfile.read(), daytemplate)
            self.assertEqual(planner.tasklistfile.read(), self.tasklist_nextday)

class PlannerExistingTemplateUpdateIntegrityTester(unittest.TestCase):
    """ Check that updates on existing templates modifies the file as expected - does the right thing, does only that thing """

    monthtemplate = ("= DECEMBER 2012 =\n"
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
                    "TIME SPENT ON PLANNER: ")

    monthtemplate_updated = ("= DECEMBER 2012 =\n"
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
                    "TIME SPENT ON PLANNER: ")

    weektemplate = ("= WEEK OF DECEMBER 1, 2012 =\n"
                    "\n"
                    "Theme: *WEEK OF THEME*\n"
                    "\n"
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
                    "TIME SPENT ON PLANNER: ")

    weektemplate_updated = ("= WEEK OF DECEMBER 1, 2012 =\n"
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
                    "TIME SPENT ON PLANNER: ")

    def test_update_existing_month_template(self):
        """ Check that writing over an existing month template adds the new week, and that there are no other changes """
        now = datetime.datetime(2012,12,4,18,50,30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
        monthfile = StringIO(self.monthtemplate)
        planner = PlannerMock(monthfile=monthfile)
        templates.write_existing_template(planner, PlannerPeriod.Month, next_day)
        self.assertEqual(planner.monthfile.read(), self.monthtemplate_updated)

    def test_update_existing_week_template(self):
        """ Check that writing over an existing week template adds the new day, and that there are no other changes """
        now = datetime.datetime(2012,12,4,18,50,30)
        today = now.date()
        next_day = today + datetime.timedelta(days=1)
        (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
        weekfile = StringIO(self.weektemplate)
        planner = PlannerMock(weekfile=weekfile)
        templates.write_existing_template(planner, PlannerPeriod.Week, next_day)
        self.assertEqual(planner.weekfile.read(), self.weektemplate_updated)
