import json
import os

import redis

# connect to redis server
r = redis.Redis(host="localhost", port=6379, db=1)

# open tasks.json
with open("tasks.json", "r") as f:
    tasks = json.load(f)

# add to redis
for k, v in tasks.items():
    r.set(k, json.dumps(v))
    print(k)
