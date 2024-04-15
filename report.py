# %%
import json

import matplotlib.pyplot as plt
import pandas as pd

with open("tasks.json", "r") as f:
    tasks = json.load(f)

df = pd.DataFrame([v for v in tasks.values()])
df["key"] = [k for k in tasks.keys()]

# %%
