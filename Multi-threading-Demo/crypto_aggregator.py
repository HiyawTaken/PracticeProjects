import requests
import time
import concurrent.futures

sequential_time=0
parallel_time=0

def req_coinbase():
    coinbase_btc_data = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot")
    if coinbase_btc_data.status_code == 200:
        return float(coinbase_btc_data.json()['data']['amount'])
    else:
        return f"Coinbase BTC data request failed with error code: {coinbase_btc_data.status_code}"

def req_coingecko():
    coingecko_btc_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
    if coingecko_btc_data.status_code == 200:
        return float(coingecko_btc_data.json()['bitcoin']['usd'])
    else:
        return f"CoinGecko BTC data request failed with error code: {coingecko_btc_data.status_code}"

def req_bitstamp():
    bitstamp_btc_data = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd/")
    if bitstamp_btc_data.status_code == 200:
        return float(bitstamp_btc_data.json()['last'])
    else:
        return f"Bitstamp BTC data request failed with error code: {bitstamp_btc_data.status_code}"

def req_binance():
    binance_btc_data = requests.get("https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT")
    if binance_btc_data.status_code == 200:
        return float(binance_btc_data.json()['price'])
    else:
        return f"Binance BTC data request failed with error code: {binance_btc_data.status_code}"

def run_sequential():
    start = time.perf_counter()
    print(f"Coinbase: ${req_coinbase()}")
    print(f"CoinGecko: ${req_coingecko()}")
    print(f"Bitstamp: ${req_bitstamp()}")
    print(f"Binance: ${req_binance()}")
    end = time.perf_counter()
    global sequential_time
    sequential_time = end - start
    print(f"Sequential execution time: {(end - start):.2f} seconds")

def run_parallel():
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        f1 = executor.submit(req_coinbase)
        f2 = executor.submit(req_coingecko)
        f3 = executor.submit(req_bitstamp)
        f4 = executor.submit(req_binance)

        print(f"Coinbase: ${f1.result()}")
        print(f"CoinGecko: ${f2.result()}")
        print(f"Bitstamp: ${f3.result()}")
        print(f"Binance: ${f4.result()}")

    end = time.perf_counter()
    global parallel_time
    parallel_time = end - start
    print(f"Parallel execution time: {(end - start):.2f} seconds")

def main():
    print("--- Sequential Run ---")
    run_sequential()
    print("\n--- Parallel Run ---")
    run_parallel()

    print(f"\nSpeed Improvement: {(sequential_time/parallel_time * 100):.2f}%")

if __name__ == "__main__":
    main()


