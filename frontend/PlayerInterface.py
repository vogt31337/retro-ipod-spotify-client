import abc


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