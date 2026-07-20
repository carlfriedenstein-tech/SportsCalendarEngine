class HealthReport:

    @staticmethod
    def print(results, total_events, total_runtime):

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        print()
        print("=" * 70)
        print("Run Summary")
        print("=" * 70)

        for result in results:

            status = "OK" if result.success else "FAILED"

            print(
                f"{result.plugin:<25}"
                f"{status:<8}"
                f"{result.events:>5} events"
                f"{result.duration:>8.2f}s"
            )

            if result.success:

                if result.coverage_start and result.coverage_end:

                    print(
                        f"{'':<25}"
                        f"Coverage : "
                        f"{result.coverage_start:%Y-%m-%d} -> "
                        f"{result.coverage_end:%Y-%m-%d}"
                    )

                if result.duplicates > 0:
                    print(
                        f"{'':<25}"
                        f"Duplicates Removed : {result.duplicates}"
                    )

                if result.skipped > 0:
                    print(
                        f"{'':<25}"
                        f"Skipped Events     : {result.skipped}"
                    )

            else:

                print(
                    f"{'':<25}"
                    f"Error : {result.error}"
                )

        print("-" * 70)
        print(f"Plugins Loaded      : {len(results)}")
        print(f"Successful Plugins  : {successful}")
        print(f"Failed Plugins      : {failed}")
        print(f"Total Events        : {total_events}")
        print(f"Total Runtime       : {total_runtime:.2f}s")
        print("=" * 70)