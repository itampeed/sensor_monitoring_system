import os
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import pandas as pd
from app.utils.logger import log

model = None

def load_model(csv_path=None):
    global model

    # Get the directory of this file
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Default path if not provided
    if csv_path is None:
        csv_path = os.path.join(base_dir, "Trainingsdaten_Timmi.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"[Model] Training file not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path)

        # Ensure at least one feature column and a label
        if df.shape[1] < 2:
            raise ValueError("[Model] Training CSV must contain at least 2 columns (label + features).")

        # Separate label and features
        y = df["Label"].values
        X = df.drop(columns=["Label"]).values  # Use all remaining columns as features

        model = KNeighborsClassifier(n_neighbors=1)
        model.fit(X, y)
        log(f"[Model] Model trained successfully on {len(X)} samples with {X.shape[1]} features.")

    except Exception as e:
        log(f"[Model] Error during model training: {e}")
        raise

def classify_sample(sample):
    global model
    if model is None:
        raise ValueError("[Model] Model has not been loaded. Please call load_model() first.")
    
    # Add debugging and validation
    log(f"[Model] classify_sample called with sample type: {type(sample)}, value: {sample}")
    
    # Ensure sample is a list or array of numbers
    if isinstance(sample, dict):
        raise TypeError(f"[Model] Expected list/array of numbers, got dict: {sample}")
    
    try:
        sample_array = np.array(sample, dtype=float).reshape(1, -1)  # Reshape for a single prediction
        prediction = model.predict(sample_array)[0]
        return prediction
    except Exception as e:
        log(f"[Model] Error in classify_sample: {e}, sample: {sample}", level="ERROR")
        raise