import requests
import concurrent.futures


def fetch_status_code(url: str) -> int:
    try:
        status_data = requests.get(url)
        return status_data.status_code
    except requests.exceptions.RequestException as e:
        return 0

def monitor(url_list: list[str]) -> dict[str, int]:
    status = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {
            executor.submit(fetch_status_code, url): url
            for url in url_list
        }

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                status[url] = future.result()
            except Exception:
                status[url] = 0

    return status