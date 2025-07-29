from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import pandas as pd
import os
from app.utils.logger import log

model = None

def load_model(csv_path="Trainingsdaten_Timmi.csv"):
    """
    Loads and trains the kNN model using the provided CSV training data.
    """
    global model

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"[Model] Training file not found: {csv_path}")

    try:
        df = pd.read_csv(csv_path)

        # Ensure there are at least 3 columns (label + 2 features)
        if df.shape[1] < 3:
            raise ValueError("[Model] Training CSV must contain at least 3 columns.")

        X = df.iloc[:, 1:3].values  # Feature columns (GRW, FF)
        y = df.iloc[:, 0].values    # Labels

        model = KNeighborsClassifier(n_neighbors=1)
        model.fit(X, y)
        log(f"[Model] Model trained successfully on {len(X)} samples.")

    except Exception as e:
        log(f"[Model] Error during model training: {e}")
        raise

def classify_sample(features):
    """
    Predict the class label based on extracted features.
    """
    global model

    if model is None:
        raise ValueError("[Model] Model not loaded. Call load_model() first.")

    try:
        feature_vector = np.array([[features["GRW"], features["FF"]]])
        prediction = model.predict(feature_vector)
        return int(prediction[0])
    except Exception as e:
        log(f"[Model] Prediction failed: {e}")
        return -1  # or raise depending on desired behavior
