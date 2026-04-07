from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.users import User
    from streaming.tracks import Track


class ListeningSession:
    def __init__(self, session_id: str, user: User, track: Track, timestamp: datetime, duration_listened_seconds: int):
        self.session_id = session_id
        self.user = user
        self.track = track
        self.timestamp = timestamp
        self.duration_listened_seconds = duration_listened_seconds

    def duration_listened_minutes(self) -> float:
        return self.duration_listened_seconds / 60