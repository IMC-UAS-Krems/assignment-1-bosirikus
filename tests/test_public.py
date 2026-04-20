"""
test_public.py
--------------
Public test suite template.

This file provides a minimal framework and examples to guide you in writing
comprehensive tests for your StreamingPlatform implementation. Each test class
corresponds to one of the 10 query methods (Q1-Q10).

You should:
1. Study the examples provided
2. Complete the stub tests (marked with TODO or pass statements)
3. Add additional test cases for edge cases and boundary conditions
4. Verify your implementation passes all tests

Run with:
    pytest tests/test_public.py -v
"""

import pytest
from datetime import datetime, timedelta, date

from streaming.platform import StreamingPlatform
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.playlists import CollaborativePlaylist, Playlist
from streaming.artists import Artist
from streaming.sessions import ListeningSession
from streaming.tracks import AlbumTrack
from streaming.albums import Album
from tests.conftest import FIXED_NOW, RECENT, OLD


# ===========================================================================
# Q1 - Total cumulative listening time for a given period
# ===========================================================================

class TestTotalListeningTime:
    """Test the total_listening_time_minutes(start, end) method."""

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        start = RECENT - timedelta(hours=1)
        end = FIXED_NOW
        result = platform.total_listening_time_minutes(start, end)
        assert isinstance(result, float)

    def test_empty_window_returns_zero(self, platform: StreamingPlatform) -> None:
        """Test that a time window with no sessions returns 0.0."""
        far_future = FIXED_NOW + timedelta(days=365)
        result = platform.total_listening_time_minutes(
            far_future, far_future + timedelta(hours=1)
        )
        assert result == 0.0

    def test_known_period_value(self, platform: StreamingPlatform) -> None:
        """Verify the correct total is returned for a known time window.

        Alice listens to t1 for 120s and Bob listens to t2 for 180s,
        both at RECENT. Total = (120 + 180) / 60 = 5.0 minutes.
        The OLD session (60 days ago) should not be counted.
        """
        alice = platform.get_user("u1")
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")

        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 120))
        platform.record_session(ListeningSession("s2", bob, t2, RECENT, 180))
        # This session is outside the window and should be excluded
        platform.record_session(ListeningSession("s3", alice, t1, OLD, 600))

        start = RECENT - timedelta(minutes=1)
        end = FIXED_NOW
        result = platform.total_listening_time_minutes(start, end)
        assert result == 5.0


# ===========================================================================
# Q2 - Average unique tracks per PremiumUser in the last N days
# ===========================================================================

class TestAvgUniqueTracksPremium:
    """Test the avg_unique_tracks_per_premium_user(days) method."""

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.avg_unique_tracks_per_premium_user(days=30)
        assert isinstance(result, float)

    def test_no_premium_users_returns_zero(self) -> None:
        """Test with a platform that has no premium users."""
        p = StreamingPlatform("EmptyPlatform")
        p.add_user(FreeUser("u99", "Nobody", age=25))
        assert p.avg_unique_tracks_per_premium_user() == 0.0

    def test_correct_value(self, platform: StreamingPlatform) -> None:
        """Bob is the only PremiumUser. He listens to t1 and t2 within the
        last 30 days (both at RECENT = 10 days ago). He also listens to t3
        at OLD (60 days ago) which should be excluded. Expected average = 2.0.
        """
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        t3 = platform.get_track("t3")

        platform.record_session(ListeningSession("s1", bob, t1, RECENT, 120))
        platform.record_session(ListeningSession("s2", bob, t2, RECENT, 120))
        # Same track again — should not count as a second unique track
        platform.record_session(ListeningSession("s3", bob, t1, RECENT, 120))
        # Outside the 30-day window — should be excluded
        platform.record_session(ListeningSession("s4", bob, t3, OLD, 120))

        result = platform.avg_unique_tracks_per_premium_user(days=30)
        assert result == 2.0


# ===========================================================================
# Q3 - Track with the most distinct listeners
# ===========================================================================

class TestTrackMostDistinctListeners:
    """Test the track_with_most_distinct_listeners() method."""

    def test_empty_platform_returns_none(self) -> None:
        """Test that an empty platform returns None."""
        p = StreamingPlatform("Empty")
        assert p.track_with_most_distinct_listeners() is None

    def test_correct_track(self, platform: StreamingPlatform) -> None:
        """t1 is heard by both Alice and Bob (2 distinct listeners).
        t2 is only heard by Alice (1 distinct listener).
        The method should return t1.
        """
        alice = platform.get_user("u1")
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")

        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 120))
        platform.record_session(ListeningSession("s2", bob, t1, RECENT, 120))
        platform.record_session(ListeningSession("s3", alice, t2, RECENT, 120))

        result = platform.track_with_most_distinct_listeners()
        assert result == t1


# ===========================================================================
# Q4 - Average session duration per user subtype, ranked
# ===========================================================================

class TestAvgSessionDurationByType:
    """Test the avg_session_duration_by_user_type() method."""

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (str, float) tuples."""
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 120))

        result = platform.avg_session_duration_by_user_type()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], str) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by duration (longest first)."""
        alice = platform.get_user("u1")
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 60))
        platform.record_session(ListeningSession("s2", bob, t2, RECENT, 300))

        result = platform.avg_session_duration_by_user_type()
        durations = [r[1] for r in result]
        assert durations == sorted(durations, reverse=True)

    def test_all_user_types_present(self, platform: StreamingPlatform) -> None:
        """When sessions exist for both FreeUser and PremiumUser,
        both type names should appear in the result.
        """
        alice = platform.get_user("u1")
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 120))
        platform.record_session(ListeningSession("s2", bob, t1, RECENT, 300))

        result = platform.avg_session_duration_by_user_type()
        type_names = [r[0] for r in result]
        assert "FreeUser" in type_names
        assert "PremiumUser" in type_names


# ===========================================================================
# Q5 - Total listening time for underage sub-users
# ===========================================================================

class TestUnderageSubUserListening:
    """Test the total_listening_time_underage_sub_users_minutes() method."""

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.total_listening_time_underage_sub_users_minutes()
        assert isinstance(result, float)

    def test_no_family_users(self) -> None:
        """Test a platform with no family accounts."""
        p = StreamingPlatform("NoFamily")
        p.add_user(FreeUser("u1", "Solo", age=20))
        assert p.total_listening_time_underage_sub_users_minutes() == 0.0

    def test_correct_value_default_threshold(self, platform: StreamingPlatform) -> None:
        """A FamilyMember aged 16 (under default threshold of 18) listens for
        240 seconds. Expected total = 240 / 60 = 4.0 minutes.
        The adult member (age 20) should not be counted.
        """
        parent = FamilyAccountUser("u3", "Parent", age=40)
        child = FamilyMember("u4", "Child", age=16, parent=parent)
        adult_member = FamilyMember("u5", "OldChild", age=20, parent=parent)
        parent.add_sub_user(child)
        parent.add_sub_user(adult_member)
        platform.add_user(parent)
        platform.add_user(child)
        platform.add_user(adult_member)

        t1 = platform.get_track("t1")
        platform.record_session(ListeningSession("s1", child, t1, RECENT, 240))
        platform.record_session(ListeningSession("s2", adult_member, t1, RECENT, 300))

        result = platform.total_listening_time_underage_sub_users_minutes()
        assert result == 4.0

    def test_custom_threshold(self, platform: StreamingPlatform) -> None:
        """With threshold=15, a 16-year-old should NOT be counted.
        Only members strictly under the threshold are included.
        """
        parent = FamilyAccountUser("u3", "Parent", age=40)
        child = FamilyMember("u4", "Child", age=16, parent=parent)
        parent.add_sub_user(child)
        platform.add_user(parent)
        platform.add_user(child)

        t1 = platform.get_track("t1")
        platform.record_session(ListeningSession("s1", child, t1, RECENT, 300))

        result = platform.total_listening_time_underage_sub_users_minutes(age_threshold=15)
        assert result == 0.0


# ===========================================================================
# Q6 - Top N artists by total listening time
# ===========================================================================

class TestTopArtistsByListeningTime:
    """Test the top_artists_by_listening_time(n) method."""

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (Artist, float) tuples."""
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 180))

        result = platform.top_artists_by_listening_time(n=3)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], Artist) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by listening time (highest first)."""
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")

        second_artist = Artist("a2", "Second", genre="rock")
        second_track = AlbumTrack("t99", "Rock Song", 120, "rock", second_artist, track_number=1)
        platform.add_artist(second_artist)
        platform.add_track(second_track)

        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 600))
        platform.record_session(ListeningSession("s2", alice, second_track, RECENT, 60))

        result = platform.top_artists_by_listening_time(n=5)
        minutes = [r[1] for r in result]
        assert minutes == sorted(minutes, reverse=True)

    def test_respects_n_parameter(self, platform: StreamingPlatform) -> None:
        """Verify only the top N artists are returned."""
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 120))

        result = platform.top_artists_by_listening_time(n=2)
        assert len(result) <= 2

    def test_top_artist(self, platform: StreamingPlatform) -> None:
        """Pixels is the only artist. Alice listens to t1 for 120s and t2
        for 180s. Total for Pixels = (120 + 180) / 60 = 5.0 minutes.
        """
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        pixels = platform.get_artist("a1")

        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 120))
        platform.record_session(ListeningSession("s2", alice, t2, RECENT, 180))

        result = platform.top_artists_by_listening_time(n=1)
        assert len(result) == 1
        assert result[0][0] == pixels
        assert result[0][1] == 5.0


# ===========================================================================
# Q7 - User's top genre and percentage
# ===========================================================================

class TestUserTopGenre:
    """Test the user_top_genre(user_id) method."""

    def test_returns_tuple_or_none(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a tuple or None."""
        result = platform.user_top_genre("u1")
        if result is not None:
            assert isinstance(result, tuple) and len(result) == 2
            assert isinstance(result[0], str) and isinstance(result[1], float)

    def test_nonexistent_user_returns_none(self, platform: StreamingPlatform) -> None:
        """Test that a nonexistent user ID returns None."""
        assert platform.user_top_genre("does_not_exist") is None

    def test_percentage_in_valid_range(self, platform: StreamingPlatform) -> None:
        """Verify percentage is between 0 and 100."""
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 180))

        for user in platform.all_users():
            result = platform.user_top_genre(user.user_id)
            if result is not None:
                _, pct = result
                assert 0.0 <= pct <= 100.0

    def test_correct_top_genre(self, platform: StreamingPlatform) -> None:
        """All tracks in the fixture are genre 'pop'. Alice listens to t1
        and t2, both pop. Top genre should be 'pop' at 100%.
        """
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")

        platform.record_session(ListeningSession("s1", alice, t1, RECENT, 180))
        platform.record_session(ListeningSession("s2", alice, t2, RECENT, 120))

        genre, pct = platform.user_top_genre("u1")
        assert genre == "pop"
        assert pct == 100.0


# ===========================================================================
# Q8 - CollaborativePlaylists with more than threshold distinct artists
# ===========================================================================

class TestCollaborativePlaylistsManyArtists:
    """Test the collaborative_playlists_with_many_artists(threshold) method."""

    def test_returns_list_of_collaborative_playlists(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a list of CollaborativePlaylist objects."""
        result = platform.collaborative_playlists_with_many_artists()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, CollaborativePlaylist)

    def test_higher_threshold_returns_empty(
        self, platform: StreamingPlatform
    ) -> None:
        """Test that a high threshold returns an empty list."""
        result = platform.collaborative_playlists_with_many_artists(threshold=100)
        assert result == []

    def test_default_threshold(self, platform: StreamingPlatform) -> None:
        """A collaborative playlist with songs from 4 distinct artists should
        be returned with the default threshold of 3. A playlist with only
        1 artist should not be returned.
        """
        alice = platform.get_user("u1")

        # Build 4 artists and 4 tracks
        artists = [Artist(f"ax{i}", f"Artist {i}", genre="pop") for i in range(4)]
        tracks = []
        for i, artist in enumerate(artists):
            track = AlbumTrack(f"tx{i}", f"Song {i}", 120, "pop", artist,
                               track_number=1)
            platform.add_artist(artist)
            platform.add_track(track)
            tracks.append(track)

        # Playlist with 4 distinct artists — should pass threshold=3
        big_collab = CollaborativePlaylist("cp1", "Big Collab", owner=alice)
        for track in tracks:
            big_collab.add_track(track)
        platform.add_playlist(big_collab)

        # Playlist with only 1 artist — should not pass threshold=3
        small_collab = CollaborativePlaylist("cp2", "Small Collab", owner=alice)
        small_collab.add_track(platform.get_track("t1"))
        platform.add_playlist(small_collab)

        result = platform.collaborative_playlists_with_many_artists(threshold=3)
        assert big_collab in result
        assert small_collab not in result


# ===========================================================================
# Q9 - Average tracks per playlist type
# ===========================================================================

class TestAvgTracksPerPlaylistType:
    """Test the avg_tracks_per_playlist_type() method."""

    def test_returns_dict_with_both_keys(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a dict with both playlist types."""
        result = platform.avg_tracks_per_playlist_type()
        assert isinstance(result, dict)
        assert "Playlist" in result
        assert "CollaborativePlaylist" in result

    def test_standard_playlist_average(self, platform: StreamingPlatform) -> None:
        """Two standard playlists: one with 2 tracks and one with 4 tracks.
        Expected average = (2 + 4) / 2 = 3.0.
        """
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        t3 = platform.get_track("t3")

        p1 = Playlist("p1", "Short", owner=alice)
        p1.add_track(t1)
        p1.add_track(t2)

        p2 = Playlist("p2", "Long", owner=alice)
        p2.add_track(t1)
        p2.add_track(t2)
        p2.add_track(t3)
        p2.add_track(t3)  # duplicate — should not be added twice

        platform.add_playlist(p1)
        platform.add_playlist(p2)

        result = platform.avg_tracks_per_playlist_type()
        # p1 has 2 tracks, p2 has 3 tracks (t3 deduped) → avg = 2.5
        assert result["Playlist"] == 2.5

    def test_collaborative_playlist_average(
        self, platform: StreamingPlatform
    ) -> None:
        """One collaborative playlist with 3 tracks. Expected average = 3.0."""
        alice = platform.get_user("u1")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        t3 = platform.get_track("t3")

        cp = CollaborativePlaylist("cp1", "Collab", owner=alice)
        cp.add_track(t1)
        cp.add_track(t2)
        cp.add_track(t3)
        platform.add_playlist(cp)

        result = platform.avg_tracks_per_playlist_type()
        assert result["CollaborativePlaylist"] == 3.0

    def test_no_instances_returns_zero(self) -> None:
        """A platform with no playlists should return 0.0 for both types."""
        p = StreamingPlatform("Empty")
        result = p.avg_tracks_per_playlist_type()
        assert result["Playlist"] == 0.0
        assert result["CollaborativePlaylist"] == 0.0


# ===========================================================================
# Q10 - Users who completed at least one full album
# ===========================================================================

class TestUsersWhoCompletedAlbums:
    """Test the users_who_completed_albums() method."""

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (User, list) tuples."""
        from streaming.users import User
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        t3 = platform.get_track("t3")
        platform.record_session(ListeningSession("s1", bob, t1, RECENT, 180))
        platform.record_session(ListeningSession("s2", bob, t2, RECENT, 210))
        platform.record_session(ListeningSession("s3", bob, t3, RECENT, 195))

        result = platform.users_who_completed_albums()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], User) and isinstance(item[1], list)

    def test_completed_album_titles_are_strings(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify all completed album titles are strings."""
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        t3 = platform.get_track("t3")
        platform.record_session(ListeningSession("s1", bob, t1, RECENT, 180))
        platform.record_session(ListeningSession("s2", bob, t2, RECENT, 210))
        platform.record_session(ListeningSession("s3", bob, t3, RECENT, 195))

        result = platform.users_who_completed_albums()
        for _, titles in result:
            assert all(isinstance(t, str) for t in titles)

    def test_correct_users_identified(self, platform: StreamingPlatform) -> None:
        """Bob listens to all 3 tracks on Digital Dreams — he should be
        identified as having completed an album. Alice only listens to t1
        and t2, so she should not appear in the result.
        """
        alice = platform.get_user("u1")
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        t3 = platform.get_track("t3")

        # Bob completes the album
        platform.record_session(ListeningSession("s1", bob, t1, RECENT, 180))
        platform.record_session(ListeningSession("s2", bob, t2, RECENT, 210))
        platform.record_session(ListeningSession("s3", bob, t3, RECENT, 195))

        # Alice only listens to 2 of the 3 tracks
        platform.record_session(ListeningSession("s4", alice, t1, RECENT, 180))
        platform.record_session(ListeningSession("s5", alice, t2, RECENT, 210))

        result = platform.users_who_completed_albums()
        users_in_result = [u for u, _ in result]
        assert bob in users_in_result
        assert alice not in users_in_result

    def test_correct_album_titles(self, platform: StreamingPlatform) -> None:
        """When Bob completes Digital Dreams, the album title in the result
        should be exactly 'Digital Dreams'.
        """
        bob = platform.get_user("u2")
        t1 = platform.get_track("t1")
        t2 = platform.get_track("t2")
        t3 = platform.get_track("t3")

        platform.record_session(ListeningSession("s1", bob, t1, RECENT, 180))
        platform.record_session(ListeningSession("s2", bob, t2, RECENT, 210))
        platform.record_session(ListeningSession("s3", bob, t3, RECENT, 195))

        result = platform.users_who_completed_albums()
        bob_entry = next((titles for u, titles in result if u.user_id == "u2"), None)
        assert bob_entry is not None
        assert "Digital Dreams" in bob_entry