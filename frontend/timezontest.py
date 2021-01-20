import datetime
import pytz
import frontend_utils

utc_time_str="2021-01-19T22:12:59"
converted=frontend_utils.date_convert(utc_time_str)

print(converted)
print(converted.strftime("%m/%d/%y %H:%M"))


