from streaming.artists import Artist
from streaming.tracks import AlbumTrack


class Album:
    def __init__(self, album_id: str, title: str, artist: Artist, release_year: int, tracks: list[AlbumTrack] | None = None):
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_year = release_year
        self.tracks: list[AlbumTrack] = tracks if tracks is not None else []

    def add_track(self, track: AlbumTrack) -> None:
        self.tracks.append(track)
        self.tracks.sort(key=lambda t: t.track_number)
        track.album = self

    def track_ids(self) -> set[str]:
        return {t.track_id for t in self.tracks}

    def duration_seconds(self) -> int:
        return sum(t.duration_seconds for t in self.tracks)