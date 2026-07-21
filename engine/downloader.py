import requests


class Downloader:

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def get_json(self, url, headers=None):
        request_headers = dict(self.HEADERS)

        if headers:
            request_headers.update(headers)

        response = requests.get(
            url,
            headers=request_headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_text(self, url):
        response = requests.get(
            url,
            headers=self.HEADERS,
            timeout=30,
        )

        response.raise_for_status()

        return response.text