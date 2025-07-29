import numpy as np
from app.utils.logger import log

def extract_features(signal):
    """
    Extracts GRW (mean abs value), FF (form factor), and Var (variance)
    from a list of numeric signal values.

    Args:
        signal (list or np.ndarray): List of float/int signal samples

    Returns:
        dict: { "GRW": ..., "FF": ..., "Var": ... }
    """
    try:
        signal = np.array(signal)

        if signal.size == 0:
            raise ValueError("Signal is empty.")

        grw = np.mean(np.abs(signal))
        ff = np.sqrt(np.mean(signal ** 2)) / grw if grw != 0 else 0
        var = np.var(signal)

        return {
            "GRW": float(grw),
            "FF": float(ff),
            "Var": float(var)
        }

    except Exception as e:
        log(f"[FeatureExtractor] Failed to extract features: {e}")
        return {"GRW": 0, "FF": 0, "Var": 0}
