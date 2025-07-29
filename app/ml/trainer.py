from app.ml.model import load_model
from app.utils.logger import log

def train_from_csv(csv_path="Trainingsdaten_Timmi.csv"):
    """
    Train model using a CSV file.
    """
    try:
        load_model(csv_path)
        log(f"[Trainer] Model training completed from file: {csv_path}")
    except Exception as e:
        log(f"[Trainer] Training failed: {e}")
