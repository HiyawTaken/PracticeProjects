import numpy as np
import matplotlib.pyplot as plt


def calc_kappa(list_of_variances: list[float]):
    # AR(1) regression for mean reversion speed
    if len(list_of_variances) < 2: return 1.0

    x_mean = np.mean(list_of_variances[:-1])
    y_mean = np.mean(list_of_variances[1:])

    numerator = np.sum((list_of_variances[:-1] - x_mean) * (list_of_variances[1:] - y_mean))
    denominator = np.sum((list_of_variances[:-1] - x_mean) ** 2)

    if denominator == 0: return 1.0

    b = numerator / denominator
    return (1 - b) * 365  # annualized kappa


def get_heston_parameters(prices: list[float]):
    prices = np.array(prices)
    #log return
    log_ret = np.log(prices[1:] / prices[:-1])

    variances = (log_ret ** 2) * 365

    #param extraction
    mu = np.mean(log_ret) * 365  #annualized drift
    theta = np.mean(variances)  #long-run mean variance
    v0 = variances[-1]  #intial variance
    kappa = calc_kappa(variances)  #speed of reversion

    d_v = np.diff(variances)
    xi = np.std(d_v) * np.sqrt(365)  #volatility of variance

    #correlation
    if len(d_v) > 1:
        rho = np.corrcoef(log_ret[1:], d_v)[0, 1]
    else:
        rho = -0.7  # Default fallback if data is too short

    return {"mu": mu, "kappa": kappa, "theta": theta, "xi": xi, "rho": rho, "v0": v0}


def simulate_heston(s0, params, days, n_paths):
    dt = 1 / 365
    mu, kappa, theta, xi, rho, v0 = params.values()

    #pre-allocate matrices
    S = np.zeros((days, n_paths))
    V = np.zeros((days, n_paths))
    S[0] = s0
    V[0] = v0

    #correlated bm
    W1 = np.random.normal(0, 1, (days, n_paths))
    W2 = np.random.normal(0, 1, (days, n_paths))
    Z_price = W1
    Z_vol = rho * W1 + np.sqrt(1 - rho ** 2) * W2

    for t in range(1, days):
        #full truncation
        V_prev = np.maximum(V[t - 1], 0)

        #CIR process
        dV = kappa * (theta - V_prev) * dt + xi * np.sqrt(V_prev * dt) * Z_vol[t]
        V[t] = V_prev + dV

        #update price
        dS_drift = (mu - 0.5 * V_prev) * dt
        dS_diff = np.sqrt(V_prev * dt) * Z_price[t]
        S[t] = S[t - 1] * np.exp(dS_drift + dS_diff)

    return S, V


def parse_numbers(raw: str) -> list[float]:
    cleaned = []
    for token in raw.replace(",", " ").split():
        try:
            cleaned.append(float(token) if "." in token else float(token))
        except ValueError:
            pass
    return cleaned


def load_numbers_from_file(path: str) -> list[float]:
    try:
        with open(path, "r") as f:
            return parse_numbers(f.read())
    except Exception as e:
        print(f"Error: {e}")
        return []


def main():
    while True:
        filename = input("Enter the filename with extension (e to exit): ")
        if filename.lower() == "e": break

        raw = load_numbers_from_file(filename)
        if not raw: continue

        params = get_heston_parameters(raw)

        try:
            days = int(input("Enter the number of day(s) to simulate: ")) + 1
            reps = int(input("Enter the number of simulation(s): "))
        except ValueError:
            print("Invalid input.")
            continue

        print("\nRunning Heston Simulation...")
        print(
            f"Parameters: Mu={params['mu']:.2f}, Theta={params['theta']:.2f}, Xi={params['xi']:.2f}, Rho={params['rho']:.2f}")

        #run simulation
        S_matrix, V_matrix = simulate_heston(raw[-1], params, days, reps)

        simulations = S_matrix.T

        print("\nPlotting results...")

        simulations = np.array(simulations)
        mean_simulations = simulations.mean(axis=0)

        #how much history to show
        hist_window = min(len(raw), days)
        hist_slice = raw[-hist_window:]

        #X ranges
        hist_x = range(hist_window)
        #future x starts at the last historical point
        future_x = range(hist_window - 1, hist_window - 1 + days)

        plt.figure(figsize=(12, 6))

        #historical slice
        plt.plot(hist_x, hist_slice, label="Historical Price", color="orange")

        # Vertical separator
        plt.axvline(
            x=hist_window - 1,
            color="black",
            linestyle="--",
            linewidth=2,
            label="Forecast Start"
        )

        #first 10 simulated paths
        for path in simulations[:10]:
            plt.plot(future_x, path, color="grey", linestyle="dashed", alpha=0.4)

        #mean path
        plt.plot(future_x, mean_simulations, label="Predicted Mean", color="green", linewidth=2)

        plt.title(f"Heston Model: Historical + Future Prediction ({days - 1} Days)")
        plt.xlabel("Time Steps")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

        #histogram of ending prices
        plt.figure(figsize=(12, 6))
        ending_prices = simulations[:, -1]

        plt.hist(ending_prices, bins=50, color="green", edgecolor="black", alpha=0.7)

        # 5% VaR
        var_price = np.percentile(ending_prices, 5)
        plt.axvline(var_price, color='r', linestyle='dashed', linewidth=2, label=f"5% VaR: ${var_price:.2f}")

        plt.title("Distribution of Ending Prices (Heston)")
        plt.xlabel("Price")
        plt.ylabel("Frequency")
        plt.legend()
        plt.show()

        #stats
        profit_paths = np.sum(ending_prices > raw[-1])
        prob_profit = (profit_paths / reps) * 100

        print(f"Probability of Profit: {prob_profit:.2f}%")
        print(f"5% Value at Risk (VaR): ${var_price:.2f}")
        print()


if __name__ == "__main__":
    main()