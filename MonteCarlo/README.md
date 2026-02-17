Monte Carlo Asset Simulator

This project moves from analyzing historical data to probabilistic forecasting. 
I implemented a Geometric Brownian Motion (GBM) model to simulate thousands of potential future price paths for cryptocurrency.

What I learned:
I mastered the implementation of Geometric Brownian Motion and the importance of volatility drag in price projections. 
I learned to transition from slow Python loops to high-performance NumPy vectorization, enabling the simulation of 10,000+ scenarios in milliseconds. 
Additionally, I integrated Matplotlib to visualize the "fan" of possibilities and the log-normal distribution of ending prices to calculate Value at Risk (VaR).

How to Run:

1. Install Dependencies

        pip install -r requirements.txt
2. Start the Simulator

         python MonteCarloGBM.py or python MonteCarloHeston.py


3. Configure Simulation

    Load your cryptocurrency `.csv`, enter the number of days to forecast, and set the number of trials (e.g., 10,000).

4. Analyze Results

    The script will generate a path chart showing the predicted mean and a histogram identifying the 5% probability "worst-case" price target.

P.S: This is my first time using vectorization, so the jump from nested loops to a vectorized matrix approach was a mesmerizing to say the least.