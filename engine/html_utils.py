from bs4 import BeautifulSoup


class HtmlUtils:

    @staticmethod
    def get_labeled_fields(soup):

        """
        Reads Elementor-style label/value blocks.

        Example:

            Series
            Australia Tour to South Africa

        becomes

            {
                "Series": "...",
                "Venue": "...",
                ...
            }
        """

        fields = {}

        for container in soup.select("div.e-con-inner"):

            values = []

            for tag in container.find_all(
                ["p", "h1", "h2", "h3"]
            ):

                text = tag.get_text(
                    " ",
                    strip=True
                )

                if text:

                    values.append(text)

            VALID_LABELS = {
                "Series",
                "Venue",
                "Date",
                "Time"
            }

            if (
                len(values) == 2
                and values[0] in VALID_LABELS
            ):

                fields[values[0]] = values[1]

        return fields