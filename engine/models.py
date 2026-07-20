from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class ValidationResult:
    events: List

    duplicates_removed: int = 0
    skipped_events: int = 0

    missing_title: int = 0
    missing_start: int = 0
    missing_end: int = 0
    invalid_dates: int = 0


@dataclass
class PluginResult:

    plugin: str

    success: bool

    events: int = 0

    duplicates: int = 0
    skipped: int = 0

    duration: float = 0.0

    coverage_start: Optional[datetime] = None
    coverage_end: Optional[datetime] = None

    error: Optional[str] = None

    warnings: List[str] = field(default_factory=list)