from datetime import datetime, timedelta
from collections import defaultdict
from streaming import Track, User, Artist, Album, Playlist, ListeningSession, CollaborativePlaylist
from streaming.tracks import Song
from streaming.users import PremiumUser, FamilyAccountUser


class StreamingPlatform:
    def __init__(self, name: str):
        self.name = name
        self._catalogue: dict[str, Track] = {}
        self._users: dict[str, User] = {}
        self._artists: dict[str, Artist] = {}
        self._albums: dict[str, Album] = {}
        self._playlists: dict[str, Playlist] = {}
        self._sessions: list[ListeningSession] = []

    def add_track(self, track: Track) -> None:
        self._catalogue[track.track_id] = track

    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def add_artist(self, artist: Artist) -> None:
        self._artists[artist.artist_id] = artist

    def add_album(self, album: Album) -> None:
        self._albums[album.album_id] = album

    def add_playlist(self, playlist: Playlist) -> None:
        self._playlists[playlist.playlist_id] = playlist

    def record_session(self, session: ListeningSession) -> None:
        self._sessions.append(session)
        session.user.add_session(session)

    def get_track(self, track_id: str) -> Track | None:
        return self._catalogue.get(track_id)

    def get_user(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_artist(self, artist_id: str) -> Artist | None:
        return self._artists.get(artist_id)

    def get_album(self, album_id: str) -> Album | None:
        return self._albums.get(album_id)

    def all_users(self) -> list[User]:
        return list(self._users.values())

    def all_tracks(self) -> list[Track]:
        return list(self._catalogue.values())

    # Q1
    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        return float(sum(
            s.duration_listened_seconds / 60
            for s in self._sessions
            if start <= s.timestamp <= end
        ))

    # Q2
    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        cutoff = datetime.now() - timedelta(days=days)
        premium_users = [u for u in self._users.values() if isinstance(u, PremiumUser)]
        if not premium_users:
            return 0.0
        total = sum(
            len({s.track.track_id for s in u.sessions if s.timestamp >= cutoff})
            for u in premium_users
        )
        return float(total / len(premium_users))

    # Q3
    def track_with_most_distinct_listeners(self) -> Track | None:
        if not self._sessions:
            return None
        listeners = defaultdict(set)
        for s in self._sessions:
            listeners[s.track.track_id].add(s.user.user_id)
        best_id = max(listeners, key=lambda tid: len(listeners[tid]))
        return self._catalogue.get(best_id)

    # Q4
    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        groups = defaultdict(list)
        for s in self._sessions:
            groups[type(s.user).__name__].append(s.duration_listened_seconds)
        result = [
            (name, float(sum(durations) / len(durations)))
            for name, durations in groups.items()
        ]
        return sorted(result, key=lambda x: x[1], reverse=True)

    # Q5
    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        underage_ids = set()
        for u in self._users.values():
            if isinstance(u, FamilyAccountUser):
                for member in u.sub_users:
                    if member.age < age_threshold:
                        underage_ids.add(member.user_id)
        return float(sum(
            s.duration_listened_seconds / 60
            for s in self._sessions
            if s.user.user_id in underage_ids
        ))

    # Q6
    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
        totals = defaultdict(float)
        for s in self._sessions:
            if isinstance(s.track, Song):
                totals[s.track.artist.artist_id] += s.duration_listened_seconds / 60
        ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:n]
        return [(self._artists[artist_id], minutes) for artist_id, minutes in ranked]

    # Q7
    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        user = self._users.get(user_id)
        if not user or not user.sessions:
            return None
        genre_time = defaultdict(float)
        for s in user.sessions:
            genre_time[s.track.genre] += s.duration_listened_seconds
        total = sum(genre_time.values())
        top = max(genre_time, key=lambda g: genre_time[g])
        return top, genre_time[top] / total * 100

    # Q8
    def collaborative_playlists_with_many_artists(self, threshold: int = 3) -> list[CollaborativePlaylist]:
        result = []
        for p in self._playlists.values():
            if isinstance(p, CollaborativePlaylist):
                artists = {t.artist.artist_id for t in p.tracks if isinstance(t, Song)}
                if len(artists) > threshold:
                    result.append(p)
        return result

    # Q9
    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        collaborative = [len(p.tracks) for p in self._playlists.values() if isinstance(p, CollaborativePlaylist)]
        playlists = [len(p.tracks) for p in self._playlists.values() if type(p).__name__ == "Playlist"]
        return {
            "Playlist": float(sum(playlists) / len(playlists)) if playlists else 0.0,
            "CollaborativePlaylist": float(sum(collaborative) / len(collaborative)) if collaborative else 0.0,
        }

    # Q10
    def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
        result = []
        for user in self._users.values():
            listened = {s.track.track_id for s in user.sessions}
            completed = [
                album.title
                for album in self._albums.values()
                if album.tracks and set(album.track_ids()).issubset(listened)
            ]
            if completed:
                result.append((user, completed))
        return result