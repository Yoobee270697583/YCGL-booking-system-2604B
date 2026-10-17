import datetime

from django.utils import timezone
from django.utils.formats import date_format


def week_monday(date):
    return date - datetime.timedelta(days=date.weekday())


def open_week_monday(today):
    """The one Monday whose week is open for applications on `today`."""
    soonest = today + datetime.timedelta(days=3)
    return soonest + datetime.timedelta(days=(7 - soonest.weekday()) % 7)


def window_message(date, today=None):
    """None if applications are open for the week containing `date`,
    otherwise a message explaining why not."""
    today = today or timezone.localdate()
    monday = week_monday(date)
    opens = monday - datetime.timedelta(days=9)   # the Saturday before last
    closes = monday - datetime.timedelta(days=3)  # the Friday before it starts

    if opens <= today <= closes:
        return None

    week = date_format(monday, "l j F")
    now_open = date_format(open_week_monday(today), "l j F")
    if today < opens:
        return (
            f"Applications for the week starting {week} open on "
            f"{date_format(opens, 'l j F')}. Right now you can apply for the "
            f"week starting {now_open}."
        )
    return (
        f"Applications for the week starting {week} closed on "
        f"{date_format(closes, 'l j F')} at 11:59 PM. Right now you can apply "
        f"for the week starting {now_open}."
    )