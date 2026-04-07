from streaming.users import User
from streaming.tracks import Track


class Playlist:
    def __init__(self, playlist_id: str, name: str, owner: User, tracks: list[Track] | None = None):
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.tracks: list[Track] = tracks if tracks is not None else []

    def add_track(self, track: Track) -> None:
        if track not in self.tracks:
            self.tracks.append(track)

    def remove_track(self, track_id: str) -> None:
        self.tracks = [t for t in self.tracks if t.track_id != track_id]

    def total_duration_seconds(self) -> int:
        return sum(t.duration_seconds for t in self.tracks)


class CollaborativePlaylist(Playlist):
    def __init__(self, playlist_id: str, name: str, owner: User, tracks: list[Track] | None = None, contributors: list[User] | None = None):
        super().__init__(playlist_id, name, owner, tracks)
        self.contributors: list[User] = contributors if contributors is not None else [owner]

    def add_contributor(self, user: User) -> None:
        if user not in self.contributors:
            self.contributors.append(user)

    def remove_contributor(self, user: User) -> None:
        if user != self.owner:
            self.contributors = [c for c in self.contributors if c != user]