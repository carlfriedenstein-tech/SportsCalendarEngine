from playwright.sync_api import sync_playwright


class Browser:

    def get_html(self, url):

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(url, wait_until="networkidle")

            html = page.content()

            browser.close()

            with open("output/fifa_page.html", "w", encoding="utf-8") as f:
                f.write(html)

            return html