import random
import simplejson
from django.utils.timezone import utc
from datetime import timedelta, datetime
from rfid_lock_management.models import RFIDkeycard, AccessTime

# Helpful functions for development

# Issue #d

def make_access_times(min_num_times=10, max_num_times=10):
    """
    Generate a random number of access times in a specified range, *for each
    keycard in the system* (i.e. not the total number of access times).  (This
    is quick and not very generalizable. Four doors, each with different usage
    characteristics, e.g. door 1 is only used two days of the week.)
    """
    counter = 0
    for keycard in RFIDkeycard.objects.all():
        for i in range(random.randint(min_num_times, max_num_times)):
            try:
                door = random.choice(keycard.lockuser.doors.all())
            except IndexError:
                return "no doors, so no access times"

            # next code duplicated by 70%.
            # door 1:  only certain days of the week
            if door.id == 1:
                j = 0
                while j < 1:
                    the_date_time = get_random_time()
                    if (the_date_time.weekday() in [5, 6, 4]):
                        lockuser = keycard.lockuser
                        at = AccessTime(
                            the_rfid=keycard.the_rfid,
                            access_time=the_date_time,
                            lockuser=lockuser, door=door)
                        assign_data_point_dict(at)
                        at.save()
                        counter += 1
                        j += 1
            # door 2:  more than all others, but only between 8 am and 3 pm
            elif door.id == 2:
                j = 0
                while j < 2:
                    the_date_time = get_random_time()
                    if the_date_time.hour > 9 and the_date_time.hour < 14:
                        lockuser = keycard.lockuser
                        at = AccessTime(
                            the_rfid=keycard.the_rfid,
                            access_time=the_date_time,
                            lockuser=lockuser, door=door)
                        assign_data_point_dict(at)
                        at.save()
                        counter += 1
                        j += 1
            # door 3: only for 4 hours during the day
            elif door.id == 3:
                j = 0
                while j < 5:
                    the_date_time = get_random_time()
                    if the_date_time.hour > 15 and the_date_time.hour < 19:
                        lockuser = keycard.lockuser
                        at = AccessTime(
                            the_rfid=keycard.the_rfid,
                            access_time=the_date_time,
                            lockuser=lockuser, door=door)
                        assign_data_point_dict(at)
                        at.save()
                        counter += 1
                        j += 1
            # all other doors
            else:
                the_date_time = get_random_time()
                lockuser = keycard.lockuser
                at = AccessTime(
                    the_rfid=keycard.the_rfid, access_time=the_date_time,
                    lockuser=lockuser, door=door)
                assign_data_point_dict(at)
                at.save()
                counter += 1
    return "created %d access times" % counter


def get_random_time():
    """
    Return a random datetime between two datetime objects.
    """
    now = datetime.now().replace(tzinfo=utc)
    time_period = timedelta(days=180)  # about half a year
    start = now - time_period
    time_period_seconds = time_period.total_seconds()
    random_second = random.randrange(time_period_seconds)
    return (start + timedelta(seconds=random_second))


def assign_data_point_dict(at):
    # data point dict to JSONify for the access times highchart
    data_point_dict = {}
    data_point = {}
    # subtract 1 from the month because months start at 0 in JavaScript, not 1
    data_point_dict['x'] = 'Date.UTC(%d,%d,%d)' % (
        at.access_time.year, at.access_time.month - 1, at.access_time.day)
    # new way to format string is .format
    data_point_dict['x'] = 'Date.UTC({},{},{})'.format(
        at.access_time.year,
        at.access_time.month - 1,
        at.access_time.day
    )
    # or. havent checked it, but works somehow like it
    data_point_dict['x'] = 'Date.UTC({year},{month},{day})'.format(
        year=at.access_time.year,
        month=at.access_time.month - 1,
        day=at.access_time.day
    )

    data_point_dict['y'] = 'Date.UTC(0,0,0, %d,%d,%d)' % (
        at.access_time.hour, at.access_time.minute, at.access_time.second)
    data_point_dict['user'] = '"%s %s"' % (
        at.lockuser.first_name, at.lockuser.last_name)
    at.data_point = simplejson.dumps(data_point_dict)
