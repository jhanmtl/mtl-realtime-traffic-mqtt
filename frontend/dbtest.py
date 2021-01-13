from frontend_utils import  RedisDB
import redis
import json

# db=redis.Redis()
# keys=[k.decode() for k in db.keys()]
#
# readings={}
#
# for k in keys:
#     readings[k]=json.loads(db.get(k))
#
# print(readings['00773'].keys())


db=RedisDB()
latest_speed=db.latest_reading("vehicle-speed")
n_latest_speed=db.n_latest_readings("vehicle-speed",5)
# latest_count=db.latest_reading("vehicle-count")
# latest_gap=db.latest_reading("vehicle-gap-time")

print(latest_speed)
print(n_latest_speed)

