from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from engine.downloader import Downloader
from engine.event import SportEvent
from engine.html_utils import HtmlUtils
from plugins.base_plugin import BasePlugin


class ProteasPlugin(BasePlugin):

    URL = (
        "https://cricket.co.za/"
        "the-proteas/the-proteas-men/"
    )

    MATCH_DURATION = {

        "TEST": timedelta(days=5),

        "ODI": timedelta(hours=8),

        "T20": timedelta(hours=4),

        "T20I": timedelta(hours=4),

        "T10": timedelta(hours=3)

    }

    KNOWN_TEAMS = [

        "Australia",
        "Bangladesh",
        "England",
        "India",
        "New Zealand",
        "Pakistan",
        "Sri Lanka",
        "West Indies",
        "Zimbabwe",
        "Ireland",
        "Afghanistan"

    ]

    def __init__(self):

        self.downloader = Downloader()

    @property
    def name(self):

        return "Proteas"

    @property
    def filename(self):

        return "proteas.ics"

    def download_page(
        self,
        url
    ):

        return self.downloader.get_text(
            url
        )

    def find_match_links(self):

        print(
            "Downloading Proteas fixtures..."
        )

        html = self.download_page(
            self.URL
        )

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        links = []

        for a in soup.find_all(
            "a",
            href=True
        ):

            href = a.get(
                "href",
                ""
            )

            if (
                "/upcoming-match/"
                not in href
            ):
                continue

            if href not in links:

                links.append(
                    href
                )

        print(
            f"Found {len(links)} fixtures"
        )

        return links

    def get_opponent(
        self,
        series
    ):

        lower = series.lower()

        for team in self.KNOWN_TEAMS:

            if team.lower() in lower:

                return team

        return "Unknown"

    def get_match_type(
    self,
    series
):
        series = (
            series
            .replace("–", "-")
            .replace("—", "-")
        )

        # Australia Tour to South Africa - 2nd ODI
        if "-" in series:
            return series.split("-", 1)[1].strip()

        # Bangladesh Men's 1st Test
        words = series.split()
        for i, word in enumerate(words):
            if word.lower() in ("test", "odi", "t20", "t20i"):
                if i > 0:
                    previous = words[i - 1]
                    if any(previous.endswith(x) for x in ("st", "nd", "rd", "th")):
                        return previous + " " + word
                return word

        return series

    def get_duration(
        self,
        match_type
    ):

        upper = (
            match_type.upper()
        )

        for key in self.MATCH_DURATION:

            if key in upper:

                return (
                    self.MATCH_DURATION[
                        key
                    ]
                )

        return timedelta(
            hours=8
        )
    
    def parse_match(
        self,
        url
    ):

        html = self.download_page(
            url
        )

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        #
        # Read the labelled fields
        #

        fields = HtmlUtils.get_labeled_fields(
            soup
        )
        
        series = fields.get(
            "Series",
            ""
        )

        venue = fields.get(
            "Venue",
            ""
        )

        date = fields.get(
            "Date",
            ""
        )

        time = fields.get(
            "Time",
            ""
        )

        #
        # Skip incomplete pages
        #

        if (
            not series
            or not venue
            or not date
            or not time
        ):

            print(
                "  Skipping incomplete page."
            )

            return None

        #
        # Determine opponent
        #

        opponent = self.get_opponent(
            series
        )

        #
        # Determine match type
        #

        match_type = self.get_match_type(
            series
        )

        #
        # Handle series that don't contain
        # the match type after a dash
        #

        if (
            match_type
            == series
        ):

            upper = series.upper()

            if "TEST" in upper:

                index = upper.find(
                    "TEST"
                )

                start = index

                while (
                    start > 0
                    and series[
                        start - 1
                    ].isdigit()
                ):
                    start -= 1

                match_type = (
                    series[start:]
                    .strip()
                )

            elif "ODI" in upper:

                index = upper.find(
                    "ODI"
                )

                start = index

                while (
                    start > 0
                    and series[
                        start - 1
                    ].isdigit()
                ):
                    start -= 1

                match_type = (
                    series[start:]
                    .strip()
                )

            elif "T20" in upper:

                index = upper.find(
                    "T20"
                )

                start = index

                while (
                    start > 0
                    and series[
                        start - 1
                    ].isdigit()
                ):
                    start -= 1

                match_type = (
                    series[start:]
                    .strip()
                )

        #
        # Build datetime
        #

        try:

            start = datetime.strptime(

                f"{date} {time}",

                "%d/%m/%y %H:%M"

            )

        except Exception:

            print(
                "  Invalid date/time."
            )

            return None

        end = (

            start +

            self.get_duration(
                match_type
            )

        )

        #
        # Calendar title
        #

        title = "\n".join([

            "🏏 Proteas",

            f"South Africa vs {opponent}",

            match_type

        ])

        #
        # Description
        #

        description = "\n".join([

            "Proteas",

            "",

            f"Series: {series}",

            f"Venue: {venue}",

            f"Date: {date}",

            f"Time: {time}"

        ])

        return SportEvent(

            title=title,

            start=start,

            end=end,

            venue=venue,

            description=description

        )

    def parse(self):

        events = []

        links = self.find_match_links()

        #
        # Track processed URLs
        #

        processed_urls = set()

        #
        # Track duplicate events
        #

        seen_events = {}

        for link in links:

            if link in processed_urls:
                continue

            processed_urls.add(
                link
            )

            try:

                event = self.parse_match(
                    link
                )

                if event is None:
                    continue

                #
                # Remove duplicates
                #

                key = (
                    event.title,
                    event.venue
                )

                existing = seen_events.get(key)

                if existing is None:

                    seen_events[key] = event

                elif event.start < existing.start:

                    seen_events[key] = event

            except Exception as ex:

                print(
                    f"Failed loading {link}"
                )

                print(
                    ex
                )

        # Rebuild events list from seen events and sort
        events = list(seen_events.values())
        events.sort(key=lambda e: e.start)

        print(

            f"Generated {len(events)} Proteas events"

        )

        return events

    def get_events(self):

        return self.parse()        