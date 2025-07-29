import os
from app.ml.model import load_model
from app.utils.logger import log

def train_from_csv(csv=None):
    try:
        if csv is None:
            # Path of the current file (trainer.py)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv = os.path.join(current_dir, "Trainingsdaten_Timmi.csv")

        load_model(csv)
        log(f"[Trainer] Model training completed from file: {csv}")
    except Exception as e:
        log(f"[Trainer] Training failed: {e}")
