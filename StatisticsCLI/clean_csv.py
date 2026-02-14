import csv

def extract_prices(input_file, output_file):
    prices = []

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header

        for row in reader:
            try:
                close_price = row[8]
                prices.append(close_price)
            except (IndexError, ValueError):
                continue  # skip malformed rows

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(",".join(prices))

    print(f"Extracted {len(prices)} prices → saved to {output_file}")

extract_prices("bitcoin_price.csv", "clean_prices.csv")
