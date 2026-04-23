import torch
import torch.nn as nn

class LSTMAutoencoder(nn.Module):
    def __init__(self, n_features, hidden_dim=64):
        super(LSTMAutoencoder, self).__init__()

        self.n_features = n_features
        self.hidden_dim = hidden_dim

        # Encoder
        self.encoder = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True
        )

        # Decoder
        self.decoder = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=n_features,
            num_layers=1,
            batch_first=True
        )

    def forward(self, x):
        # Encode
        encoded, _ = self.encoder(x)

        # Decode
        decoded, _ = self.decoder(encoded)

        return decoded