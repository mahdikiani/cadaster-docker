import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def is_png_file(file_path):
    png_magic_number = b"\x89PNG\x0D\x0A\x1A\x0A"
    try:
        with open(file_path, "rb") as file:
            magic_number = file.read(8)
            return magic_number == png_magic_number
    except IOError:
        return False


def is_valid_image(file_path):
    image_formats = [
        b"\xFF\xD8\xFF",
        b"\x89PN",
        b"GIF",
        b"BM",
    ]
    # png_magic_number = b'\x89PNG\x0D\x0A\x1A\x0A'
    try:
        with open(file_path, "rb") as file:
            file_signature = file.read(3)
            if file_signature in image_formats:
                return True
        return False
    except IOError:
        return False


tasks_df = pd.read_json("tasks.json").T
tasks_df["path"] = tasks_df.apply(
    lambda task: f"/mnt/HC_Volume_35080261/cadaster/{task['z']}/{task['key']}/{task['x']}_{task['y']}.png",
    axis=1,
)
tasks_df["file_size"] = tasks_df.apply(
    lambda task: os.path.getsize(task["path"]) if task["done"] else 0, axis=1
)

df = tasks_df[tasks_df["file_size"] > 0]
df["valid_png"] = df.apply(lambda row: is_png_file(row.path), axis=1)
df["valid"] = df.apply(lambda row: is_valid_image(row.path), axis=1)
dfv = df[df.valid]

for key in dfv.key.unique():
    dfv[dfv.key == key].plot.scatter(x="x", y="y")
    plt.xlim(df.x.min(), df.x.max())
    plt.ylim(df.y.min(), df.y.max())
    plt.gca().invert_yaxis()
    plt.savefig(f"imgs/{key}.png")
    plt.close()

# task = tasks_df.iloc[0]
# with open(task.path, "rb") as f:
#     data = f.read()
# print(data)
# print(data.decode("utf-8"))

num_rows = df.x.max() - df.x.min() + 1
num_cols = df.y.max() - df.y.min() + 1
big_img_height = num_rows * 256
big_img_width = num_cols * 256

for key in dfv.key.unique():
    # key_im = cv2.Mat((50*256, 56*256, 3))

    key_im = np.zeros((big_img_width, big_img_height, 4), dtype=np.uint8)
    for _, task in dfv[dfv.key == key].iterrows():
        img = cv2.imread(task.path, cv2.IMREAD_UNCHANGED)
        x = task.x - df.x.min()
        y = task.y - df.y.min()
        key_im[y * 256 : y * 256 + 256, x * 256 : x * 256 + 256, : img.shape[2]] = img
        if img.shape[2] == 3:
            key_im[y * 256 : y * 256 + 256, x * 256 : x * 256 + 256, 3] = 255
    cv2.imwrite(f"imgs/{key}.png", key_im)
    thumbnail = cv2.resize(
        key_im, (num_rows * 10, num_cols * 10), interpolation=cv2.INTER_AREA
    )
    cv2.imwrite(f"imgs/{key}_t.png", thumbnail)
    # break


for key in dfv.key.unique():
    # key_im = cv2.Mat((50*256, 56*256, 3))

    key_im = np.memmap(
        f"imgs/{key}.mmap",
        mode="w+",
        shape=(big_img_width, big_img_height, 4),
        dtype=np.uint8,
    )
    for _, task in dfv[dfv.key == key].iterrows():
        img = cv2.imread(task.path, cv2.IMREAD_UNCHANGED)
        x = task.x - df.x.min()
        y = task.y - df.y.min()
        key_im[y * 256 : y * 256 + 256, x * 256 : x * 256 + 256, : img.shape[2]] = img
        if img.shape[2] == 3:
            key_im[y * 256 : y * 256 + 256, x * 256 : x * 256 + 256, 3] = 255
    cv2.imwrite(f"imgs/{key}.png", key_im)
    thumbnail = cv2.resize(
        key_im, (num_rows * 20, num_cols * 20), interpolation=cv2.INTER_AREA
    )
    cv2.imwrite(f"imgs/{key}_t.png", thumbnail)
    # break
