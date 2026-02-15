import numpy as np
import matplotlib.pyplot as plt


#calc volatility and corrected drift
def calc_sigma_and_mu_daily(prices: list[float]):
    prices = np.array(prices)
    log_return = np.log(prices[1:] / prices[:-1])
    sigma_daily = np.std(log_return, ddof=1)
    return sigma_daily, np.mean(log_return) - 1/2 * sigma_daily ** 2

#Geometric Brownian Motion, mu = drift, sigma = volatility
def wiener_process_daily(current_price, days, mu, sigma):
    prices = []
    t = 1

    for i in range(days):
        z = np.random.normal(0, 1)
        current_price = current_price * np.exp(mu * t + sigma * np.sqrt(t) * z)
        prices.append(float(current_price))

    return prices

#this is my attempt of vectorization on the GME model
def vectorize_simulation(s0,days, reps, mu,sigma):
    z = np.random.normal(0, 1, (reps, days))
    daily_returns = np.exp(mu + sigma * z)
    return s0 * np.cumprod(daily_returns, axis=1)

def parse_numbers(raw: str) -> list[int]:
    cleaned = []
    for token in raw.replace(",", " ").split():
        try:
            cleaned.append(float(token) if "." in token else int(token))
        except ValueError:
            print(f"Warning: '{token}' is not a number and was ignored.")
    return cleaned

def load_numbers_from_file(path: str) -> list[int]:
    try:
        with open(path, "r") as f:
            raw = f.read()
        print(f"Loaded data from: {path}")
        return parse_numbers(raw)
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
        return []
    except Exception as e:
        print(f"Unexpected error reading file: {e}")
        return []


def main():
    while True:
        simulations = []

        filename = input("Enter the filename with extension(e to exit): ")

        #exit function
        if filename == "e":
            return False

        raw = load_numbers_from_file(filename)
        sigma, mu = calc_sigma_and_mu_daily(raw)

        days = int(input("Enter the number of day(s) to simulate: ")) + 1
        reps = int(input("Enter the number of simulation(s): "))

        simulations = vectorize_simulation(raw[-1], days, reps, mu, sigma)

        print()
        simulations = np.array(simulations)
        mean_simulations = simulations.mean(axis=0)

        #how much history to show
        hist_window = min(len(raw), days)
        hist_slice = raw[-hist_window:]

        #x ranges
        hist_x = range(hist_window)  # 0 ... hist_window-1
        future_x = range(hist_window - 1, hist_window - 1 + days)

        plt.figure(figsize=(12, 6))

        #historical slice
        plt.plot(hist_x, hist_slice, label="Historical Price", color="orange")

        #vertical seperator
        plt.axvline(
            x=hist_window - 1,
            color="black",
            linestyle="--",
            linewidth=2,
            label="Forecast Start"
        )
        #first 10 simulated path
        for path in simulations[:10]:
            plt.plot(future_x, path, color="grey", linestyle="dashed", alpha=0.4)

        #mean path
        plt.plot(future_x, mean_simulations, label="Predicted Mean", color="green", linewidth=2)

        plt.title("Historical + Future Prediction")
        plt.legend()

        plt.show()

        #histogram of ending prices
        plt.figure(figsize=(12, 6))
        ending_prices = simulations[:, -1]

        plt.hist(ending_prices, bins=50, color="green", edgecolor="black")

        #5th percentile
        plt.axvline(np.percentile(ending_prices, 5), color='r', linestyle='dashed', label="5% VaR")
        plt.title("Distribution of Ending Prices")
        plt.legend()

        plt.show()

        profit_paths = np.sum(ending_prices > raw[-1])
        prob_profit = (profit_paths / reps) * 100

        print(f"Probability of Profit: {prob_profit:.2f}%")
        print(f"5% Value at Risk (VaR): ${np.percentile(ending_prices, 5):.2f}")

        print()





if __name__ == "__main__":
    main()

