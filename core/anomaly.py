import numpy as np
import pandas as pd

def compute_reconstruction_error(original, reconstructed):
    # Mean squared error per sequence
    errors = np.mean((original - reconstructed) ** 2, axis=(1, 2))
    return errors


def adaptive_threshold(errors, window=100, k=3):
    errors_series = pd.Series(errors)

    rolling_mean = errors_series.rolling(window=window).mean()
    rolling_std = errors_series.rolling(window=window).std()

    threshold = rolling_mean + k * rolling_std

    return threshold.bfill().values


def detect_anomalies(errors, threshold):
    return errors > threshold