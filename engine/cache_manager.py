from pathlib import Path
from datetime import datetime, timedelta
import json


class CacheManager:

    # ---------------------------------------------------------
    # INITIALIZE
    # ---------------------------------------------------------

    def __init__(self):

        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)

        self.matches_dir = (
            self.cache_dir / "matches"
        )

        self.matches_dir.mkdir(
            exist_ok=True
        )

    # ---------------------------------------------------------
    # CACHE FILES
    # ---------------------------------------------------------

    def events_file(self):

        return (
            self.cache_dir
            / "events.json"
        )

    def players_file(self):

        return (
            self.cache_dir
            / "players.json"
        )

    def matches_file(
        self,
        event_id,
    ):

        return (
            self.matches_dir
            / f"{event_id}.json"
        )

    # ---------------------------------------------------------
    # LOAD JSON
    # ---------------------------------------------------------

    def load_json(
        self,
        file_path,
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            return json.load(file)

    # ---------------------------------------------------------
    # SAVE JSON
    # ---------------------------------------------------------

    def save_json(
        self,
        file_path,
        data,
    ):

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            file_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
            )

    # ---------------------------------------------------------
    # CACHE AGE
    # ---------------------------------------------------------

    def is_expired(
        self,
        file_path,
        max_age,
    ):

        file_path = Path(file_path)

        if not file_path.exists():

            return True

        modified = datetime.fromtimestamp(
            file_path.stat().st_mtime
        )

        return (
            datetime.now()
            - modified
        ) > max_age

    # ---------------------------------------------------------
    # REFRESH RULES
    # ---------------------------------------------------------

    def events_expired(self):

        return self.is_expired(
            self.events_file(),
            timedelta(days=7),
        )

    def players_expired(self):

        return self.is_expired(
            self.players_file(),
            timedelta(days=30),
        )

    def matches_expired(
        self,
        event_id,
    ):

        return self.is_expired(
            self.matches_file(
                event_id
            ),
            timedelta(hours=6),
        )