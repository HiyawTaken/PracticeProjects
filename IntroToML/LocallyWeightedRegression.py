import numpy as np
import pandas as pd

# 1. Load Data
btc_data = pd.read_csv('btc_data.csv').dropna()

# 2. Prepare Time-Series Features
# We create an index (0 to N) representing the passage of days
raw_x = np.arange(len(btc_data))
raw_y = btc_data['Close'].values

# 3. Normalization
# For Time-Series LWR, we MUST normalize X so the tau value (0.1)
# makes sense relative to the distance between days.
def normalize(data):
    return (data - np.mean(data)) / np.std(data), np.mean(data), np.std(data)

x_train, x_mean, x_std = normalize(raw_x)
y_train, y_mean, y_std = normalize(raw_y)

# --- LWR Parameters ---
tau = 50  # Bandwidth: Smaller follows price closer, larger is smoother
learning_rate = 0.05
max_iterations = 100000
tolerance = 1e-7

def get_weights(query_x, x_train, tau):
    return np.exp(-(x_train - query_x) ** 2 / (2 * tau ** 2))

def predict_lwr(query_x, x_train, y_train, tau, lr, iters):
    theta_0, theta_1 = 0.0, 0.0
    weights = get_weights(query_x, x_train, tau)
    m = len(x_train)

    for _ in range(iters):
        predictions = theta_0 + theta_1 * x_train
        errors = predictions - y_train

        # Weighted Gradient Descent
        d_theta0 = (1 / m) * np.sum(weights * errors)
        d_theta1 = (1 / m) * np.sum(weights * errors * x_train)

        new_t0 = theta_0 - lr * d_theta0
        new_t1 = theta_1 - lr * d_theta1

        if abs(new_t0 - theta_0) < tolerance:
            break
        theta_0, theta_1 = new_t0, new_t1

    return theta_0 + theta_1 * query_x

# --- Execution ---

# Example: Predict the price for the "current" day (the last day in the dataset)
# We take the last index, normalize it using the training stats, and predict.
last_day_index = 3000
query_x_scaled = (last_day_index - x_mean) / x_std

prediction_scaled = predict_lwr(query_x_scaled, x_train, y_train, tau, learning_rate, max_iterations)

# Denormalize the result to get the actual USD price
final_price_prediction = (prediction_scaled * y_std) + y_mean

print(f"Prediction for Day {last_day_index}: ${final_price_prediction:.2f}")
print(f"Actual Price on Day {last_day_index}: ${raw_y[-1]:.2f}")
