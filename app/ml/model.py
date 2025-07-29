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

        if df.shape[1] < 3:
            raise ValueError("[Model] Training CSV must contain at least 3 columns.")

        X = df.iloc[:, 1:3].values
        y = df.iloc[:, 0].values

        model = KNeighborsClassifier(n_neighbors=1)
        model.fit(X, y)
        log(f"[Model] Model trained successfully on {len(X)} samples.")

    except Exception as e:
        log(f"[Model] Error during model training: {e}")
        raise