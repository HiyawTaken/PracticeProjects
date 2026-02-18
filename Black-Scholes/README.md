**Black-Scholes Option Pricing Engine**

This project bridges the gap between stochastic simulation and analytical pricing. 
I implemented a fully vectorized Black-Scholes-Merton (BSM) class to calculate the theoretical "fair value" of Bitcoin options 
and quantify the specific risks associated with them.

**What I Learned**

I implemented the partial differential equations behind the Greeks, Delta, Gamma, Theta, Vega, and Rho, and translated them into high-performance Python code. 
I moved beyond simple pricing to build a Newton-Raphson Solver, allowing me to reverse-engineer Implied Volatility (IV) from live market prices.

Most importantly, I learned to visualize Convexity Risk. 
By plotting the "Death Zone" (Gamma exposure),
I can now mathematically identify the exact price levels where portfolio risk accelerates exponentially.

**How to run**

1. Install Dependencies

        pip install -r requirements.txt

2. Start the Pricing Engine

        python BlackScholes.py

3. Configure Analysis

    - Enter your data file (e.g., btc.csv).
    - The script will auto-calibrate historical volatility ($\sigma$) from the data.
    - Input the Strike Price ($K$) and Days to Expiration.


The script will output:

- Theoretical Prices: Call and Put values based on the BSM model.

- The Greeks: A breakdown of risk sensitivity (e.g., how much value is lost per day to Theta).

- Scenario Charts: A multi-plot visualization showing the "Hockey Stick" payoff diagram and the Gamma risk curve.