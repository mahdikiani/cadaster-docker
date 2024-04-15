import json
import os

import redis

# connect to redis server
r = redis.Redis(host="localhost", port=6379, db=0)

# add to redis
keys = [k.decode() for k in r.keys() if k.decode().count("/") > 0]
tasks = {}
for k in keys:
    tasks[k] = json.loads(r.get(k))

with open("tasks_redis.json", "w") as f:
    json.dump(tasks, f, indent=4)
