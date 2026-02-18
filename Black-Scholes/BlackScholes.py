import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class BlackScholes:
    def __init__(self, S, K, T, r, sigma):
        self.S = S  # underlying price
        self.K = K  # strike
        self.T = T  # time to maturity (in years)
        self.r = r  # risk‑free rate
        self.sigma = sigma  # volatility

def calc_d1(bs: BlackScholes):
    numerator = np.log(bs.S / bs.K) + (bs.r + 0.5 * bs.sigma ** 2) * bs.T
    denominator = bs.sigma * np.sqrt(bs.T)
    return numerator / denominator

def calc_d1_and_d2(black_scholes: BlackScholes):
    d1 = calc_d1(black_scholes)

    return d1 , d1 - black_scholes.sigma * np.sqrt(black_scholes.T)

def price_call(black_scholes: BlackScholes):
    d1, d2 = calc_d1_and_d2(black_scholes)
    N_d1 = norm.cdf(d1)
    N_d2 = norm.cdf(d2)

    S = black_scholes.S
    K = black_scholes.K
    r = black_scholes.r
    T = black_scholes.T

    return S * N_d1 - K * N_d2 * np.exp(-r * T)

def price_put(black_scholes: BlackScholes):
    d1, d2 = calc_d1_and_d2(black_scholes)
    N_d1 = norm.cdf(-d1)
    N_d2 = norm.cdf(-d2)

    S = black_scholes.S
    K = black_scholes.K
    r = black_scholes.r
    T = black_scholes.T

    return K * np.exp(-r * T) * N_d2 - S * N_d1

def calc_greeks(bs: BlackScholes):
    d1, d2 = calc_d1_and_d2(bs)
    cdf_N_d1 = norm.cdf(d1)
    pdf_N_d1 = norm.pdf(d1)
    cdf_N_d2 = norm.cdf(d2)
    negative_cdf_N_d2 = norm.cdf(-d2)

    S = bs.S
    K = bs.K
    r = bs.r
    T = bs.T
    sqrt_T = np.sqrt(T)
    sigma = bs.sigma

    exp_r_and_t = np.exp(-r * T)

    #directional risk
    delta_call = cdf_N_d1
    delta_put = cdf_N_d1 - 1

    #convexity
    gamma = pdf_N_d1 / (S * sigma * sqrt_T)

    #volatiltiy risk
    vega = S * sqrt_T * pdf_N_d1

    #time decay (for year)
    theta_call = - (S * pdf_N_d1 * sigma / (2 * sqrt_T)) - (r * K * exp_r_and_t * cdf_N_d2)
    theta_put = - (S * pdf_N_d1 * sigma / (2 * sqrt_T)) + (r * K * exp_r_and_t * negative_cdf_N_d2)

    #intrest rate risk
    rho_call = K * T * exp_r_and_t * cdf_N_d2
    rho_put = - K * T * exp_r_and_t * negative_cdf_N_d2

    return {
        'delta_call': delta_call,
        'delta_put': delta_put,
        'gamma': gamma,
        'vega': vega,
        'theta_call': theta_call,
        'theta_put': theta_put,
        'rho_call': rho_call,
        'rho_put': rho_put,
    }

def implied_volatility(bs: BlackScholes, market_price, sigma, is_call = True, precision = 1e-5, max_iteration = 100):
    for i in range(max_iteration):
        bs.sigma = sigma

        #calc price and vega with curr sigma
        if is_call:
            price = price_call(bs)
        else:
            price = price_put(bs)

        vega = calc_greeks(bs)['vega']

        diff = market_price - price

        #chk for convergence
        if abs(diff) < precision:
            return sigma

        #avoid division by zero
        if abs(vega) < 1e-8:
            break

        #Newton-Raphson step
        sigma = sigma + diff / vega

    return sigma


def parse_numbers(raw: str) -> list[float]:
    cleaned = []
    for token in raw.replace(",", " ").split():
        try:
            cleaned.append(float(token))
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


def get_historical_volatility(prices):
    prices = np.array(prices)
    log_ret = np.log(prices[1:] / prices[:-1])
    #annualize volatility
    return np.std(log_ret, ddof=1) * np.sqrt(365)


# --- Main Execution Loop GENERATED WITH AI ---

def main():
    while True:
        print("\n" + "=" * 40)
        print("   BLACK-SCHOLES OPTION PRICER & GREEKS")
        print("=" * 40)

        filename = input("Enter filename (e.g., 'btc.csv') or 'e' to exit: ")
        if filename.lower() == 'e':
            break

        prices = load_numbers_from_file(filename)
        if not prices:
            print("No data found.")
            continue

        # 1. Auto-Calibrate Inputs from Data
        S = prices[-1]
        sigma_hist = get_historical_volatility(prices)

        print(f"\n[Data Analysis]")
        print(f"Current Spot Price (S): ${S:,.2f}")
        print(f"Historical Volatility (σ): {sigma_hist:.2%}")

        # 2. User Inputs for Option Details
        try:
            K = float(input("Enter Strike Price (K): "))
            days = float(input("Days to Expiration: "))
            r = float(input("Risk-Free Rate (e.g., 0.045 for 4.5%): "))
        except ValueError:
            print("Invalid number entered.")
            continue

        T = days / 365.0

        # 3. Initialize Object & Run Pricing
        bs = BlackScholes(S, K, T, r, sigma_hist)

        call_price = price_call(bs)
        put_price = price_put(bs)
        greeks = calc_greeks(bs)

        # 4. Output Results
        print(f"\n[Theoretical Fair Value]")
        print(f"CALL Price: ${call_price:,.2f}")
        print(f"PUT Price:  ${put_price:,.2f}")

        print(f"\n[Risk Profile / Greeks]")
        print(f"{'Greek':<10} | {'Call':<10} | {'Put':<10} | {'Meaning'}")
        print("-" * 55)
        print(
            f"{'Delta':<10} | {greeks['delta_call']:<10.4f} | {greeks['delta_put']:<10.4f} | Exposure ($ per $1 move)")
        print(f"{'Gamma':<10} | {greeks['gamma']:<10.6f} | {greeks['gamma']:<10.6f} | Acceleration (Risk of blowout)")
        print(
            f"{'Theta':<10} | {greeks['theta_call'] / 365:<10.2f} | {greeks['theta_put'] / 365:<10.2f} | Daily Time Decay ($)")
        print(
            f"{'Vega':<10} | {greeks['vega'] * 0.01:<10.2f} | {greeks['vega'] * 0.01:<10.2f} | Value change per 1% Vol spike")
        print(
            f"{'Rho':<10} | {greeks['rho_call'] * 0.01:<10.2f} | {greeks['rho_put'] * 0.01:<10.2f} | Sensitivity to Rates")

        # 5. Implied Volatility Solver
        mkt_price_input = input("\nEnter Market Price of the CALL to find IV (or Press Enter to skip): ")
        if mkt_price_input.strip():
            try:
                mkt_price = float(mkt_price_input)
                # Pass a copy of the object or reset sigma after, here we pass current
                # Initial guess can be historical vol
                iv = implied_volatility(bs, mkt_price, sigma=sigma_hist, is_call=True)

                print(f"Implied Volatility (IV): {iv:.2%}")
                diff = iv - sigma_hist
                status = "OVERPRICED" if diff > 0 else "UNDERPRICED"
                print(f"Market is pricing risk {diff * 100:+.2f}% vs History -> {status}")
            except Exception as e:
                print(f"IV Calculation Error: {e}")

        # 6. Scenario Visualization (The "Hockey Stick" & "Gamma Spike")
        print("\nGenerating Scenario Plot...")

        # Create a range of spot prices +/- 20%
        spot_range = np.linspace(S * 0.8, S * 1.2, 100)
        call_values = []
        gamma_values = []

        # Save original S to restore later
        original_S = bs.S

        for spot in spot_range:
            bs.S = spot  # Update object
            call_values.append(price_call(bs))
            gamma_values.append(calc_greeks(bs)['gamma'])

        bs.S = original_S  # Restore

        # Plotting
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

        # Price Plot
        ax1.plot(spot_range, call_values, label='Theoretical Call Price', color='blue', linewidth=2)
        # Intrinsic Value (Payoff at expiry)
        intrinsic = np.maximum(spot_range - K, 0)
        ax1.plot(spot_range, intrinsic, label='Intrinsic Value (Expiry)', color='gray', linestyle='--')

        ax1.axvline(S, color='orange', linestyle=':', label='Current Spot')
        ax1.axvline(K, color='black', linewidth=1, label='Strike')
        ax1.set_title(f"Option Price Scenario (Strike: ${K})")
        ax1.set_ylabel("Price ($)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Gamma Plot
        ax2.plot(spot_range, gamma_values, color='red', label='Gamma (Convexity)')
        ax2.fill_between(spot_range, gamma_values, color='red', alpha=0.1)
        ax2.axvline(S, color='orange', linestyle=':', label='Current Spot')
        ax2.axvline(K, color='black', linewidth=1, label='Strike')
        ax2.set_title("The Death Zone: Gamma Risk Exposure")
        ax2.set_xlabel("Spot Price ($)")
        ax2.set_ylabel("Gamma Value")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()