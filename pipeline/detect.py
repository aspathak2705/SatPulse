import torch
import numpy as np
import pandas as pd

from models.lstm_autoencoder import LSTMAutoencoder
from data.loader import load_selected_parameters
from core.preprocess import clean_data, scale_data, create_sequences
from core.anomaly import compute_reconstruction_error, get_threshold, detect_anomalies

# Config
DATA_PATH = "data/raw"
WINDOW_SIZE = 20

selected_params = ["AMT00102", "AMT00103"]

# Load + preprocess
df = load_selected_parameters(DATA_PATH, selected_params)
df = clean_data(df)

scaled_data, scaler = scale_data(df)
sequences = create_sequences(scaled_data, WINDOW_SIZE)

# Convert to tensor
X = torch.tensor(sequences, dtype=torch.float32)

# Load model
model = LSTMAutoencoder(n_features=X.shape[2])
model.load_state_dict(torch.load("models/lstm_autoencoder.pth"))
model.eval()

# Predict (reconstruct)
with torch.no_grad():
    reconstructed = model(X).numpy()

# Compute error
errors = compute_reconstruction_error(sequences, reconstructed)

# Threshold
threshold = get_threshold(errors)

# Detect anomalies
anomalies = detect_anomalies(errors, threshold)

result = pd.DataFrame({
    "error":errors,
    "anomaly":anomalies
})

result.to_csv("outputs/results.csv",index=False)
