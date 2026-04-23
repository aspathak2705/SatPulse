import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from models.lstm_autoencoder import LSTMAutoencoder
from data.loader import load_selected_parameters
from core.preprocess import clean_data, scale_data, create_sequences

# Config
DATA_PATH = "data/raw"
WINDOW_SIZE = 20
BATCH_SIZE = 64
EPOCHS = 5
LR = 1e-3

selected_params = ["AMT00102", "AMT00103"]

# Load & preprocess
df = load_selected_parameters(DATA_PATH, selected_params)
df = clean_data(df)

scaled_data, scaler = scale_data(df)
sequences = create_sequences(scaled_data, WINDOW_SIZE)

# Convert to tensor
X = torch.tensor(sequences, dtype=torch.float32)

dataset = TensorDataset(X, X)  # input = target
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# Model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = LSTMAutoencoder(n_features=X.shape[2]).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

# Training loop
for epoch in range(EPOCHS):
    total_loss = 0

    for batch_x, _ in loader:
        batch_x = batch_x.to(device)

        optimizer.zero_grad()

        output = model(batch_x)

        loss = criterion(output, batch_x)
        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {total_loss:.4f}")

# Save model
torch.save(model.state_dict(), "models/lstm_autoencoder.pth")
print("Model saved!")