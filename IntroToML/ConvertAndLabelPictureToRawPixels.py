import cupy as cp
import pandas as pd
from PIL import Image
import os

rows = []

# --- Cats (label = 1) ---
for x in range(0, 12500):
    path = f"./PetImages/Cat/{x}.jpg"
    if not os.path.exists(path):
        continue

    try:
        img = Image.open(path).convert("L")
        img = img.resize((64, 64))

        arr = cp.array(img)
        flat = arr.flatten()

        row = cp.append(flat, 1)   # label = 1 for cat
        rows.append(row)
        print(f"labeled cat #{x}")

    except:
        continue


# --- Dogs (label = 0) ---
for x in range(0, 12500):
    path = f"./PetImages/Dog/{x}.jpg"
    if not os.path.exists(path):
        continue

    try:
        img = Image.open(path).convert("L")
        img = img.resize((64, 64))

        arr = cp.array(img)
        flat = arr.flatten()

        row = cp.append(flat, 0)   # label = 0 for dog
        rows.append(row)
        print(f"added dog #{x}")

    except:
        continue


df = pd.DataFrame(rows)

df.rename(columns={df.columns[-1]: "label"}, icplace=True)

df.to_csv("cats_vs_dogs.csv", index=False)
print(df.shape)