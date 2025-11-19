from app.schemas.input_schema import InputProperty, InputPropertyLite
from app.custom_transformers import HouseDateFeatures
from fastapi import FastAPI, status
from datetime import datetime
import pandas as pd
import joblib
import json
import logging
import time


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()

# Instantiate FastAPI app
app = FastAPI()

# Load demographic features once
demographics = pd.read_csv("app/data/zipcode_demographics.csv").set_index("zipcode")
demographic_means = demographics.mean()

# Load initial model
model = joblib.load("app/model_store/model.pkl")
model_features = json.load(open("app/model_store/model_features.json"))
model_version = "v1"


# Inference logic
def run_inference(input_data: InputProperty):
    # Start timer
    start = time.time()
    logger.info(f"Received request: {input_data}")
    
    # Store input data as pandas DataFrame
    df = pd.DataFrame([input_data.dict()])
    zipcode = input_data.zipcode
    demo_imputed = False

    # Join if zipcode exists in demographics, else impute means
    if zipcode in demographics.index:
        demo_row = demographics.loc[[zipcode]]
    else:
        # Impute means
        logger.info(f"Zip Code {zipcode} not found. Imputing mean demographic values.")
        demo_row = pd.DataFrame([demographic_means], index=[zipcode])
        demo_imputed = True

    # Add today's date for date column
    if model_version == "v2":
        df["date"] = str(datetime.now().date()).replace("-", "")

    # Enrich input with demographic features
    df = df.join(demo_row, on="zipcode")[model_features]

    # Predict
    pred = float(model.predict(df)[0])
    latency = round((time.time() - start) * 1000, 2)
    logger.info(f"Prediction: {pred}, latency_ms={latency}")

    return {
        "prediction": round(pred, 2),
        "latency_ms": latency,
        "demo_imputed": demo_imputed,
        "model_version": model_version
    }


# Base model endpoint (all input features required)
@app.post("/predict", status_code=status.HTTP_200_OK)
def predict(input_data: InputProperty):
    return run_inference(input_data)


# Base model-lite endpoint (only modeling features required)
@app.post("/predict-lite", status_code=status.HTTP_200_OK)
def predict_lite(input_data: InputPropertyLite):
    return run_inference(input_data)


# Endpoint for updating model version
@app.post("/reload-model")
def reload_model():
    """Hot-swap model without restarting the server."""
    global model, model_features, model_version
    logger.info("Reloading model...")

    model = joblib.load("app/model_store/model_v2.pkl")
    model_features = json.load(open("app/model_store/model_features_v2.json"))
    model_version = "v2"

    logger.info(f"Model reloaded. New version: {model_version}")
    return {"status": "model reloaded", "model_version": model_version}
