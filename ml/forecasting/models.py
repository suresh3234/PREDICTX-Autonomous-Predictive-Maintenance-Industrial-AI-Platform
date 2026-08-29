import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor


class RidgeForecaster:
    """
    Multi-output baseline regressor using Ridge Regression.
    Predicts 15 targets (5 sensors x 3 horizons) simultaneously.
    """

    def __init__(self, alpha=1.0, random_state=42):
        self.model = MultiOutputRegressor(Ridge(alpha=alpha, random_state=random_state))

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.model.fit(X, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)


class PyTorchForecasterLSTM(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 64), nn.ReLU(), nn.Linear(64, output_dim)
        )

    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_dim)
        lstm_out, _ = self.lstm(x)
        # Gather hidden state of the last time step
        last_step_out = lstm_out[:, -1, :]
        return self.fc(last_step_out)


class LSTMForecaster:
    """
    PyTorch LSTM model for multi-output time-series sensor forecasting.
    """

    def __init__(
        self,
        seq_length=24,
        hidden_dim=64,
        num_layers=2,
        epochs=10,
        batch_size=128,
        lr=0.005,
    ):
        self.seq_length = seq_length
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.model = None

    def fit(self, X_seq: np.ndarray, y: np.ndarray):
        input_dim = X_seq.shape[2]
        output_dim = y.shape[1]
        self.model = PyTorchForecasterLSTM(
            input_dim, output_dim, self.hidden_dim, self.num_layers
        )

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        # Convert to PyTorch dataset
        tensor_X = torch.tensor(X_seq, dtype=torch.float32)
        tensor_y = torch.tensor(y, dtype=torch.float32)

        dataset = torch.utils.data.TensorDataset(tensor_X, tensor_y)
        dataloader = torch.utils.data.DataLoader(
            dataset, batch_size=self.batch_size, shuffle=True
        )

        self.model.train()
        for _epoch in range(self.epochs):
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                preds = self.model(batch_X)
                loss = criterion(preds, batch_y)
                loss.backward()
                optimizer.step()

        return self

    def predict(self, X_seq: np.ndarray) -> np.ndarray:
        self.model.eval()
        tensor_X = torch.tensor(X_seq, dtype=torch.float32)
        with torch.no_grad():
            preds = self.model(tensor_X).numpy()
        return preds
