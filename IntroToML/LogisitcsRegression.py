import numpy as np
import cupy as cp
import pandas as pd

def normalize(data):
    return (data - cp.mean(data)) / cp.std(data), cp.mean(data), cp.std(data)

def get_learning_rate(initial_lr, iteration, decay_rate=0.99, decay_steps=1000):
    return initial_lr * (decay_rate ** (iteration / decay_steps))

def sigmoid(z):
    return 1 / (1 + cp.exp(-z))

def predict_proba(thetas, x_row):
    z = cp.dot(thetas, x_row)
    return sigmoid(z)

def predict_class(thetas, x):
    return 1 if predict_proba(thetas, x) >= 0.5 else 0

def calc_cost_and_update_thetas(thetas, y, x, learning_rate):
    m = len(y)
    X = cp.column_stack([cp.ones(m), x])

    preds = sigmoid(X @ thetas)
    preds = cp.clip(preds, 1e-7, 1 - 1e-7)
    cost = -(1/m) * cp.sum(y * cp.log(preds) + (1 - y) * cp.log(1 - preds))
    gradient = (1/m) * X.T @ (preds - y)
    new_thetas = thetas - learning_rate * gradient

    return float(cost), new_thetas

def main():
    max_iterations = 100000
    initial_learning_rate = 0.01
    iterations = 0
    cost = 30
    prev_cost = 0
    tolerance = 1e-7
    no_improvement_count = 0
    max_no_improvement = 1000

    data = pd.read_csv('cats_vs_dogs.csv').dropna()

    x_values = [str(x) for x in range(0, 4096)]
    x_train = data[x_values].values
    y_train = data["label"].values

    #update to cupy for faster calculations
    x_train, train_mean, train_std = normalize(cp.array(x_train))
    y_train = cp.array(y_train)
    thetas = cp.zeros(x_train.shape[1] + 1)

    print("---Starting Training---")
    for _ in range(max_iterations):
        learning_rate = get_learning_rate(initial_learning_rate, iterations)
        cost, thetas = calc_cost_and_update_thetas(thetas, y_train, x_train, learning_rate)
        iterations += 1
        print(f"Iteration: {iterations} Cost function: {cost}")

        if abs(prev_cost - cost) < tolerance:
            no_improvement_count += 1
            if no_improvement_count >= max_no_improvement:
                print(f"Converged at iteration {iterations}")
                break
        else:
            no_improvement_count = 0

        prev_cost = cost

    print(f"---FINAL RESULTS---\n Cost Function: {cost}\n Initial_Learning Rate: {initial_learning_rate}, Final Learning Rate: {learning_rate}")
    #save parameters
    np.save('thetas.npy', cp.asnumpy(thetas))
    np.save('train_stats.npy', np.array([train_mean.get(), train_std.get()]))

    preds = sigmoid(cp.column_stack([cp.ones(len(y_train)), x_train]) @ thetas)
    predicted_classes = (preds >= 0.5).astype(int)
    accuracy = float(cp.mean(predicted_classes == y_train)) * 100
    print(f"Training Accuracy: {accuracy:.2f}%")


if __name__ == '__main__':
    main()
