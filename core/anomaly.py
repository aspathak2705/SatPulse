import numpy as np

def compute_reconstruction_error(original, reconstructed):
    # Mean squared error per sequence
    errors = np.mean((original - reconstructed) ** 2, axis=(1, 2))
    return errors


def get_threshold(errors, method="percentile"):
    if method == "percentile":
        return np.percentile(errors, 95)  # top 5% = anomalies
    elif method == "std":
        return errors.mean() + 3 * errors.std()
    else:
        raise ValueError("Unknown method")


def detect_anomalies(errors, threshold):
    return errors > threshold