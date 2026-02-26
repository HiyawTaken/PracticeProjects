import yfinance as yf
import numpy as np

asset = "BTC-USD"
ticker = yf.Ticker(asset)

historical_prices = ticker.history(period="1y", interval="1d").dropna()

rolling_window = 20
historical_prices[f"SMA_10"] = historical_prices["Close"].rolling(10).mean()
historical_prices[f"SMA_{rolling_window}"] = historical_prices["Close"].rolling(rolling_window).mean()
historical_prices[f"SMA_50"] = historical_prices["Close"].rolling(50).mean()
historical_prices[f"EMA_{rolling_window}"] = historical_prices["Close"].ewm(span=rolling_window, adjust=False).mean()
historical_prices[f"STD_{rolling_window}"] = historical_prices["Close"].rolling(rolling_window).std()
historical_prices[f"max_{rolling_window}"] = historical_prices["Close"].rolling(rolling_window).max()
historical_prices[f"min_{rolling_window}"] = historical_prices["Close"].rolling(rolling_window).min()

#gain and loss columns to calc RSI
price_change = historical_prices['Close'] - historical_prices['Close'].shift(1)
historical_prices["gain"] = price_change.clip(lower=0)
historical_prices["loss"] = (-price_change).clip(lower=0)

avg_gain = historical_prices["gain"].ewm(com=13, min_periods=14).mean()
avg_loss = historical_prices["loss"].ewm(com=13, min_periods=14).mean()
RS = avg_gain / avg_loss
historical_prices[f"RSI_14"] = 100 - (100 / (1 + RS))

#calc MACD
ema_12 = historical_prices["Close"].ewm(span=12, adjust=False).mean()
ema_26 = historical_prices["Close"].ewm(span=26, adjust=False).mean()

historical_prices["MACD"] = ema_12 - ema_26
historical_prices["MACD_Signal"] = historical_prices["MACD"].ewm(span=9, adjust=False).mean()
historical_prices["MACD_Histogram"] = historical_prices["MACD"] - historical_prices["MACD_Signal"]

#calc ATR - add a column of true range & take a mean of over 14 days
historical_prices["prev_close"] = historical_prices["Close"].shift(1)

historical_prices["TR"] = historical_prices[["High", "Low", "prev_close"]].apply(
    lambda row: max(
        row["High"] - row["Low"],
        abs(row["High"] - row["prev_close"]),
        abs(row["Low"] - row["prev_close"])
    ),
    axis=1
)

historical_prices["ATR_14"] = historical_prices["TR"].ewm(com=13, adjust=False).mean()

#vwap
typical_price = (historical_prices["High"] + historical_prices["Low"] + historical_prices["Close"]) / 3
historical_prices["vwap"] = (historical_prices["Volume"] * typical_price).cumsum() / (historical_prices["Volume"]).cumsum()

#future return
historical_prices["future_return_5d"] = (historical_prices["Close"].shift(-5) - historical_prices["Close"]) / historical_prices["Close"] * 100
historical_prices["future_5d_label"] = np.where(historical_prices["future_return_5d"] > 0, 1, 0)

historical_prices.drop(columns=["prev_close", "gain", "loss", "TR"], inplace=True)
historical_prices.to_csv(f"analyzed_{asset}_data.csv")