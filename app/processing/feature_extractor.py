import numpy as np
from app.utils.logger import log

def extract_features(signal):
    """
    Extracts 9 features from a list of numeric signal values to match the training data.

    Returns a dict with:
        I-L1_SigStat-MW, I-L1_StatSig-qMW, I-L1_Stat-StdAW, I-L1_Stat-Var,
        I-L1_Stat-Wb, I-L1_Stat-N6M, I-L1_Sig-QWM, I-L1_Sig-GRW, I-L1_Sig-FF
    """
    try:
        signal = np.array(signal)

        if signal.size == 0:
            raise ValueError("Signal is empty.")

        # Example calculations — adjust as needed to match your dataset logic
        mw = np.mean(signal)
        qmw = np.median(signal)  # Assumed approximation
        stdaw = np.std(signal)
        var = np.var(signal)
        wb = np.max(signal) - np.min(signal)
        n6m = np.sum(signal > mw)  # count of values above mean
        qwm = np.quantile(signal, 0.75)  # example: 75th percentile
        grw = np.mean(np.abs(signal))
        ff = np.sqrt(np.mean(signal ** 2)) / grw if grw != 0 else 0

        return {
            "I-L1_SigStat-MW": float(mw),
            "I-L1_StatSig-qMW": float(qmw),
            "I-L1_Stat-StdAW": float(stdaw),
            "I-L1_Stat-Var": float(var),
            "I-L1_Stat-Wb": float(wb),
            "I-L1_Stat-N6M": float(n6m),
            "I-L1_Sig-QWM": float(qwm),
            "I-L1_Sig-GRW": float(grw),
            "I-L1_Sig-FF": float(ff)
        }

    except Exception as e:
        log(f"[FeatureExtractor] Failed to extract features: {e}")
        # Return zeros in same order if failed
        return {
            "I-L1_SigStat-MW": 0,
            "I-L1_StatSig-qMW": 0,
            "I-L1_Stat-StdAW": 0,
            "I-L1_Stat-Var": 0,
            "I-L1_Stat-Wb": 0,
            "I-L1_Stat-N6M": 0,
            "I-L1_Sig-QWM": 0,
            "I-L1_Sig-GRW": 0,
            "I-L1_Sig-FF": 0
        }
