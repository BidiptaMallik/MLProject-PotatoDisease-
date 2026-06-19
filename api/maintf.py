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

endpoint = os.getenv("TF_SERVING_URL", "http://localhost:8501/v1/models/potatoes_model:predict")



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

    json_data = {
    "instances": img_batch.tolist()
    }

    response = requests.post(endpoint, json=json_data)


    

    if response.status_code != 200:
        return {"error": response.text}
    
    prediction = np.array(response.json()["predictions"])

    print("RAW PREDICTION:", prediction)
    print("ARGMAX:", np.argmax(prediction[0]))

    prediction = np.array(response.json()["predictions"])

    predicted_class = CLASS_NAMES[np.argmax(prediction[0])]
    confidence = float(np.max(prediction[0]))

    return {
        "class": predicted_class,
        "confidence": confidence
    }
    

if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=int(os.getenv("PORT", 8000)))