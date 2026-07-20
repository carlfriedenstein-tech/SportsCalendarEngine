from abc import abstractmethod

from engine.cache_manager import CacheManager
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from engine.downloader import Downloader
from engine.event import SportEvent
from plugins.base_plugin import BasePlugin


class SnookerPlugin(BasePlugin):

    def __init__(self):

        self.downloader = Downloader()
        self.cache = CacheManager(
            "snooker"
    )

    # ---------------------------------------------------------
    # LOCAL TEST DATA
    # ---------------------------------------------------------

    PROJECT_ROOT = (
        Path(__file__).resolve().parent.parent
    )

    TEST_DATA_FOLDER = (
        PROJECT_ROOT
        / "tests"
        / "data"
        / "snooker"
    )

    EVENTS_FILE = (
        TEST_DATA_FOLDER
        / "events.json"
    )

    MATCHES_FILE = (
        TEST_DATA_FOLDER
        / "matches.json"
    )

    PLAYERS_FILE = (
        TEST_DATA_FOLDER
        / "players.json"
    )

    # ---------------------------------------------------------
    # CONFIGURATION
    # ---------------------------------------------------------

    # Tournament placeholders are controlled here.
    #
    # Matching is case-insensitive against both:
    #
    # Name
    # ShortName
    #
    # The current sample events do not contain the major
    # tournaments we eventually want, so this initial fixture
    # list intentionally selects the two sample events.
    #
    # Once live API access is connected, we will replace this
    # list with your actual major-tournament choices.

    PLACEHOLDER_TOURNAMENTS = [

        "Australian Goldfields Open Qualifiers",

        "World Cup, Group C",

    ]

    # Watched players are configured using verified
    # Snooker.org player IDs.
    #
    # This avoids ambiguous name matching.
    #
    # The readable name remains here so adding or removing
    # players is easy.

    WATCHED_PLAYERS = {

        1: "Mark Williams",

    }

    # Default duration used when a scheduled match does not
    # yet have a reliable EndDate.
    #
    # Snooker matches can vary substantially in length.
    # Three hours is only a calendar display block, not a
    # prediction of actual match duration.

    DEFAULT_MATCH_DURATION = timedelta(
        hours=3
    )

    # ---------------------------------------------------------
    # PLUGIN METADATA
    # ---------------------------------------------------------

    @property
    def name(self):

        return "Snooker"

    @property
    def filename(self):

        return "snooker.ics"

    # ---------------------------------------------------------
    # LOAD JSON FILE
    # ---------------------------------------------------------

    @staticmethod
    def load_json_file(
        file_path,
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        if not isinstance(
            data,
            list,
        ):

            raise ValueError(
                f"Expected JSON array in "
                f"{file_path}"
            )

        return data

    # ---------------------------------------------------------
    # GET EVENTS (CACHE OR DOWNLOAD)
    # ---------------------------------------------------------

    def download_events(self):

        cache_file = self.cache.events_file()

        if not self.cache.cache_expired(
            cache_file,
            timedelta(days=7),
        ):

            print(
                "Loading Snooker events from cache..."
            )

            events = self.cache.load_json(
                cache_file
            )

            print(
                f"Loaded {len(events)} "
                "Snooker events"
            )

            return events

        headers = {
            "X-Requested-By":
                "FriedensteiniCalendar353"
        }

        print(
            "Downloading Snooker season events..."
        )

        events = self.downloader.get_json(
            (
                "https://api.snooker.org/"
                "?t=5&s=2026&tr=main"
            ),
            headers=headers,
        )

        self.cache.save_json(
            cache_file,
            events,
        )

        print(
            f"Downloaded {len(events)} "
            "Snooker events"
        )

        return events
    
    # ---------------------------------------------------------
    # GET PLAYERS (CACHE OR DOWNLOAD)
    # ---------------------------------------------------------

    def download_players(self):

        cache_file = self.cache.players_file()

        if not self.cache.cache_expired(
            cache_file,
            timedelta(days=30),
        ):

            print(
                "Loading Snooker players from cache..."
            )

            players = self.cache.load_json(
                cache_file
            )

            print(
                f"Loaded {len(players)} "
                "Snooker players"
            )

            return players

        headers = {
            "X-Requested-By":
                "FriedensteiniCalendar353"
        }

        print(
            "Downloading Snooker players..."
        )

        players = self.downloader.get_json(
            "https://api.snooker.org/?t=10&st=p&s=2026",
            headers=headers,
        )

        self.cache.save_json(
            cache_file,
            players,
        )

        print(
            f"Downloaded {len(players)} "
            "Snooker players"
        )

        return players
    
    # ---------------------------------------------------------
    # LOAD WATCHED PLAYERS
    # ---------------------------------------------------------

    def load_watched_players(self):

        config_file = (
            Path(__file__).resolve().parent.parent
            / "config"
            / "snooker.json"
        )

        try:

            with open(
                config_file,
                "r",
                encoding="utf-8",
            ) as file:

                config = json.load(
                    file
                )

            return config.get(
                "watched_players",
                [],
            )

        except Exception as error:

            print(
                "Warning: Unable to load "
                f"watched players: {error}"
            )

            return []
    
    # ---------------------------------------------------------
    # GET MATCHES (CACHE OR DOWNLOAD)
    # ---------------------------------------------------------

    def download_matches(
        self,
        event,
    ):

        event_id = event["ID"]

        end_date = self.parse_api_date(
            event["EndDate"]
        )

        today = datetime.now().date()

        cache_file = self.cache.matches_file(
            event_id
        )

        # -----------------------------------------------------
        # COMPLETED TOURNAMENTS NEVER REFRESH
        # -----------------------------------------------------

        if (
            today > end_date
            and cache_file.exists()
        ):

            print(
                f"Loading archived Snooker matches "
                f"for event {event_id} "
                f"from cache..."
            )

            matches = self.cache.load_json(
                cache_file
            )

            print(
                f"Loaded {len(matches)} "
                "Snooker matches"
            )

            return matches

        # -----------------------------------------------------
        # UPCOMING / ACTIVE TOURNAMENTS
        # -----------------------------------------------------

        if not self.cache.cache_expired(
            cache_file,
            timedelta(hours=6),
        ):

            print(
                f"Loading Snooker matches "
                f"for event {event_id} "
                f"from cache..."
            )

            matches = self.cache.load_json(
                cache_file
            )

            print(
                f"Loaded {len(matches)} "
                "Snooker matches"
            )

            return matches

        headers = {
            "X-Requested-By":
                "FriedensteiniCalendar353"
        }

        print(
            f"Downloading matches "
            f"for event {event_id}..."
        )

        try:

            matches = self.downloader.get_json(
                (
                    "https://api.snooker.org/"
                    f"?t=6&e={event_id}"
                ),
                headers=headers,
            )

        except Exception as exc:

            print(
                f"Unable to download matches "
                f"for event {event_id}: {exc}"
            )

            if cache_file.exists():

                print(
                    "Using existing cache instead."
                )

                return self.cache.load_json(
                    cache_file
                )

            return []

        self.cache.save_json(
            cache_file,
            matches,
        )

        print(
            f"Downloaded {len(matches)} "
            "Snooker matches"
        )

        return matches
    
    # ---------------------------------------------------------
    # UPDATE MATCH CACHE
    # ---------------------------------------------------------

    def update_match_cache(
        self,
        tournaments,
    ):

        today = datetime.now().date()

        downloaded = False

        for event in tournaments:

            event_id = event["ID"]

            cache_file = self.cache.matches_file(
                event_id
            )

            end_date = self.parse_api_date(
                event["EndDate"]
            )

            print(
                "Checking cache:",
                self.clean_text(
                    event.get("Name")
                ),
            )

            # Completed tournaments never refresh.
            if (
                end_date
                and today > end_date
                and cache_file.exists()
            ):

                continue

            # Cache still fresh.
            if (
                cache_file.exists()
                and not self.cache.cache_expired(
                    cache_file,
                    timedelta(hours=6),
                )
            ):

                continue

            # Only ONE download per run.
            if downloaded:

                print(
                    "Skipping download."
                )

                continue

            self.download_matches(
                event
            )

            downloaded = True

    # ---------------------------------------------------------
    # LOAD CACHED MATCHES
    # ---------------------------------------------------------

    def load_cached_matches(
        self,
        tournaments,
    ):

        matches = []

        for event in tournaments:

            event_id = event["ID"]

            cache_file = self.cache.matches_file(
                event_id
            )

            if not cache_file.exists():

                continue

            event_matches = self.cache.load_json(
                cache_file
            )

            matches.extend(
                event_matches
            )

        return matches

    # ---------------------------------------------------------
    # LOAD LOCAL FIXTURES
    # ---------------------------------------------------------

    def load_events(self):

        events = self.load_json_file(
            self.EVENTS_FILE
        )

        print(
            f"Loaded {len(events)} "
            f"Snooker event fixtures"
        )

        return events

    def load_matches(self):

        matches = self.load_json_file(
            self.MATCHES_FILE
        )

        print(
            f"Loaded {len(matches)} "
            f"Snooker match fixtures"
        )

        return matches

    def load_players(self):

        players = self.load_json_file(
            self.PLAYERS_FILE
        )

        print(
            f"Loaded {len(players)} "
            f"Snooker player fixtures"
        )

        return players

    # ---------------------------------------------------------
    # CLEAN TEXT
    # ---------------------------------------------------------

    @staticmethod
    def clean_text(
        value,
    ):

        if value is None:

            return ""

        return " ".join(
            str(value)
            .replace("\xa0", " ")
            .split()
        )

    # ---------------------------------------------------------
    # PARSE API DATE
    # ---------------------------------------------------------

    @staticmethod
    def parse_api_date(
        value,
    ):

        if not value:

            return None

        try:

            return date.fromisoformat(
                value
            )

        except ValueError:

            return None

    # ---------------------------------------------------------
    # PARSE API DATETIME
    # ---------------------------------------------------------

    @staticmethod
    def parse_api_datetime(
        value,
    ):

        if not value:

            return None

        try:

            # Snooker.org timestamps use:
            #
            # 2015-07-29T14:00:00Z
            #
            # Replace Z with the explicit UTC offset so the
            # result is a timezone-aware datetime.

            parsed_datetime = (
                datetime.fromisoformat(
                    value.replace(
                        "Z",
                        "+00:00",
                    )
                )
            )

        except ValueError:

            return None

        if (
            parsed_datetime.tzinfo
            is None
        ):

            parsed_datetime = (
                parsed_datetime.replace(
                    tzinfo=timezone.utc
                )
            )

        return (
            parsed_datetime.astimezone(
                timezone.utc
            )
        )

    # ---------------------------------------------------------
    # BUILD PLAYER NAME
    # ---------------------------------------------------------

    @classmethod
    def build_player_name(
        cls,
        player,
    ):

        team_name = cls.clean_text(
            player.get("TeamName")
        )

        if team_name:

            return team_name

        first_name = cls.clean_text(
            player.get("FirstName")
        )

        middle_name = cls.clean_text(
            player.get("MiddleName")
        )

        last_name = cls.clean_text(
            player.get("LastName")
        )

        return " ".join(
            part
            for part in [
                first_name,
                middle_name,
                last_name,
            ]
            if part
        )

    # ---------------------------------------------------------
    # BUILD PLAYER LOOKUP
    # ---------------------------------------------------------

    @classmethod
    def build_player_lookup(
        cls,
        players,
    ):

        player_lookup = {}

        for player in players:

            player_id = player.get(
                "ID"
            )

            if player_id is None:

                continue

            player_lookup[player_id] = (
                cls.build_player_name(
                    player
                )
            )

        return player_lookup
    
    # ---------------------------------------------------------
    # LOAD WATCHED PLAYER IDS
    # ---------------------------------------------------------

    @classmethod
    def load_watched_player_ids(
        cls,
        player_lookup,
        watched_player_names,
    ):

        cls.WATCHED_PLAYERS = {}

        name_lookup = {

            name.casefold(): player_id

            for player_id, name in (
                player_lookup.items()
            )

        }

        for name in watched_player_names:

            player_id = name_lookup.get(
                name.casefold()
            )

            if player_id is None:

                print(
                    f"Warning: Watched player "
                    f"'{name}' not found."
                )

                continue

            cls.WATCHED_PLAYERS[
                player_id
            ] = player_lookup[
                player_id
            ]

    # ---------------------------------------------------------
    # CHECK IF MAIN TOUR EVENT
    # ---------------------------------------------------------

    @classmethod
    def is_main_tour_event(
        cls,
        event,
    ):

        event_name = cls.clean_text(
            event.get("Name")
        )

        if not event_name:

            return False

        excluded = [

            "Qualifiers",

            "Stage One Group",

            "Stage Two Group",

            "Stage Three Group",

            "Championship League - Group",

            "Winners Group",

        ]

        return not any(
            text in event_name
            for text in excluded
        )
    
    # ---------------------------------------------------------
    # VALIDATE TOURNAMENT
    # ---------------------------------------------------------

    @classmethod
    def validate_tournament(
        cls,
        event,
    ):

        event_id = event.get(
            "ID"
        )

        event_name = cls.clean_text(
            event.get("Name")
        )

        start_date = cls.parse_api_date(
            event.get("StartDate")
        )

        end_date = cls.parse_api_date(
            event.get("EndDate")
        )

        if event_id is None:

            return False

        if not event_name:

            return False

        if not start_date:

            return False

        if not end_date:

            return False

        if end_date < start_date:

            return False

        return True

    # ---------------------------------------------------------
    # BUILD TOURNAMENT LOCATION
    # ---------------------------------------------------------

    @classmethod
    def build_tournament_location(
        cls,
        event,
    ):

        venue = cls.clean_text(
            event.get("Venue")
        )

        city = cls.clean_text(
            event.get("City")
        )

        country = cls.clean_text(
            event.get("Country")
        )

        location_parts = []

        for value in [
            venue,
            city,
            country,
        ]:

            if (
                value
                and value.lower()
                != "unknown"
                and value not in location_parts
            ):

                location_parts.append(
                    value
                )

        return ", ".join(
            location_parts
        )

    # ---------------------------------------------------------
    # BUILD TOURNAMENT DESCRIPTION
    # ---------------------------------------------------------

    @classmethod
    def build_tournament_description(
        cls,
        event,
    ):

        lines = [
            "Snooker Tournament",
            "",
            f"Tournament: "
            f"{cls.clean_text(event.get('Name'))}",
        ]

        event_type = cls.clean_text(
            event.get("Type")
        )

        if event_type:

            lines.append(
                f"Type: {event_type}"
            )

        venue = cls.build_tournament_location(
            event
        )

        if venue:

            lines.append(
                f"Venue: {venue}"
            )

        tour = cls.clean_text(
            event.get("Tour")
        )

        if tour:

            lines.append(
                f"Tour: {tour}"
            )

        lines.extend([
            "",
            "Data Source:",
            "Snooker.org",
        ])

        return "\n".join(
            lines
        )

    # ---------------------------------------------------------
    # CREATE TOURNAMENT PLACEHOLDER
    # ---------------------------------------------------------

    @classmethod
    def create_tournament_placeholder(
        cls,
        event,
    ):

        start_date = cls.parse_api_date(
            event.get("StartDate")
        )

        end_date = cls.parse_api_date(
            event.get("EndDate")
        )

        # True all-day iCalendar event.
        #
        # DTEND is exclusive, so one day is added to
        # the official final tournament date.

        end_date_exclusive = (
            end_date
            + timedelta(days=1)
        )

        display_name = cls.clean_text(
            event.get("ShortName")
        )

        if not display_name:

            display_name = cls.clean_text(
                event.get("Name")
            )

        return SportEvent(
            title=(
                "🎱 Snooker - "
                f"{display_name}"
            ),
            start=start_date,
            end=end_date_exclusive,
            venue=(
                cls.build_tournament_location(
                    event
                )
            ),
            description=(
                cls.build_tournament_description(
                    event
                )
            ),
        )

    # ---------------------------------------------------------
    # SELECT CONFIGURED TOURNAMENTS
    # ---------------------------------------------------------

    @classmethod
    def select_placeholder_tournaments(
        cls,
        events,
    ):

        selected_events = []

        for event in events:

            if not cls.is_main_tour_event(
                event
            ):

                continue

            if not cls.validate_tournament(
                event
            ):

                print(
                    "Skipping invalid Snooker "
                    "tournament:",
                    cls.clean_text(
                        event.get("Name")
                    ),
                )

                continue

            selected_events.append(
                event
            )

        selected_events.sort(
            key=lambda event: (
                cls.parse_api_date(
                    event.get("StartDate")
                )
            )
        )

        return selected_events

    # ---------------------------------------------------------
    # CHECK IF PLAYER IS WATCHED
    # ---------------------------------------------------------

    @classmethod
    def is_watched_player(
        cls,
        player_id,
    ):

        return (
            player_id
            in cls.WATCHED_PLAYERS
        )

    # ---------------------------------------------------------
    # CHECK IF MATCH INVOLVES WATCHED PLAYER
    # ---------------------------------------------------------

    @classmethod
    def is_watched_match(
        cls,
        match,
    ):

        player1_id = match.get(
            "Player1ID"
        )

        player2_id = match.get(
            "Player2ID"
        )

        return bool(
            cls.is_watched_player(
                player1_id
            )
            or
            cls.is_watched_player(
                player2_id
            )
        )

    # ---------------------------------------------------------
    # RESOLVE PLAYER NAME
    # ---------------------------------------------------------

    @classmethod
    def resolve_player_name(
        cls,
        player_id,
        player_lookup,
    ):

        # Prefer the name returned by the player data.

        player_name = player_lookup.get(
            player_id
        )

        if player_name:

            return player_name

        # Fall back to the configured watchlist name.
        #
        # This is useful if a watched player's full
        # player record has not yet been downloaded.

        watched_name = (
            cls.WATCHED_PLAYERS.get(
                player_id
            )
        )

        if watched_name:

            return watched_name

        # Final fallback prevents malformed titles.

        if player_id is None:

            return "TBD"

        return f"Player {player_id}"

    # ---------------------------------------------------------
    # FIND EVENT FOR MATCH
    # ---------------------------------------------------------

    @staticmethod
    def find_event_for_match(
        match,
        event_lookup,
    ):

        event_id = match.get(
            "EventID"
        )

        return event_lookup.get(
            event_id
        )

    # ---------------------------------------------------------
    # BUILD EVENT LOOKUP
    # ---------------------------------------------------------

    @staticmethod
    def build_event_lookup(
        events,
    ):

        event_lookup = {}

        for event in events:

            event_id = event.get(
                "ID"
            )

            if event_id is None:

                continue

            event_lookup[event_id] = event

        return event_lookup

    # ---------------------------------------------------------
    # GET MATCH START DATETIME
    # ---------------------------------------------------------

    @classmethod
    def get_match_start(
        cls,
        match,
    ):

        # ScheduledDate is the correct calendar source
        # before the match begins.
        #
        # If it is unavailable, fall back to StartDate.

        scheduled_date = (
            cls.parse_api_datetime(
                match.get("ScheduledDate")
            )
        )

        if scheduled_date:

            return scheduled_date

        return cls.parse_api_datetime(
            match.get("StartDate")
        )

    # ---------------------------------------------------------
    # GET MATCH END DATETIME
    # ---------------------------------------------------------

    @classmethod
    def get_match_end(
        cls,
        match,
        start_datetime,
    ):

        end_datetime = (
            cls.parse_api_datetime(
                match.get("EndDate")
            )
        )

        # Only use EndDate when it is logically later
        # than the selected calendar start time.

        if (
            end_datetime
            and end_datetime
            > start_datetime
        ):

            return end_datetime

        return (
            start_datetime
            + cls.DEFAULT_MATCH_DURATION
        )
    
    # ---------------------------------------------------------
    # BUILD MATCH TITLE
    # ---------------------------------------------------------

    @classmethod
    def build_match_title(
        cls,
        match,
        player_lookup,
    ):

        player1_name = (
            cls.resolve_player_name(
                match.get("Player1ID"),
                player_lookup,
            )
        )

        player2_name = (
            cls.resolve_player_name(
                match.get("Player2ID"),
                player_lookup,
            )
        )

        return (
            "🎱 "
            f"{player1_name} vs "
            f"{player2_name}"
        )

    # ---------------------------------------------------------
    # BUILD MATCH DESCRIPTION
    # ---------------------------------------------------------

    @classmethod
    def build_match_description(
        cls,
        match,
        event,
        player_lookup,
    ):

        player1_name = (
            cls.resolve_player_name(
                match.get("Player1ID"),
                player_lookup,
            )
        )

        player2_name = (
            cls.resolve_player_name(
                match.get("Player2ID"),
                player_lookup,
            )
        )

        lines = [
            "Snooker Match",
            "",
            f"{player1_name} vs {player2_name}",
        ]

        if event:

            tournament_name = cls.clean_text(
                event.get("Name")
            )

            if tournament_name:

                lines.extend([
                    "",
                    f"Tournament: {tournament_name}",
                ])

        round_number = match.get(
            "Round"
        )

        if round_number is not None:

            lines.append(
                f"Round: {round_number}"
            )

        match_number = match.get(
            "Number"
        )

        if match_number is not None:

            lines.append(
                f"Match Number: {match_number}"
            )

        if match.get("Estimated"):

            lines.extend([
                "",
                "Scheduled time is estimated.",
            ])

        lines.extend([
            "",
            "Data Source:",
            "Snooker.org",
        ])

        return "\n".join(
            lines
        )

    # ---------------------------------------------------------
    # CREATE MATCH EVENT
    # ---------------------------------------------------------

    @classmethod
    def create_match_event(
        cls,
        match,
        event,
        player_lookup,
    ):

        start_datetime = (
            cls.get_match_start(
                match
            )
        )

        if not start_datetime:

            return None

        end_datetime = (
            cls.get_match_end(
                match,
                start_datetime,
            )
        )

        venue = ""

        if event:

            venue = (
                cls.build_tournament_location(
                    event
                )
            )

        return SportEvent(
            title=cls.build_match_title(
                match,
                player_lookup,
            ),
            start=start_datetime,
            end=end_datetime,
            venue=venue,
            description=(
                cls.build_match_description(
                    match,
                    event,
                    player_lookup,
                )
            ),
        )

    # ---------------------------------------------------------
    # CREATE WATCHED MATCH EVENTS
    # ---------------------------------------------------------

    @classmethod
    def create_watched_match_events(
        cls,
        matches,
        event_lookup,
        player_lookup,
    ):

        events = []

        for match in matches:

            if not cls.is_watched_match(
                match
            ):
                continue

            match_event = (
                cls.find_event_for_match(
                    match,
                    event_lookup,
                )
            )

            calendar_event = (
                cls.create_match_event(
                    match,
                    match_event,
                    player_lookup,
                )
            )

            if not calendar_event:

                print(
                    "Skipping watched Snooker "
                    "match without usable date:",
                    match.get("ID"),
                )

                continue

            events.append(
                calendar_event
            )

        events.sort(
            key=lambda event: event.start
        )

        return events

    # ---------------------------------------------------------
    # PRINT FIXTURE DIAGNOSTICS
    # ---------------------------------------------------------

    def print_fixture_diagnostics(
        self,
        selected_tournaments,
        watched_match_events,
        matches,
        player_lookup,
    ):

        print(
            f"Selected "
            f"{len(selected_tournaments)} "
            f"Snooker tournament placeholders"
        )

        watched_match_count = sum(
            1
            for match in matches
            if self.is_watched_match(
                match
            )
        )

        print(
            f"Found {watched_match_count} "
            f"watched Snooker match fixtures"
        )

        print(
            f"Generated "
            f"{len(watched_match_events)} "
            f"watched Snooker match events"
        )

        # Explain the known mismatch in our static fixtures.

        if not watched_match_events:

            fixture_player_ids = set()

            for match in matches:

                player1_id = match.get(
                    "Player1ID"
                )

                player2_id = match.get(
                    "Player2ID"
                )

                if player1_id is not None:

                    fixture_player_ids.add(
                        player1_id
                    )

                if player2_id is not None:

                    fixture_player_ids.add(
                        player2_id
                    )

            watched_ids = set(
                self.WATCHED_PLAYERS
            )

            if (
                fixture_player_ids
                and watched_ids.isdisjoint(
                    fixture_player_ids
                )
            ):

                print(
                    "  Expected fixture mismatch:"
                )

                print(
                    "  Match fixture player IDs:",
                    sorted(fixture_player_ids),
                )

                print(
                    "  Watched player IDs:",
                    sorted(watched_ids),
                )

        if player_lookup:

            print(
                "Loaded player lookup IDs:",
                sorted(player_lookup),
            )

    # ---------------------------------------------------------
    # GET EVENTS
    # ---------------------------------------------------------

    
    def get_events(self):

        print(
            "Loading Snooker local fixtures..."
        )

        # -----------------------------------------------------
        # 1. LOAD DATA
        # -----------------------------------------------------

        raw_events = self.download_events()

        raw_players = self.download_players()

        # -----------------------------------------------------
        # 2. BUILD LOOKUPS
        # -----------------------------------------------------

        event_lookup = (
            self.build_event_lookup(
                raw_events
            )
        )

        player_lookup = (
            self.build_player_lookup(
                raw_players
            )
        )

        # -----------------------------------------------------
        # 3. SELECT CONFIGURED TOURNAMENT PLACEHOLDERS
        # -----------------------------------------------------

        selected_tournaments = (
            self.select_placeholder_tournaments(
                raw_events
            )
        )

        # -----------------------------------------------------
        # 4. CREATE TRUE ALL-DAY PLACEHOLDERS
        # -----------------------------------------------------

        placeholder_events = [

            self.create_tournament_placeholder(
                event
            )

            for event in selected_tournaments

        ]

        # -----------------------------------------------------
        # 5. DOWNLOAD MATCHES
        # -----------------------------------------------------

        self.update_match_cache(
            selected_tournaments
        )

        matches = self.load_cached_matches(
            selected_tournaments
        )

        # -----------------------------------------------------
        # 6. CREATE MATCH EVENTS FOR WATCHED PLAYERS
        # -----------------------------------------------------

        self.load_watched_player_ids(
            player_lookup,
            self.load_watched_players(),
        )

        watched_match_events = (
            self.create_watched_match_events(
                matches,
                event_lookup,
                player_lookup,
            )
        )

        # -----------------------------------------------------
        # 7. PRINT DIAGNOSTICS
        # -----------------------------------------------------

        self.print_fixture_diagnostics(
            selected_tournaments,
            watched_match_events,
            matches,
            player_lookup,
        )

        # -----------------------------------------------------
        # 8. COMBINE EVENTS
        # -----------------------------------------------------

        calendar_events = (
            placeholder_events
            + watched_match_events
        )

        # Sort all-day events (date) and timed events (datetime)
        calendar_events.sort(
            key=lambda event: (
                datetime.combine(
                    event.start,
                    datetime.min.time(),
                    tzinfo=timezone.utc,
                )
                if isinstance(
                    event.start,
                    date,
                )
                and not isinstance(
                    event.start,
                    datetime,
                )
                else event.start
            )
        )

        print(
            f"Generated "
            f"{len(calendar_events)} "
            f"Snooker events"
        )

        return calendar_events