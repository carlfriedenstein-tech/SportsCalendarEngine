from dataclasses import dataclass
from datetime import datetime


@dataclass
class SportEvent:
    title: str
    start: datetime
    end: datetime
    venue: str
    description: str