import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from engine.downloader import Downloader
from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class MotoAmericaPlugin(BasePlugin):

    # ---------------------------------------------------------
    # OFFICIAL MOTOAMERICA SOURCES
    # ---------------------------------------------------------

    # Standalone document embedded by the public calendar page.
    #
    # Contains the complete MotoAmerica season calendar.

    SEASON_CALENDAR_URL = (
        "https://www.motoamerica.com/"
        "wp-content/Calendar/"
    )

    # Shared MotoAmerica event schedule page.
    #
    # When a detailed race schedule is published, the current
    # schedule appears here as Elementor tabs.

    SCHEDULE_URL = (
        "https://www.motoamerica.com/event/"
    )

    # MotoAmerica explicitly labels the published schedule
    # times as Pacific Time.

    SOURCE_TIMEZONE = ZoneInfo(
        "America/Los_Angeles"
    )

    def __init__(self):

        self.downloader = Downloader()

    # ---------------------------------------------------------
    # PLUGIN METADATA
    # ---------------------------------------------------------

    @property
    def name(self):

        return "MotoAmerica"

    @property
    def filename(self):

        return "motoamerica.ics"

    # ---------------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------------

    @staticmethod
    def clean_text(value):

        if not value:
            return ""

        return " ".join(
            value
            .replace("\xa0", " ")
            .split()
        )

    # ---------------------------------------------------------
    # DOWNLOAD HTML
    # ---------------------------------------------------------

    def download_html(
        self,
        url,
    ):

        return self.downloader.get_text(
            url
        )

    # ---------------------------------------------------------
    # GET EVENT SLUG
    # ---------------------------------------------------------

    @staticmethod
    def get_event_slug(event_url):

        return (
            event_url
            .rstrip("/")
            .split("/")[-1]
            .lower()
        )

    # ---------------------------------------------------------
    # PARSE SEASON DATE RANGE
    # ---------------------------------------------------------

    @classmethod
    def parse_date_range(
        cls,
        date_text,
        year,
    ):

        """
        Supported examples:

        March 5 - 7

        April 17 - 19

        July 10 - 12

        July 31 - August 2
        """

        date_text = cls.clean_text(
            date_text
        )

        date_text = (
            date_text
            .replace("–", "-")
            .replace("—", "-")
        )

        # -----------------------------------------------------
        # CROSS-MONTH RANGE
        #
        # Example:
        #
        # July 31 - August 2
        # -----------------------------------------------------

        cross_month_match = re.match(
            r"^([A-Za-z]+)\s+"
            r"(\d{1,2})\s*-\s*"
            r"([A-Za-z]+)\s+"
            r"(\d{1,2})$",
            date_text,
        )

        if cross_month_match:

            start_month = (
                cross_month_match.group(1)
            )

            start_day = int(
                cross_month_match.group(2)
            )

            end_month = (
                cross_month_match.group(3)
            )

            end_day = int(
                cross_month_match.group(4)
            )

            try:

                start_date = datetime.strptime(
                    f"{start_month} "
                    f"{start_day} "
                    f"{year}",
                    "%B %d %Y",
                ).date()

                end_date = datetime.strptime(
                    f"{end_month} "
                    f"{end_day} "
                    f"{year}",
                    "%B %d %Y",
                ).date()

            except ValueError:

                return None, None

            return start_date, end_date

        # -----------------------------------------------------
        # SAME-MONTH RANGE
        #
        # Example:
        #
        # July 10 - 12
        # -----------------------------------------------------

        same_month_match = re.match(
            r"^([A-Za-z]+)\s+"
            r"(\d{1,2})\s*-\s*"
            r"(\d{1,2})$",
            date_text,
        )

        if not same_month_match:

            return None, None

        month_name = (
            same_month_match.group(1)
        )

        start_day = int(
            same_month_match.group(2)
        )

        end_day = int(
            same_month_match.group(3)
        )

        try:

            start_date = datetime.strptime(
                f"{month_name} "
                f"{start_day} "
                f"{year}",
                "%B %d %Y",
            ).date()

            end_date = datetime.strptime(
                f"{month_name} "
                f"{end_day} "
                f"{year}",
                "%B %d %Y",
            ).date()

        except ValueError:

            return None, None

        return start_date, end_date

    # ---------------------------------------------------------
    # DOWNLOAD COMPLETE SEASON CALENDAR
    # ---------------------------------------------------------

    def download_season_events(self):

        print(
            "Downloading MotoAmerica "
            "season calendar..."
        )

        html = self.download_html(
            self.SEASON_CALENDAR_URL
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        articles = soup.select(
            "article.event-article"
        )

        print(
            f"Found {len(articles)} "
            f"MotoAmerica event cards"
        )

        season_events = []

        current_year = datetime.now().year

        for article in articles:

            date_element = article.select_one(
                "span.start-date"
            )

            venue_element = article.select_one(
                "div.event-loc-place"
            )

            title_element = article.select_one(
                "div.event-content "
                "h4.event-title "
                "a.heading"
            )

            if not all([
                date_element,
                venue_element,
                title_element,
            ]):

                continue

            date_text = self.clean_text(
                date_element.get_text()
            )

            venue = self.clean_text(
                venue_element.get_text()
            )

            event_title = self.clean_text(
                title_element.get_text()
            )

            event_url = title_element.get(
                "href",
                "",
            )

            if not event_url:

                continue

            event_url = urljoin(
                self.SEASON_CALENDAR_URL,
                event_url,
            )

            start_date, end_date = (
                self.parse_date_range(
                    date_text,
                    current_year,
                )
            )

            if (
                not start_date
                or not end_date
            ):

                print(
                    "Skipping MotoAmerica event "
                    "with unknown date:",
                    event_title,
                    date_text,
                )

                continue

            season_events.append({

                "title": event_title,

                "venue": venue,

                "url": event_url,

                "slug": self.get_event_slug(
                    event_url
                ),

                "start_date": start_date,

                "end_date": end_date,

            })

        print(
            f"Parsed {len(season_events)} "
            f"MotoAmerica season events"
        )

        return season_events

    # ---------------------------------------------------------
    # NORMALIZE CLASS NAME
    # ---------------------------------------------------------

    @classmethod
    def normalize_class_name(
        cls,
        class_name,
    ):

        class_name = cls.clean_text(
            class_name
        )

        lower_name = class_name.lower()

        # Order matters.

        if "super hooligan" in lower_name:

            return "Super Hooligan"

        if "king of the baggers" in lower_name:

            return "King of the Baggers"

        if "talent cup" in lower_name:

            return "Talent Cup"

        if "supersport" in lower_name:

            return "Supersport"

        if "superbike" in lower_name:

            return "Superbike"

        return class_name
    
    # ---------------------------------------------------------
    # PARSE SCHEDULE TAB DATE
    # ---------------------------------------------------------

    @classmethod
    def parse_schedule_tab_date(
        cls,
        tab_text,
        year,
    ):

        """
        Example:

        Laguna Seca, 7/10
        Laguna Seca, 7/11
        Laguna Seca, 7/12
        """

        tab_text = cls.clean_text(
            tab_text
        )

        match = re.search(
            r",\s*"
            r"(\d{1,2})/"
            r"(\d{1,2})\s*$",
            tab_text,
        )

        if not match:

            return None

        month = int(
            match.group(1)
        )

        day = int(
            match.group(2)
        )

        try:

            return datetime(
                year,
                month,
                day,
            ).date()

        except ValueError:

            return None

    # ---------------------------------------------------------
    # PARSE SCHEDULE LINE
    # ---------------------------------------------------------

    @classmethod
    def parse_schedule_line(
        cls,
        line_text,
    ):

        """
        Example:

        1:10 PM – Supersport – Race 1 (17 laps)

        Returns:

        {
            "time_text": "1:10 PM",
            "class_name": "Supersport",
            "session_name": "Race 1",
            "full_text": "...",
        }
        """

        line_text = cls.clean_text(
            line_text
        )

        line_text = (
            line_text
            .replace("—", "–")
        )

        parts = re.split(
            r"\s+[–-]\s+",
            line_text,
            maxsplit=2,
        )

        if len(parts) < 3:

            return None

        time_text = cls.clean_text(
            parts[0]
        )

        class_name = cls.clean_text(
            parts[1]
        )

        session_name = cls.clean_text(
            parts[2]
        )

        # Confirm that the first field is a clock time.

        try:

            datetime.strptime(
                time_text,
                "%I:%M %p",
            )

        except ValueError:

            return None

        return {

            "time_text": time_text,

            "class_name": (
                cls.normalize_class_name(
                    class_name
                )
            ),

            "session_name": session_name,

            "full_text": line_text,

        }

    # ---------------------------------------------------------
    # DOWNLOAD SHARED PUBLISHED SCHEDULE
    # ---------------------------------------------------------

    def download_published_schedule(self):

        print(
            "Downloading MotoAmerica "
            "published schedule..."
        )

        html = self.download_html(
            self.SCHEDULE_URL
        )

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        tab_widgets = soup.select(
            "div.elementor-tabs"
        )

        print(
            f"Found {len(tab_widgets)} "
            f"MotoAmerica schedule widgets"
        )

        if not tab_widgets:

            return None

        current_year = datetime.now().year

        schedule_days = []

        # Usually only one schedule widget is published,
        # but parse all widgets if MotoAmerica changes this.

        for widget in tab_widgets:

            desktop_tabs = widget.select(
                "div.elementor-tabs-wrapper "
                "div.elementor-tab-desktop-title"
            )

            for tab_title in desktop_tabs:

                tab_number = tab_title.get(
                    "data-tab"
                )

                if not tab_number:

                    continue

                schedule_date = (
                    self.parse_schedule_tab_date(
                        tab_title.get_text(),
                        current_year,
                    )
                )

                if not schedule_date:

                    continue

                content = widget.select_one(
                    "div.elementor-tabs-content-wrapper "
                    f'div.elementor-tab-content'
                    f'[data-tab="{tab_number}"]'
                )

                if not content:

                    continue

                sessions = []

                # Each actual schedule entry is stored
                # as a div inside the tab content.

                for line_element in content.select(
                    "div"
                ):

                    # Ignore container divs that contain
                    # other div elements.

                    if line_element.find(
                        "div",
                        recursive=False,
                    ):

                        continue

                    session = self.parse_schedule_line(
                        line_element.get_text(
                            " ",
                            strip=True,
                        )
                    )

                    if session:

                        sessions.append(
                            session
                        )

                schedule_days.append({

                    "date": schedule_date,

                    "tab_title": self.clean_text(
                        tab_title.get_text()
                    ),

                    "sessions": sessions,

                })

        if not schedule_days:

            print(
                "No usable MotoAmerica "
                "schedule days found"
            )

            return None

        schedule_days.sort(
            key=lambda item: item["date"]
        )

        print(
            f"Parsed {len(schedule_days)} "
            f"MotoAmerica schedule days"
        )

        for day in schedule_days:

            print(
                "  ",
                day["date"],
                day["tab_title"],
                f"({len(day['sessions'])} sessions)",
            )

        return {

            "start_date": (
                schedule_days[0]["date"]
            ),

            "end_date": (
                schedule_days[-1]["date"]
            ),

            "days": schedule_days,

        }

    # ---------------------------------------------------------
    # MATCH PUBLISHED SCHEDULE TO SEASON EVENT
    # ---------------------------------------------------------

    @staticmethod
    def match_schedule_to_event(
        published_schedule,
        season_events,
    ):

        if not published_schedule:

            return None

        schedule_start = (
            published_schedule["start_date"]
        )

        schedule_end = (
            published_schedule["end_date"]
        )

        # Primary match:
        #
        # The schedule dates must fall within the
        # official season event date range.

        for season_event in season_events:

            if (
                season_event["start_date"]
                <= schedule_start
                <= season_event["end_date"]
                and
                season_event["start_date"]
                <= schedule_end
                <= season_event["end_date"]
            ):

                return season_event

        return None

    # ---------------------------------------------------------
    # DISCOVER CLASSES RACING
    # ---------------------------------------------------------

    @classmethod
    def discover_classes(
        cls,
        published_schedule,
    ):

        classes = []

        seen = set()

        if not published_schedule:

            return classes

        for day in published_schedule["days"]:

            for session in day["sessions"]:

                class_name = session[
                    "class_name"
                ]

                # Ignore non-racing promotional
                # activities and miscellaneous items.

                known_classes = {

                    "Superbike",

                    "Supersport",

                    "King of the Baggers",

                    "Super Hooligan",

                    "Talent Cup",

                }

                if (
                    class_name in known_classes
                    and class_name not in seen
                ):

                    seen.add(
                        class_name
                    )

                    classes.append(
                        class_name
                    )

        return classes

    # ---------------------------------------------------------
    # BUILD PLACEHOLDER DESCRIPTION
    # ---------------------------------------------------------

    @staticmethod
    def build_placeholder_description(
        season_event,
        classes=None,
    ):

        lines = [
            "MotoAmerica Race Weekend",
        ]

        if classes:

            lines.extend([
                "",
                "Classes Racing:",
            ])

            for class_name in classes:

                lines.append(
                    f"• {class_name}"
                )

        lines.extend([
            "",
            "Official Event Page:",
            season_event["url"],
        ])

        return "\n".join(
            lines
        )

    # ---------------------------------------------------------
    # DETERMINE IF SESSION IS A WANTED RACE
    # ---------------------------------------------------------

    @staticmethod
    def is_wanted_race(
        session,
    ):

        class_name = session[
            "class_name"
        ]

        session_name = session[
            "session_name"
        ].lower()

        if class_name not in {
            "Superbike",
            "Supersport",
        }:

            return False

        return bool(
            re.search(
                r"\brace\s+\d+\b",
                session_name,
            )
        )

    # ---------------------------------------------------------
    # EXTRACT RACE NUMBER
    # ---------------------------------------------------------

    @staticmethod
    def get_race_number(
        session_name,
    ):

        match = re.search(
            r"\brace\s+(\d+)\b",
            session_name,
            flags=re.IGNORECASE,
        )

        if not match:

            return None

        return int(
            match.group(1)
        )
    
    # ---------------------------------------------------------
    # CREATE UTC DATETIME FROM PACIFIC SCHEDULE TIME
    # ---------------------------------------------------------

    @classmethod
    def create_race_datetime(
        cls,
        race_date,
        time_text,
    ):

        parsed_time = datetime.strptime(
            time_text,
            "%I:%M %p",
        ).time()

        local_datetime = datetime.combine(
            race_date,
            parsed_time,
            tzinfo=cls.SOURCE_TIMEZONE,
        )

        return local_datetime.astimezone(
            timezone.utc
        )

    # ---------------------------------------------------------
    # CREATE PLACEHOLDER EVENT
    # ---------------------------------------------------------

    @classmethod
    def create_placeholder_event(
        cls,
        season_event,
        classes=None,
    ):

        # Use Python date objects for true all-day
        # iCalendar events.
        #
        # CalendarWriter passes these directly to
        # icalendar.Event, which will generate:
        #
        # DTSTART;VALUE=DATE:YYYYMMDD
        # DTEND;VALUE=DATE:YYYYMMDD
        #
        # DTEND is exclusive, so add one day to
        # the official final date.

        start_date = (
            season_event["start_date"]
        )

        end_date_exclusive = (
            season_event["end_date"]
            + timedelta(days=1)
        )

        description = (
            cls.build_placeholder_description(
                season_event,
                classes,
            )
        )

        return SportEvent(
            title=(
                "🏍️ MotoAmerica Race Weekend\n"
                f"{season_event['title']}"
            ),
            start=start_date,
            end=end_date_exclusive,
            venue=season_event["venue"],
            description=description,
        )

    # ---------------------------------------------------------
    # CREATE DETAILED RACE EVENTS
    # ---------------------------------------------------------

    @classmethod
    def create_detailed_race_events(
        cls,
        published_schedule,
        season_event,
    ):

        events = []

        for day in published_schedule["days"]:

            race_date = day["date"]

            for session in day["sessions"]:

                if not cls.is_wanted_race(
                    session
                ):

                    continue

                start_datetime = (
                    cls.create_race_datetime(
                        race_date,
                        session["time_text"],
                    )
                )

                # The official schedule provides race laps
                # rather than a reliable race duration.
                #
                # Use a 1-hour calendar block.

                end_datetime = (
                    start_datetime
                    + timedelta(hours=1)
                )

                class_name = session[
                    "class_name"
                ]

                race_number = (
                    cls.get_race_number(
                        session["session_name"]
                    )
                )

                if race_number:

                    title = (
                        "🏍️ MotoAmerica "
                        f"{class_name} "
                        f"Race {race_number}"
                    )

                else:

                    title = (
                        "🏍️ MotoAmerica "
                        f"{class_name} Race"
                    )

                description_lines = [

                    season_event["title"],

                    "",

                    "Official Schedule Entry:",

                    session["full_text"],

                    "",

                    "Official Event Page:",

                    season_event["url"],

                    "",

                    "Official MotoAmerica Schedule:",

                    cls.SCHEDULE_URL,

                ]

                events.append(
                    SportEvent(
                        title=title,
                        start=start_datetime,
                        end=end_datetime,
                        venue=season_event["venue"],
                        description="\n".join(
                            description_lines
                        ),
                    )
                )

        return events

    # ---------------------------------------------------------
    # GET EVENTS
    # ---------------------------------------------------------

    def get_events(self):

        print(
            "Downloading MotoAmerica fixtures..."
        )

        # -----------------------------------------------------
        # 1. DOWNLOAD COMPLETE OFFICIAL SEASON CALENDAR
        # -----------------------------------------------------

        season_events = (
            self.download_season_events()
        )

        if not season_events:

            print(
                "No MotoAmerica season events found"
            )

            return []

        # -----------------------------------------------------
        # 2. DOWNLOAD CURRENTLY PUBLISHED DETAILED SCHEDULE
        #
        # The shared schedule page is downloaded once.
        # -----------------------------------------------------

        published_schedule = (
            self.download_published_schedule()
        )

        # -----------------------------------------------------
        # 3. MATCH PUBLISHED SCHEDULE TO OFFICIAL WEEKEND
        # -----------------------------------------------------

        matched_event = (
            self.match_schedule_to_event(
                published_schedule,
                season_events,
            )
        )

        if (
            published_schedule
            and matched_event
        ):

            print(
                "Matched published schedule to:",
                matched_event["title"],
            )

        elif published_schedule:

            print(
                "Published MotoAmerica schedule "
                "did not match a season event"
            )

        else:

            print(
                "No detailed MotoAmerica "
                "schedule currently published"
            )

        # -----------------------------------------------------
        # 4. DISCOVER CLASSES FOR THE MATCHED WEEKEND
        # -----------------------------------------------------

        classes = []

        if matched_event:

            classes = self.discover_classes(
                published_schedule
            )

            print(
                "Classes racing:",
                ", ".join(classes)
                if classes
                else "None found",
            )

        # -----------------------------------------------------
        # 5. CREATE ALL SEASON PLACEHOLDERS
        #
        # The matched weekend is enriched with classes.
        # All other weekends remain basic placeholders.
        # -----------------------------------------------------

        events = []

        for season_event in season_events:

            event_classes = None

            if (
                matched_event
                and season_event["url"]
                == matched_event["url"]
            ):

                event_classes = classes

            events.append(
                self.create_placeholder_event(
                    season_event,
                    event_classes,
                )
            )

        # -----------------------------------------------------
        # 6. ADD SUPERBIKE AND SUPERSPORT RACE EVENTS
        #
        # The weekend placeholder remains in the calendar.
        # Detailed race events are added alongside it.
        # -----------------------------------------------------

        if matched_event:

            detailed_events = (
                self.create_detailed_race_events(
                    published_schedule,
                    matched_event,
                )
            )

            events.extend(
                detailed_events
            )

            print(
                f"Added {len(detailed_events)} "
                f"detailed MotoAmerica race events"
            )

        # -----------------------------------------------------
        # 7. COMPLETE
        # -----------------------------------------------------

        print(
            f"Generated {len(events)} "
            f"MotoAmerica events"
        )

        return events