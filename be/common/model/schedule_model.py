from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScheduleModel:
    date_time: datetime
    status: str
    home_team: str
    away_team: str
    league: str
    cheer_url: str
