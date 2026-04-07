from streaming.tracks import Track


class Artist:
    def __init__(self, artist_id: str, name: str, genre: str, tracks: list[Track] | None = None):
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.tracks: list[Track] = tracks if tracks is not None else []

    def add_track(self, track: Track) -> None:
        self.tracks.append(track)

    def track_count(self) -> int:
        return len(self.tracks)