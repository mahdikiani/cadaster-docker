import os
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASEDIR = Path("/mnt/HC_Volume_35080261/cadaster")
zs = [
    6,
    7,
    10,
    13,
]

for z in zs:
    if not (BASEDIR / str(z) / "map").exists():
        os.makedirs(BASEDIR / str(z) / "map")
    keys = os.listdir(BASEDIR / str(z))
    keys.remove("map")
    keys.remove("700")
    keys.remove("708")

    for x in os.listdir(BASEDIR / str(z) / "708"):
        if not (BASEDIR / str(z) / "map" / x).exists():
            os.makedirs(BASEDIR / str(z) / "map" / x)
        for y in os.listdir(BASEDIR / str(z) / "708" / x):
            if (BASEDIR / str(z) / "map" / x / y).exists():
                continue
            base_img = cv2.imread(
                str(BASEDIR / str(z) / "708" / x / y), cv2.IMREAD_UNCHANGED
            )
            if base_img is None:
                continue
            if base_img.shape[2] == 3:
                base_img[:, :, :, 3] = 255

            alpha = base_img[:, :, 3] / 255.0
            canvas = cv2.resize(base_img, (base_img.shape[1], base_img.shape[0]))
            trans_mask = canvas[:, :, 3] == 0
            canvas[trans_mask] = [255, 255, 255, 255]

            for key in keys:
                path = BASEDIR / str(z) / key / x / y
                if path.exists():
                    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
                    if img is None:
                        continue
                    # if img.shape[2] == 3:
                    #     img[:, :, :, 3] = 255
                    # Blend the images using the alpha channel
                    overlay = img[:, :, :3]  # Extract RGB channels
                    alpha = img[:, :, 3] / 255.0
                    for c in range(3):
                        canvas[:, :, c] = (1.0 - alpha) * canvas[
                            :, :, c
                        ] + alpha * overlay[:, :, c]

                print(f"{BASEDIR}/{z}/map/{x}/{y}")
                cv2.imwrite(f"{BASEDIR}/{z}/map/{x}/{y}", canvas)
                # plt.imshow(img)
                # plt.show()
                # plt.close()
                # break
