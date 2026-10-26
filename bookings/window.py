from datetime import timedelta

from django.utils import timezone
from django.utils.formats import date_format

# Figure out Monday of the week of the date passed in
def calculate_monday(date):
    # Get and return Monday for the week of the date being passed in
    monday_date = date - timedelta(days=date.weekday())
    return monday_date


# Remember, the "application window" rolls over to the following week at midnight/12:00am of Friday night/Saturday morning
# Applications can't be made for the current week. They can only be made for next week until midnight Friday
# And can only be made for the following week on Saturday & Sunday
# Therefore, a function to figure out the Monday of the week currently open for applications, as of today's date:
def open_week_monday(today):
    # First, calculate Monday of this week
    this_monday = calculate_monday(today)
    # Then, if it's currently a weekday
    if today.weekday() <= 4:
        # Applications are currently open for next week, so return next Monday
        next_monday = this_monday + timedelta(days=7)
        return next_monday
    # Otherwise, if it's currently a weekend
    else:
        # Applications are currently open for the following week, so return the following Monday
        the_following_monday = this_monday + timedelta(days=14)
        return the_following_monday

# Function to check if applications are open for the week the user currently has selected
# If not, return a message with an explanation
def application_window_message(date):
    # Start by making some variables
    today = timezone.localdate()                # Today's date
    monday = calculate_monday(date)             # Monday of the week of the currently selected date
    open_monday = open_week_monday(today)       # Monday of the week currently open for applications, by calling open_week_monday from above
    opens = monday - timedelta(days=9)          # Applications for any given week open at 12:00am the Saturday 9 days before
    closes = monday - timedelta(days=3)         # And close at 11:59pm the Friday 3 days before

    # If applications are currently open for the date selected, no message is needed
    if opens <= today <= closes:
        return None

    # Save and format the currently selected week as a variable
    selected_week = date_format(monday, "l j F")
    # Save and format the currently open week as a variable
    now_open = date_format(open_monday, "l j F")
    # Format the applications open date
    opens_text = date_format(opens, 'l j F')
    # Format the applications close date
    closes_text = date_format(closes, 'l j F')

    # If applications are currently closed for the future date selected, meaning the user is too early
    if today < opens:
        # Return a formatted string explaining the situation
        return (
            f"Applications for the week of {selected_week} open on "
            f"{opens_text}. Right now you can apply for the "
            f"week starting {now_open}."
        )
    # Otherwise if applications have already closed for the date selected, return a formatted string explaining that situation
    return (
        f"Applications for the week starting {selected_week} closed on "
        f"{closes_text} at 11:59 PM. Right now, you can apply "
        f"for the week starting {now_open}."
    )