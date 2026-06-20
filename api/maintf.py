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

    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image, axis=0)

    json_data = {"instances": img_batch.tolist()}

    try:
        response = requests.post(
            endpoint,
            json=json_data,
            timeout=120
        )

        print("Status:", response.status_code)
        print("Body:", response.text[:500])

    except Exception as e:
        print("ERROR:", repr(e))
        return {"error": str(e)}

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()

    predictions = np.array(result.get("predictions"))

    # 🔥 safety check
    if predictions is None or len(predictions) == 0:
        return {"error": "Invalid prediction from model"}

    probs = predictions[0]

    predicted_index = int(np.argmax(probs))
    confidence = float(probs[predicted_index])

    return {
        "class": CLASS_NAMES[predicted_index],
        "confidence": confidence
    }
    

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=int(os.getenv("PORT", 8000)))