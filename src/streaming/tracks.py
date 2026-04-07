from __future__ import annotations
from abc import ABC
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from streaming.artists import Artist
    from streaming.albums import Album


class Track(ABC):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str):
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.genre = genre

    def duration_minutes(self) -> float:
        return self.duration_seconds / 60

    def __eq__(self, other) -> bool:
        if not isinstance(other, Track):
            return False
        return self.track_id == other.track_id


class Song(Track):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist: Artist):
        super().__init__(track_id, title, duration_seconds, genre)
        self.artist = artist


class AlbumTrack(Song):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist: Artist, track_number: int, album: Album | None = None):
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.track_number = track_number
        self.album = album


class SingleRelease(Song):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist: Artist, release_date: date):
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.release_date = release_date


class Podcast(Track):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, description: str = ""):
        super().__init__(track_id, title, duration_seconds, genre)
        self.host = host
        self.description = description


class InterviewEpisode(Podcast):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, guest: str, description: str = ""):
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.guest = guest


class NarrativeEpisode(Podcast):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, season: int, episode_number: int, description: str = ""):
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.season = season
        self.episode_number = episode_number


class AudiobookTrack(Track):
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, author: str, narrator: str):
        super().__init__(track_id, title, duration_seconds, genre)
        self.author = author
        self.narrator = narrator