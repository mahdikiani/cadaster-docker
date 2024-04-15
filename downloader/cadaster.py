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


def download_file(url, status):
    filename = "imgs/" + url.split("?")[-1]
    filename = "imgs/" + url.split("?")[-1]

    logging.info("Downloading {url}".format(url=url))
    response = requests.get(url, stream=True, proxies=proxies, timeout=60, verify=False)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    logging.info("Downloaded {url}".format(url=url))
    status[url] = "downloaded"
    with open(status_file, "a") as f:
        f.write("{url} downloaded\n".format(url=url))


def done_task(task):
    task["done"] = True
    rediscli.set(f"{task['x']}/{task['y']}/{task['z']}/{task['key']}", json.dumps(task))

    # with open("tasks.json") as f:
    #     tasks = json.load(f)
    # tasks[f"{task['x']}/{task['y']}/{task['z']}/{task['key']}"] = task
    # with open("tasks.json", "w") as f:
    #     json.dump(tasks, f, indent=4)

    logging.info("Downloaded {url}".format(url=task["url"]))


def downloader(queue: queue.Queue):
    while True:
        task = queue.get()
        if task is None:
            break
        try:
            key = f"{task['x']}/{task['y']}/{task['z']}/{task['key']}"
            task = json.loads(rediscli.get(key))
            if not task["done"]:
                logging.info("Downloading {url}".format(url=task["url"]))
                # download_file(url, status_file)
                file_size = S3().upload_url(
                    task["url"],
                    f"{task['z']}/{task['key']}/{task['x']}/{task['y']}.png",
                    proxies=proxies,
                )
                if file_size > 0:
                    task["file_size"] = file_size
                    done_task(task)
                else:
                    logging.info("Failed {url}".format(url=task["url"]))
        except Exception as e:
            logging.error(f'Failed {task["url"]} {e}')
        queue.task_done()


def get_route_key(x, y, z):
    # r = requests.get(f"http://keygen:3000/key?x={x}&y={y}&z={z}")
    r = requests.get(f"http://localhost:3000/key?x={x}&y={y}&z={z}")
    return r.text


def get_tasks():
    zlists = {
        6: {"x": range(20, 30 + 1), "y": range(20, 30 + 1)},
        7: {"x": range(40, 100 + 1), "y": range(40, 100 + 1)},
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

    z = 7
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
                        "done": False,
                    }
                    rediscli.set(f"{x}/{y}/{z}/{key}", json.dumps(new_task))
                tasks.update({f"{x}/{y}/{z}/{key}": new_task})

    return tasks


def main():
    tasks = get_tasks()
    with open("tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)

    qu = queue.Queue()
    for task in tasks.values():
        if not task["done"]:
            qu.put(task)

    # downloader(qu)
    run = True
    multithread = True
    if run and multithread:
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = []
            for i in range(50):
                future = executor.submit(downloader, qu)
                futures.append(future)

            qu.join()

            for future in futures:
                future.result()

            with open("tasks.json", "w") as f:
                json.dump(tasks, f, indent=4)

    logging.info("All downloads completed")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.FileHandler("download.log"), logging.StreamHandler()],
    )
    main()
