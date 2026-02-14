import math
from collections import Counter


def calc_mean(nums: list[int]) -> float | int:
    return sum(nums) / len(nums)

def calc_median(nums: list[int]) -> float | int:
    nums = sorted(nums)
    if len(nums) % 2 == 1:
        return nums[int(len(nums) // 2)]
    else:
        dec_index = len(nums) // 2
        num1, num2 = nums[dec_index], nums[dec_index - 1]
        return (num1 + num2)/2

def calc_mode(nums: list[int]):
    count = Counter(nums)
    max_freq = max(count.values())

    if max_freq == 1:
        return "No Mode"

    # Otherwise return all numbers with max frequency
    return [num for num, freq in count.items() if freq == max_freq]


#returns sample and population respectively
def calc_variance_popln(nums: list[int]) -> float:
    n =len(nums)
    if n < 4:
        raise ValueError("Variance requires at least 2 data points.")

    mean = calc_mean(nums)
    nums = [(f-mean) ** 2 for f in nums]
    return sum(nums) / n

def calc_variance_sample(nums: list[int]) -> float:
    mean = calc_mean(nums)
    nums = [(f-mean) ** 2 for f in nums]
    return sum(nums) / (len(nums) - 1)

def calc_standard_deviation(variance) -> float:
    return math.sqrt(variance)

def calc_z_score(nums: list[int]) -> list[float]:
    mean = calc_mean(nums)
    standard_deviation = calc_standard_deviation(calc_variance_popln(nums))
    z_scores = [(num - mean) / standard_deviation for num in nums]
    return z_scores


def find_upper_and_lower_half(nums: list[int]) -> tuple[list[int], list[int]]:
    n = len(nums)

    if n % 2 == 1:
        # odd length → exclude the median element
        mid = n // 2
        lower_half = nums[:mid]
        upper_half = nums[mid + 1:]
    else:
        # even length → split exactly in half
        mid = n // 2
        lower_half = nums[:mid]
        upper_half = nums[mid:]

    return lower_half, upper_half

#returns q1, q3, IQR
def calc_quartiles(nums: list[int]) -> tuple[float, float, float]:
    nums = sorted(nums)
    lower_half, upper_half = find_upper_and_lower_half(nums)

    q1 = calc_median(lower_half)
    q3 = calc_median(upper_half)

    return q1, q3, q3 - q1

def calc_skewness(nums: list[int]) -> float:
    l = len(nums)

    if l < 3:
        raise ValueError("Skewness requires at least 3 data points.")

    mean = calc_mean(nums)
    standard_deviation = calc_standard_deviation(calc_variance_sample(nums))

    if standard_deviation == 0:
        return 0.0

    #list of the sum of the (datapoint - mean/standard)
    average_deviation = [((n - mean)/ standard_deviation) ** 3 for n in nums]

    # Adjusted Fisher–Pearson Standardized Moment Coefficient Formula
    return sum(average_deviation) * (l/ ((l-1) * (l-2)))

def calc_kurtosis(nums: list[int]) -> float:
    n = len(nums)

    if n < 4:
        raise ValueError("Kurtosis requires at least 4 data points.")

    mean = calc_mean(nums)
    standard_deviation = calc_standard_deviation(calc_variance_sample(nums))

    if standard_deviation == 0:
        return 0.0

    #sum of (point - mean / standard deviation) ^ 4
    average_deviation = sum(((n - mean)/standard_deviation) ** 4 for n in nums)

    #Excess Kurtosis Formula
    return ((n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))) * average_deviation - ((3 * (n-1)**2)/((n - 2) * (n - 3)))


def parse_numbers(raw: str) -> list[int]:
    cleaned = []
    for token in raw.replace(",", " ").split():
        try:
            cleaned.append(float(token) if "." in token else int(token))
        except ValueError:
            print(f"Warning: '{token}' is not a number and was ignored.")
    return cleaned


def print_stats(nums: list[int]):
    mean = calc_mean(nums)
    median = calc_median(nums)
    mode = calc_mode(nums)
    var_pop = calc_variance_popln(nums)
    var_sample = calc_variance_sample(nums)
    sd = calc_standard_deviation(var_sample)
    z_scores = calc_z_score(nums)
    q1, q3, iqr = calc_quartiles(nums)
    skew = calc_skewness(nums)
    kurt = calc_kurtosis(nums)

    print("\n=== Statistical Profile ===")
    print(f"{'Count:':25} {len(nums)}")
    print(f"{'Mean:':25} {mean}")
    print(f"{'Median:':25} {median}")
    print(f"{'Mode:':25} {mode}")
    print(f"{'Population Variance:':25} {var_pop}")
    print(f"{'Sample Variance:':25} {var_sample}")
    print(f"{'Std Deviation:':25} {sd}")
    print(f"{'Q1:':25} {q1}")
    print(f"{'Q3:':25} {q3}")
    print(f"{'IQR:':25} {iqr}")
    print(f"{'Skewness:':25} {skew}")
    print(f"{'Kurtosis:':25} {kurt}")
    print(f"{'Z-Scores:':25} {z_scores}")
    print("===========================\n")

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

def main_menu():
    print("=== Statistical Analysis CLI ===")

    while True:
        print("\nChoose an option:")
        print("1. Enter numbers manually")
        print("2. Load numbers from a file (.txt or .csv)")
        print("q. Quit")

        choice = input("> ").strip().lower()

        if choice == "q":
            print("Exiting. Goodbye.")
            break

        # Manual input
        if choice == "1":
            raw = input("\nEnter numbers (space or comma separated):\n> ")
            nums = parse_numbers(raw)

        # File input
        elif choice == "2":
            path = input("\nEnter file path:\n> ").strip()
            nums = load_numbers_from_file(path)

        else:
            print("Invalid selection. Try again.")
            continue

        # Validate numbers
        if len(nums) == 0:
            print("No valid numbers found. Try again.")
            continue

        if len(nums) < 3:
            print("At least 3 numbers are required for full statistical analysis.")
            continue

        print_stats(nums)

if __name__ == "__main__":
    main_menu()

