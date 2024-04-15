import itertools
import json
import os

download_dir = "/mnt/HC_Volume_35080261/cadaster"


def get_tasks():
    zlists = {
        6: {"x": range(20, 79 + 1), "y": range(20, 48 + 1)},
        7: {"x": range(79, 86 + 1), "y": range(48, 54 + 1)},
        10: {"x": range(636, 692 + 1), "y": range(388, 438 + 1)},
        13: {"x": range(5099, 5537 + 1), "y": range(3107, 3505 + 1)},
    }
    route_key = "map"
    z = 7
    tasks = {}
    for z in zlists.keys():
        xmin = max(zlists[z]["x"])
        xmax = min(zlists[z]["x"])
        ymin = max(zlists[z]["y"])
        ymax = min(zlists[z]["y"])
        tasks[z] = []

        for x, y in itertools.product(*zlists[z].values()):
            if not os.path.exists(f"{download_dir}/{z}/{route_key}/{x}/{y}.png"):
                # print(f"{download_dir}/{z}/{route_key}/{x}/{y}.png")
                # break
                tasks[z].append({"x": x, "y": y})
            else:
                xmin = min(xmin, x)
                xmax = max(xmax, x)
                ymin = min(ymin, y)
                ymax = max(ymax, y)
            # if x % 10 == 0 and y % 10 == 0:
            #     print(z, x, y)

        print(z, xmin, xmax, ymin, ymax)
    return tasks


tasks = get_tasks()
with open("open_tasks.json", "w") as f:
    json.dump(tasks, f, indent=4)
