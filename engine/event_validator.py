from datetime import date, datetime, time, timezone

from engine.models import ValidationResult


class EventValidator:

    @staticmethod
    def _normalize_datetime(value):
        """
        Convert dates and datetimes into comparable UTC-aware datetimes.

        This is only used internally for validation and sorting.
        The original SportEvent values are left unchanged.
        """

        if isinstance(value, date) and not isinstance(value, datetime):

            return datetime.combine(
                value,
                time.min,
                tzinfo=timezone.utc
            )

        if value.tzinfo is None:

            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    @classmethod
    def validate(cls, events):

        valid_events = []

        seen = set()

        duplicates_removed = 0
        skipped_events = 0

        missing_title = 0
        missing_start = 0
        missing_end = 0
        invalid_dates = 0

        for event in events:

            if not getattr(event, "title", None):
                missing_title += 1
                skipped_events += 1
                continue

            if getattr(event, "start", None) is None:
                missing_start += 1
                skipped_events += 1
                continue

            if getattr(event, "end", None) is None:
                missing_end += 1
                skipped_events += 1
                continue

            normalized_start = cls._normalize_datetime(
                event.start
            )

            normalized_end = cls._normalize_datetime(
                event.end
            )

            if normalized_end <= normalized_start:
                invalid_dates += 1
                skipped_events += 1
                continue

            key = (
                event.title,
                normalized_start,
                normalized_end
            )

            if key in seen:
                duplicates_removed += 1
                continue

            seen.add(key)

            valid_events.append(event)

        valid_events.sort(
            key=lambda event: cls._normalize_datetime(
                event.start
            )
        )

        return ValidationResult(
            events=valid_events,
            duplicates_removed=duplicates_removed,
            skipped_events=skipped_events,
            missing_title=missing_title,
            missing_start=missing_start,
            missing_end=missing_end,
            invalid_dates=invalid_dates
        )