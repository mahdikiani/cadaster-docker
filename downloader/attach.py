import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

images = [
    f"{BASE_DIR}/imgs/{im}" for im in os.listdir(f"{BASE_DIR}/imgs") if im.find("_") < 0
]
images = [
    # "imgs/700.png",
    f"{BASE_DIR}/imgs/708.png",
    f"{BASE_DIR}/imgs/M10.png",
    f"{BASE_DIR}/imgs/140202171.png",
    f"{BASE_DIR}/imgs/9696.png",
    f"{BASE_DIR}/imgs/Pahneh.png",
    f"{BASE_DIR}/imgs/140202173.png",
    f"{BASE_DIR}/imgs/12121.png",
    f"{BASE_DIR}/imgs/14000329.png",
    f"{BASE_DIR}/imgs/9092.png",
    f"{BASE_DIR}/imgs/14010601.png",
    f"{BASE_DIR}/imgs/14010228.png",
    f"{BASE_DIR}/imgs/2.png",
]

canvas = None

# Iterate through PNG files and overlay them
for image_path in images:
    print(image_path)
    # Load the PNG image with an alpha channel
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if img is None:
        continue

    # Extract the alpha channel
    alpha = img[:, :, 3] / 255.0

    # Resize the image to match the canvas size (optional)
    if canvas is None:
        canvas = cv2.resize(img, (img.shape[1], img.shape[0]))
        trans_mask = canvas[:, :, 3] == 0
        canvas[trans_mask] = [255, 255, 255, 255]

    else:
        # Blend the images using the alpha channel
        overlay = img[:, :, :3]  # Extract RGB channels
        alpha = img[:, :, 3] / 255.0
        for c in range(3):
            canvas[:, :, c] = (1.0 - alpha) * canvas[:, :, c] + alpha * overlay[:, :, c]


cv2.imwrite(f"{BASE_DIR}/imgs/overlay_result.png", canvas)
thumbnail = cv2.resize(
    canvas, (canvas.shape[1] // 10, canvas.shape[0] // 10), interpolation=cv2.INTER_AREA
)
cv2.imwrite(f"{BASE_DIR}/imgs/overlay_result_t.png", thumbnail)
