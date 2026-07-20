import json
from datetime import datetime
from pathlib import Path


class RegressionDetector:

    FILE = Path("data/plugin_stats.json")

    DROP_THRESHOLD = 0.50

    @classmethod
    def load(cls):

        if cls.FILE.exists():

            with open(
                cls.FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        return {}

    @classmethod
    def save(cls, stats):

        cls.FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            cls.FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                stats,
                f,
                indent=4
            )

    @classmethod
    def check(cls, results):

        previous = cls.load()

        for result in results:

            if not result.success:
                continue

            old = previous.get(result.plugin)

            if not old:
                continue

            previous_events = old.get(
                "events",
                0
            )

            if previous_events == 0:
                continue

            if (
                result.events
                < previous_events * cls.DROP_THRESHOLD
            ):

                print()

                print(
                    f"WARNING: {result.plugin} event count dropped "
                    f"from {previous_events} to {result.events}"
                )

    @classmethod
    def update(cls, results):

        stats = cls.load()

        now = datetime.now().isoformat(
            timespec="seconds"
        )

        for result in results:

            if not result.success:
                continue

            stats[result.plugin] = {

                "last_success": now,

                "events": result.events,

                "coverage_start": (
                    result.coverage_start.isoformat()
                    if result.coverage_start
                    else None
                ),

                "coverage_end": (
                    result.coverage_end.isoformat()
                    if result.coverage_end
                    else None
                )

            }

        cls.save(stats)