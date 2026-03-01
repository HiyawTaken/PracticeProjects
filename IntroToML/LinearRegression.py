import numpy as np

house_size = [850, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1800]
house_price = [180000, 195000, 210000, 225000, 240000, 255000, 270000, 285000, 300000, 330000]

house_size_mean = np.mean(house_size)
house_size_std = np.std(house_size)

house_price_mean = np.mean(house_price)
house_price_std = np.std(house_price)

#calc z scores
house_size = [(x - house_size_mean) / house_size_std for x in house_size]
house_price = [(x - house_price_mean) / house_price_std for x in house_price]

theta_1 = 0
theta_0 = 0

learning_rate = 0.001
cost_function = 30
max_iterations = 100000
iteration = 0

def approx_value(theta0,theta1, x1):
    return theta0 + theta1 * x1

while cost_function > 0.0000000001 and iteration < max_iterations:
    sum_of_training_data_partial_derivatives_squared = sum((approx_value(theta_0, theta_1, house_size[x]) - house_price[x])**2 for x in range(0, len(house_size)))
    sum_of_training_data_partial_derivatives_1 = sum((approx_value(theta_0, theta_1, house_size[x]) - house_price[x]) * house_size[x] for x in range(0, len(house_size)))
    sum_of_training_data_partial_derivatives_0 = sum((approx_value(theta_0, theta_1, house_size[x]) - house_price[x]) for x in range(0, len(house_size)))

    cost_function = 1/(2 * len(house_size)) * sum_of_training_data_partial_derivatives_squared

    theta_0 = theta_0 - learning_rate * (1/len(house_size)) * sum_of_training_data_partial_derivatives_0
    theta_1 = theta_1 - learning_rate * 1/len(house_size) * sum_of_training_data_partial_derivatives_1
    print(f"theta_0: {theta_0} | theta_1: {theta_1} cost_function: {cost_function}")
    iteration += 1

print(f"FINAL ANSWER:\niterations: {iteration} \ntheta_0: {theta_0} \ntheta_1: {theta_1} \ncost_function: {cost_function}")
