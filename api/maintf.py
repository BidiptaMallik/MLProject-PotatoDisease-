from fastapi import FastAPI,File,UploadFile
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
import os
import requests


app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

endpoint = os.getenv("TF_SERVING_URL")



CLASS_NAMES=["Early Blight", "Late Blight","Healthy"]


@app.get("/ping")
async def ping():
    return "Hello"

def read_file_as_image(data) -> np.ndarray:
    image = Image.open(BytesIO(data)).convert("RGB")
    image = image.resize((256, 256))
    image = np.array(image)
    return image






@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    import time

    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, axis=0)

    json_data = {"instances": img_batch.tolist()}

    response = None
    last_error = None

    # 🔥 RETRY LOGIC (FIX FOR 502 / COLD START)
    for attempt in range(5):
        try:
            response = requests.post(
                endpoint,
                json=json_data,
                timeout=120
            )

            print(f"Attempt {attempt+1} status:", response.status_code)

            if response.status_code == 200:
                break

        except Exception as e:
            last_error = str(e)
            print(f"Attempt {attempt+1} failed:", e)
            time.sleep(3)

    
    if response is None:
        return {"error": f"Model not reachable: {last_error}"}

    print("Final Status:", response.status_code)
    print("Body:", response.text[:500])

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    predictions = result.get("predictions")

    if not predictions:
        return {"error": "No predictions from model"}

    probs = np.squeeze(np.array(predictions))

    if probs.ndim != 1:
        return {"error": "Invalid prediction shape"}

    predicted_index = int(np.argmax(probs))
    confidence = float(probs[predicted_index])

    return {
        "class": CLASS_NAMES[predicted_index],
        "confidence": confidence
    }
    

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=int(os.getenv("PORT", 8000)))