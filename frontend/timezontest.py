import datetime
import pytz
import frontend_utils

t1=last_time="2021-01-08T22:16:59"
t2=now_time="2022-01-08T22:16:59"

t1=datetime.datetime.strptime(t1,"%Y-%m-%dT%H:%M:%S")
t2=datetime.datetime.strptime(t2,"%Y-%m-%dT%H:%M:%S")

print(t1)
print(t2)

delta=t2-t1

days=delta.days
seconds=delta.seconds

hrs=seconds//3600
minutes=(seconds//60)%60
seconds=seconds%60

print("{} days, {} hours, {} minutes, {} seconds".format(days,hrs,minutes,seconds))


