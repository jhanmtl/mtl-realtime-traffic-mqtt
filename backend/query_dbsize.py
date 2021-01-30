import redis
import json

db = redis.Redis(host='localhost', port=6379, db=0)

data=json.loads(db.get("00773"))
size=len(data['vehicle-gap-time'])
print(size)
