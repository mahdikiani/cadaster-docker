import concurrent.futures
import itertools
import json
import logging
import os
import queue

import redis
import requests
from localstorage import S3

redis_host = "localhost"
redis_port = 6379
rediscli = redis.Redis(host=redis_host, port=redis_port)

# proxies = {"http": "socks5://host.docker.internal:27273", "https": "socks5://host.docker.internal:27273"}
proxies = {"http": "socks5://localhost:27273", "https": "socks5://localhost:27273"}
status_file = "status.txt"

storage_path = "/mnt/HC_Volume_35080261/cadaster"


def get_route_key(x, y, z):
    # r = requests.get(f"http://keygen:3000/key?x={x}&y={y}&z={z}")
    r = requests.get(f"http://localhost:3000/key?x={x}&y={y}&z={z}")
    return r.text


def get_tasks():
    zlists = {
        10: {"x": range(636, 692 + 1), "y": range(388, 438 + 1)},
        13: {"x": range(5090, 5540 + 1), "y": range(3100, 3510 + 1)},
    }
    route_key = {
        "SafaTGBaseMap": [708, 700],
        "SafaTGLive": [
            "Pahneh",
            "M10",
            "MozayedeInProg",
            9092,
            9696,
            2,
            14000329,
            12121,
            14000329,
            14010228,
            14010601,
            140202171,
            140202173,
        ],
    }

    z = 13
    tasks = {}
    flag = False
    for x, y in itertools.product(*zlists[z].values()):
        r = get_route_key(x, y, z)

        for route, keys in route_key.items():
            for key in keys:
                if rediscli.exists(f"{x}/{y}/{z}/{key}"):
                    new_task = json.loads(rediscli.get(f"{x}/{y}/{z}/{key}"))
                else:
                    new_task = {
                        "x": x,
                        "y": y,
                        "z": z,
                        "route": route,
                        "key": key,
                        "r": r,
                        "url": "https://map.mimt.gov.ir/{route}/maptile.ashx?x={x}&y={y}&z={z}&Key={key}&r={r}".format(
                            route=route, x=x, y=y, z=z, key=key, r=r
                        ),
                        "path": f"{storage_path}/{z}/{key}/{x}_{y}.png",
                        "done": False,
                    }
                new_task["path"] = f"{storage_path}/{z}/{key}/{x}_{y}.png"
                if os.path.exists(new_task["path"]):
                    file_stats = os.stat(new_task["path"])
                    if file_stats.st_size > 0:
                        new_task["done"] = True
                rediscli.set(f"{x}/{y}/{z}/{key}", json.dumps(new_task))
                tasks.update({f"{x}/{y}/{z}/{key}": new_task})

    return tasks


tasks = get_tasks()
with open("tasks.json", "w") as f:
    json.dump(tasks, f, indent=4)
