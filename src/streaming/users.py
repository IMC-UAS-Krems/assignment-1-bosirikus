from __future__ import annotations
from abc import ABC
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.sessions import ListeningSession


class User(ABC):
    def __init__(self, user_id: str, name: str, age: int, sessions: list[ListeningSession] | None = None):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions: list[ListeningSession] = sessions if sessions is not None else []

    def add_session(self, session: ListeningSession) -> None:
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        return sum(s.duration_listened_seconds for s in self.sessions)

    def total_listening_minutes(self) -> float:
        return self.total_listening_seconds() / 60

    def unique_tracks_listened(self) -> set[str]:
        return {s.track.track_id for s in self.sessions}


class FreeUser(User):
    MAX_SKIPS_PER_HOUR: int = 6


class PremiumUser(User):
    def __init__(self, user_id: str, name: str, age: int, subscription_start: date, sessions: list[ListeningSession] | None = None):
        super().__init__(user_id, name, age, sessions)
        self.subscription_start = subscription_start


class FamilyAccountUser(PremiumUser):
    def __init__(self, user_id: str, name: str, age: int, subscription_start: date | None = None, sessions: list[ListeningSession] | None = None):
        super().__init__(user_id, name, age, subscription_start, sessions)
        self.sub_users: list[FamilyMember] = []

    def add_sub_user(self, member: FamilyMember) -> None:
        self.sub_users.append(member)

    def all_members(self) -> list[User]:
        return [self] + self.sub_users


class FamilyMember(User):
    def __init__(self, user_id: str, name: str, age: int, parent: FamilyAccountUser, sessions: list[ListeningSession] | None = None):
        super().__init__(user_id, name, age, sessions)
        self.parent = parent