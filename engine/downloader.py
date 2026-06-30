import requests


class Downloader:

    def get_json(self, url):

        print(f"Downloading JSON: {url}")

        response = requests.get(url, timeout=30)

        response.raise_for_status()

        return response.json()

    def get_text(self, url):

        print(f"Downloading Text: {url}")

        response = requests.get(url, timeout=30)

        response.raise_for_status()

        return response.text

    def download_file(self, url):

        print(f"Downloading File: {url}")

        response = requests.get(url, timeout=30)

        response.raise_for_status()

        return response.content