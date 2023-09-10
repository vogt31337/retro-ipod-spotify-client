import abc
from dataclasses import dataclass

@dataclass
class NowPlayingItem:
    name: str           # Title or track label
    artist: str         # Artist currently playing
    album: str          # Album title
    context_name: str   # The context from which the track is, e.g. playlist name
    state: str          # Current state: play, pause, stop
    is_repeat: bool
    is_random: bool
    is_single: bool
    timestamp: float    # Timestamp since start of the song in seconds
    progress: float     # Progress in seconds
    duration: float     # Duration in seconds
    track_index: int    # Track number on album
    track_total: int    # Total number of tracks on album


class FormalPlayerInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'play_previous') and
                callable(subclass.play_previous) and
                hasattr(subclass, 'play_next') and
                callable(subclass.play_next) or
                hasattr(subclass, 'toggle_play') and
                callable(subclass.toggle_play) or
                hasattr(subclass, 'resume') and
                callable(subclass.resume) or
                NotImplemented)

    @abc.abstractmethod
    def set_datastore(self, datastore):
        raise NotImplementedError

    @abc.abstractmethod
    def play_previous(self):
        raise NotImplementedError

    @abc.abstractmethod
    def play_next(self):
        raise NotImplementedError

    @abc.abstractmethod
    def toggle_play(self):
        raise NotImplementedError

    @abc.abstractmethod
    def resume(self):
        raise NotImplementedError

    @abc.abstractmethod
    def play_from_playlist(self, playlist_uri, track_uri, device_id=None):
        raise NotImplementedError

    @abc.abstractmethod
    def play_from_show(self, show_uri, episode_uri, device_id=None):
        raise NotImplementedError

    @abc.abstractmethod
    def play_artist(self, artist_uri):
        raise NotImplementedError

    @abc.abstractmethod
    def update_status(self) -> NowPlayingItem:
        raise NotImplementedError
