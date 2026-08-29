import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestRegressor


class RandomForestRULRegressor:
    """
    Random Forest regressor for Remaining Useful Life (RUL).
    Computes dynamic confidence intervals using prediction variance across all estimators.
    """

    def __init__(self, n_estimators=100, max_depth=12, random_state=42, **kwargs):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,
            **kwargs
        )
        self.max_rul = 24.0  # Capped piecewise RUL target

    def fit(self, X: np.ndarray, y: np.ndarray):
        # Clip targets for piecewise linear RUL regression
        y_clipped = np.clip(y, 0.0, self.max_rul)
        self.model.fit(X, y_clipped)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_with_interval(
        self, X: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculates RUL predictions and 95% confidence intervals based on tree variance.
        """
        # Collect predictions from each tree in the forest
        tree_preds = np.array([tree.predict(X) for tree in self.model.estimators_])

        mean_pred = np.mean(tree_preds, axis=0)
        std_pred = np.std(tree_preds, axis=0)

        # 95% CI is approx 1.96 standard deviations
        lower_bound = np.clip(mean_pred - 1.96 * std_pred, 0.0, self.max_rul)
        upper_bound = np.clip(mean_pred + 1.96 * std_pred, 0.0, self.max_rul)

        return mean_pred, lower_bound, upper_bound


class PyTorchLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2
        )
        self.fc = nn.Sequential(nn.Linear(hidden_dim, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, x):
        # x shape: (batch_size, sequence_length, input_dim)
        lstm_out, _ = self.lstm(x)
        # Take the hidden state output of the last sequence step
        last_step_out = lstm_out[:, -1, :]
        return self.fc(last_step_out).squeeze(-1)


class LSTMRULRegressor:
    """
    PyTorch LSTM regressor for sequence-based RUL prediction.
    """

    def __init__(
        self,
        seq_length=24,
        hidden_dim=64,
        num_layers=2,
        epochs=15,
        batch_size=64,
        lr=0.002,
    ):
        self.seq_length = seq_length
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.model = None
        self.max_rul = 24.0
        self.train_mse_variance = 0.0  # Used as general variance proxy for test CI

    def fit(self, X_seq: np.ndarray, y_seq: np.ndarray):
        input_dim = X_seq.shape[2]
        self.model = PyTorchLSTM(input_dim, self.hidden_dim, self.num_layers)

        # Clip targets
        y_clipped = np.clip(y_seq, 0.0, self.max_rul)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

        # Convert to PyTorch dataset
        tensor_X = torch.tensor(X_seq, dtype=torch.float32)
        tensor_y = torch.tensor(y_clipped, dtype=torch.float32)

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

        # Calculate fit MSE variance
        self.model.eval()
        with torch.no_grad():
            all_preds = self.model(tensor_X).numpy()
            self.train_mse_variance = float(np.mean((y_clipped - all_preds) ** 2))

        return self

    def predict(self, X_seq: np.ndarray) -> np.ndarray:
        self.model.eval()
        tensor_X = torch.tensor(X_seq, dtype=torch.float32)
        with torch.no_grad():
            preds = self.model(tensor_X).numpy()
        return np.clip(preds, 0.0, self.max_rul)

    def predict_with_interval(
        self, X_seq: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Returns predictions and confidence intervals using model fitting variance.
        """
        preds = self.predict(X_seq)
        std_dev = np.sqrt(self.train_mse_variance)

        lower_bound = np.clip(preds - 1.96 * std_dev, 0.0, self.max_rul)
        upper_bound = np.clip(preds + 1.96 * std_dev, 0.0, self.max_rul)

        return preds, lower_bound, upper_bound
