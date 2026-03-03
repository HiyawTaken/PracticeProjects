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
    validation_cost = 30
    prev_cost = 0
    tolerance = 1e-7
    no_improvement_count = 0
    max_no_improvement = 1000

    #update this two file to adjust for a different dataset
    csv_file = "btc_data.csv"
    label_name = "future_5d_label"
    coulmns_to_be_dropped = ["Open", "High", "Low", "Close", "Volume", "future_return_5d", "SMA_10", "SMA_20", "SMA_50", "EMA_20", "max_20", "min_20", "MACD", "MACD_Signal", "vwap"]

    data = pd.read_csv(csv_file).dropna()
    if 'Date' in data.columns:
        data = data.set_index('Date')
    data = data.select_dtypes(include=[np.number])
    data = data.drop(columns=coulmns_to_be_dropped)

    #train/validate/test 80 10 10
    n = len(data)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)

    training_data = data.iloc[:train_end]
    validation_data = data.iloc[train_end: val_end]
    test_data = data.iloc[val_end:]

    x_values = [col for col in data.columns if col != label_name]

    x_train = training_data[x_values].values
    y_train = training_data[label_name].values

    x_validate = validation_data[x_values].values
    y_validate = validation_data[label_name].values

    x_test = test_data[x_values].values
    y_test = test_data[label_name].values

    #update to cupy for faster calculations
    x_train, train_mean, train_std = normalize(cp.array(x_train))
    y_train = cp.array(y_train)
    thetas = cp.zeros(x_train.shape[1] + 1)

    x_validate = (cp.array(x_validate) - train_mean) / train_std
    y_validate = cp.array(y_validate)

    x_test= (cp.array(x_test) - train_mean) / train_std
    y_test = cp.array(y_test)

    print("---Starting Training---")
    try:
        #uncomment the following line and comment the get learning rate line after the for loop for a static learning rate
        learning_rate = initial_learning_rate
        for _ in range(max_iterations):
            #learning_rate = get_learning_rate(initial_learning_rate, iterations)
            cost, thetas = calc_cost_and_update_thetas(thetas, y_train, x_train, learning_rate)
            validation_cost = calc_cost_and_update_thetas(thetas, y_validate, x_validate, learning_rate)[0]
            iterations += 1
            print(f"Iteration: {iterations} Training Cost function: {cost} Validation Cost function: {validation_cost}")

            if abs(prev_cost - cost) < tolerance:
                no_improvement_count += 1
                if no_improvement_count >= max_no_improvement:
                    print(f"Converged at iteration {iterations}")
                    break
            else:
                no_improvement_count = 0

            prev_cost = cost
    except KeyboardInterrupt:
        print("Training stopped by user.")

    finally:
        print(f"\n---FINAL RESULTS---\n Cost Function: {cost}\n Validation Cost Function: {validation_cost}\n Initial_Learning Rate: {initial_learning_rate}, Final Learning Rate: {learning_rate}")

        #calc accuracy using test data
        X_test = cp.column_stack([cp.ones(len(x_test)), x_test])
        preds = sigmoid(X_test @ thetas)
        labels = (preds >= 0.5).astype(int).tolist()

        true_positive= 0
        true_negative= 0
        false_positive= 0
        false_negative= 0

        for i in range(len(labels)):
            if labels[i] == 1:
                if y_test[i] == 1:
                    true_positive += 1
                if y_test[i] == 0:
                    false_positive += 1
            elif labels[i] == 0:
                if y_test[i] == 1:
                    false_negative += 1
                if y_test[i] == 0:
                    true_negative += 1

        test_accuracy = (true_positive + true_negative)/ len(labels)
        test_precision = true_positive / (true_positive + false_positive) if true_positive + false_positive != 0 else None
        test_recall = true_positive / (true_positive + false_negative) if true_positive + false_negative != 0 else None
        if test_precision is not None and test_recall is not None:
            test_f1 = 2 * test_precision * test_recall / (test_precision + test_recall)
        else:
            test_f1 = None

        #calc majority of the labels for baseline comparision
        one_count = len([x for x in y_train if x == 1])
        zero_count = len([x for x in y_train if x == 0])
        majority_class = 1 if one_count > zero_count else 0

        baseline_accuracy = len([x for x in y_test if x == majority_class]) / len(y_test)

        print(f"\n---TEST DATA RESULTS---\n Accuracy: {test_accuracy}\n Precision: {test_precision}\n Recall: {test_recall}\n F1: {test_f1}\n Baseline Accuracy: {baseline_accuracy}")


        #accuracy on the training data itself
        preds = sigmoid(cp.column_stack([cp.ones(len(y_train)), x_train]) @ thetas)
        predicted_classes = (preds >= 0.5).astype(int)
        accuracy = float(cp.mean(predicted_classes == y_train)) * 100
        print(f"\nTraining Accuracy(on training data): {accuracy:.2f}%")

        #save parameters
        save_files = input("\nWould you like to save these files? (y/n)")
        if save_files == "y":
            np.save(f'thetas_{csv_file}.npy', cp.asnumpy(thetas))
            np.save(f'train_stats_{csv_file}.npy', np.array([train_mean.get(), train_std.get()]))


if __name__ == '__main__':
    main()
