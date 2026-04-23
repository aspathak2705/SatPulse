import torch
import numpy as np
import pandas as pd

from models.lstm_autoencoder import LSTMAutoencoder
from data.loader import load_selected_parameters
from core.preprocess import clean_data, scale_data, create_sequences
from core.anomaly import compute_reconstruction_error, adaptive_threshold
from models.isolation_forest import train_isolation_forest, predict_isolation_forest

# Config
DATA_PATH = "data/raw"
WINDOW_SIZE = 20

selected_params = ["AMT00102", "AMT00103"]

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load + preprocess
df = load_selected_parameters(DATA_PATH, selected_params)
df = clean_data(df)

scaled_data, scaler = scale_data(df)
sequences = create_sequences(scaled_data, WINDOW_SIZE)

# Tensor
X = torch.tensor(sequences, dtype=torch.float32).to(device)

# Load model
model = LSTMAutoencoder(n_features=X.shape[2]).to(device)
model.load_state_dict(torch.load("models/lstm_autoencoder.pth", map_location=device))
model.eval()

# Reconstruct
with torch.no_grad():
    reconstructed = model(X).cpu().numpy()

# Error
errors = compute_reconstruction_error(sequences, reconstructed)

# Adaptive threshold
adaptive_thresh = adaptive_threshold(errors)
lstm_anomalies = errors > adaptive_thresh

# Isolation Forest
flat_data = scaled_data[WINDOW_SIZE:]
iso_model = train_isolation_forest(flat_data)
iso_preds = predict_isolation_forest(iso_model, flat_data)
iso_anomalies = iso_preds == -1

# Hybrid
final_anomalies = lstm_anomalies | iso_anomalies

print("LSTM anomalies:", lstm_anomalies.sum())
print("Isolation Forest anomalies:", iso_anomalies.sum())
print("Final anomalies:", final_anomalies.sum())

# Save results
results = pd.DataFrame({
    "time_index": np.arange(len(errors)),
    "error": errors,
    "lstm_anomaly": lstm_anomalies,
    "iso_anomaly": iso_anomalies,
    "final_anomaly": final_anomalies
})

results.to_csv("outputs/results.csv", index=False)
print("Results saved!")