import numpy as np
import pandas as pd


btc_data = pd.read_csv('btc_data.csv').dropna()

btc_RSI = btc_data['RSI_14'].tolist()
#normalize RSI_14
btc_RSI_mean = np.mean(btc_RSI)
btc_RSI_std = np.std(btc_RSI)
btc_RSI = [(x - btc_RSI_mean) / btc_RSI_std for x in btc_RSI]

#btc days
btc_days = [x for x in range(len(btc_data))]
#normalize days
btc_days_mean = np.mean(btc_days)
btc_days_std = np.std(btc_days)
btc_days = [(x - btc_days_mean) / btc_days_std for x in btc_days]


#btc return in 5 days
btc_return_5d = btc_data["future_return_5d"].tolist()
#normalize return_5d
btc_return_5d_mean = np.mean(btc_return_5d)
btc_return_5d_std = np.std(btc_return_5d)
btc_return_5d = [(x - btc_return_5d_mean) / btc_return_5d_std for x in btc_return_5d]
actual_learning_rate = 0.01

theta_0 = 0
theta_1 = 0
theta_2 = 0
cost_function = 30
max_iterations = 100000
prev_cost = 0
iteration = 0
standard_deviation = 0
tolerance = 1e-8
no_improvement_count = 0
max_no_improvement = 100

def approx_value(theta0,theta1, theta2, x1, x2):
    return theta0 + theta1 * x1 + theta2 * x2 

def calc_cost_function(theta0, theta1, theta2, final_answer, variable_1, variable_2):
    return 1/(2 * len(final_answer)) * sum((approx_value(theta0, theta1, theta2, variable_1[x], variable_2[x]) - final_answer[x])**2 for x in range(len(variable_1)))

def update_theta0(theta0, theta1, theta2, final_answer, variable_1, variable_2, learning_rate):
    return theta0 - learning_rate * (1/len(final_answer) * sum((approx_value(theta0, theta1, theta2, variable_1[x], variable_2[x]) - final_answer[x]) for x in range(0, len(final_answer))))

def update_theta_1(theta0, theta1, theta2, final_answer, variable_1, variable_2, learning_rate):
    return theta1 - learning_rate * (1/len(final_answer)) * sum((approx_value(theta0, theta1, theta2, variable_1[x], variable_2[x]) - final_answer[x]) * variable_1[x] for x in range(0, len(final_answer)))

def update_theta_2(theta0, theta1, theta2, final_answer, variable_1, variable_2, learning_rate):
    return theta2 - learning_rate * (1/len(final_answer)) * sum((approx_value(theta0, theta1, theta2, variable_1[x], variable_2[x]) - final_answer[x]) * variable_2[x] for x in range(0, len(final_answer)))

while cost_function > 0.01 and iteration < max_iterations:
    cost_function = calc_cost_function(theta_0, theta_1, theta_2, btc_return_5d, btc_RSI, btc_days)

    if abs(prev_cost - cost_function) < tolerance:
        no_improvement_count += 1
        if no_improvement_count >= max_no_improvement:
            print(f"Converged at iteration {iteration}")
            break
    else:
        no_improvement_count = 0

    prev_cost = cost_function
    temp_theta_0 = update_theta0(theta_0, theta_1, theta_2, btc_return_5d, btc_RSI, btc_days, actual_learning_rate)
    temp_theta_1 = update_theta_1(theta_0, theta_1, theta_2, btc_return_5d, btc_RSI, btc_days, actual_learning_rate)
    temp_theta_2 = update_theta_2(theta_0, theta_1, theta_2, btc_return_5d, btc_RSI, btc_days, actual_learning_rate)
    theta_0 = temp_theta_0
    theta_1 = temp_theta_1
    theta_2 = temp_theta_2
    standard_deviation = np.sqrt(2 * cost_function)
    iteration += 1
    if iteration % 100 == 0:
        print(f"Cost function: {cost_function} at iteration {iteration}. Theta_0: {theta_0}, Theta_1: {theta_1}, Theta_2: {theta_2}, Standard Deviation: {standard_deviation}")


print(f"FINAL COST FUNCTION: {cost_function}\n Theta_0: {theta_0},\n Theta_1: {theta_1},\n Theta_2: {theta_2}\n Standard Deviation: {standard_deviation}")
