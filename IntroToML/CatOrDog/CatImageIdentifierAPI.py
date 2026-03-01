import cupy as cp
import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

app = FastAPI()

#helper to run locally with no issue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sigmoid(z):
    return 1 / (1 + cp.exp(-z))

def predict_cat(thetas, img, train_mean, train_std):
    thetas = cp.array(thetas)

    img = img.convert("L").resize((64, 64))
    arr = cp.array(np.array(img), dtype=cp.float64).flatten()
    arr = (arr - train_mean) / train_std

    x = cp.append(cp.array([1.0]), arr)
    prob = float(sigmoid(thetas.dot(x)))
    label = 1 if prob >= 0.5 else 0

    return {"probability": prob, "label": label, "prediction": "cat" if label == 1 else "dog"}

#load files
thetas = np.load('../thetas.npy')
stats = np.load('../train_stats.npy')
train_mean, train_std = stats[0], stats[1]


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    return predict_cat(thetas, img, train_mean, train_std)
