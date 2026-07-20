from time import perf_counter
import traceback

from engine.calendar_writer import CalendarWriter
from engine.plugin_loader import PluginLoader
from engine.event_validator import EventValidator
from engine.calendar_guard import CalendarGuard
from engine.health_report import HealthReport
from engine.models import PluginResult
from engine.regression_detector import RegressionDetector


class SportsCalendarEngine:

    def run(self):

        engine_start = perf_counter()

        loader = PluginLoader()
        plugins = loader.load_plugins()

        writer = CalendarWriter()

        all_events = []
        results = []

        print("=" * 70)
        print("Sports Calendar Engine")
        print("=" * 70)

        for plugin in plugins:

            print(f"\nLoading {plugin.name}...")

            plugin_start = perf_counter()

            try:

                # Plugin pre-processing
                plugin.before_run()

                # Download and parse events
                events = plugin.get_events()

                # Plugin post-processing
                events = plugin.after_run(events)

                # Validate events
                validation = EventValidator.validate(events)
                events = validation.events

                # Write individual calendar
                if CalendarGuard.should_write(
                    plugin.name,
                    plugin.filename,
                    validation
                ):

                    writer.write(
                        events,
                        plugin.filename
                    )

                    # Add to combined calendar
                    all_events.extend(events)

                duration = perf_counter() - plugin_start

                print("✓ SUCCESS")
                print(f"  Events          : {len(events)}")
                print(f"  Duplicates      : {validation.duplicates_removed}")
                print(f"  Skipped         : {validation.skipped_events}")
                print(f"  Time            : {duration:.2f}s")

                results.append(
                    PluginResult(
                        plugin=plugin.name,
                        success=True,
                        events=len(events),
                        duplicates=validation.duplicates_removed,
                        skipped=validation.skipped_events,
                        duration=duration,
                        coverage_start=(
                            events[0].start
                            if events
                            else None
                        ),
                        coverage_end=(
                            events[-1].end
                            if events
                            else None
                        )
                    )
                )

            except Exception as ex:

                duration = perf_counter() - plugin_start

                print("✗ FAILED")
                print(f"  Time            : {duration:.2f}s")
                print(f"  Error           : {ex}\n")

                traceback.print_exc()

                results.append(
                    PluginResult(
                        plugin=plugin.name,
                        success=False,
                        duration=duration,
                        error=str(ex)
                    )
                )

                continue

        # Validate the combined calendar
        combined_validation = EventValidator.validate(
            all_events
        )

        all_events = combined_validation.events

        # Write combined calendar only if at least one
        # valid event remains.
        if all_events:

            writer.write(
                all_events,
                "all_sports.ics"
            )

        else:

            print("\nWARNING: No valid events generated.")
            print("Combined calendar was not written.")

        total_duration = (
            perf_counter() - engine_start
        )

        HealthReport.print(
            results,
            len(all_events),
            total_duration
        )

        RegressionDetector.check(results)

        if any(
            result.success
            for result in results
        ):

            RegressionDetector.update(results)