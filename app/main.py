from fastapi import FastAPI
from schemas.input_schema import InputProperty
import pandas as pd
import joblib
import time

app = FastAPI()

# Load demographic features once
demographics = pd.read_csv("app/data/zipcode_demographics.csv").set_index("zipcode")

# Load initial model
model = joblib.load("app/model_store/model.pkl")
model_version = "v1"

@app.post("/predict")
def predict(input_data: InputProperty):
    start = time.time()

    # Convert JSON to dataframe
    df = pd.DataFrame([input_data.dict()])

    # Join demographic features
    df = df.join(demographics, on="zipcode")

    # Run prediction
    pred = model.predict(df)[0]
    latency = round((time.time() - start) * 1000, 2)

    return {
        "prediction": float(pred),
        "model_version": model_version,
        "latency_ms": latency
    }

@app.post("/reload-model")
def reload_model():
    """Hot-swap model without restarting the server."""
    global model, model_version

    model = joblib.load("app/model_store/model_v2.pkl")
    model_version = "v2"

    return {"status": "model reloaded", "model_version": model_version}
