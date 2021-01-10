import redis
import json
import os

db=redis.Redis()
files=os.listdir("../data")
jfiles=[i for i in files if ".json" in i and "data" not in i]

for j in jfiles:
    key=j.replace(".json","")
    j="../data/"+j
    with open(j,"r") as f:
        data=json.load(f)
        db.set(key,json.dumps(data))
