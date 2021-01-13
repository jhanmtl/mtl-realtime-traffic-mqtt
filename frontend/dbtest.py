from frontend_utils import  RedisDB
import redis
import json


db=RedisDB()
latest_speed=db.latest_readings("vehicle-speed")
n_latest_speed=db.n_latest_readings("vehicle-speed",3)
latest_count=db.latest_readings("vehicle-count")
latest_gaptime=db.latest_readings("vehicle-gap-time")


print(latest_speed)
print(n_latest_speed)

