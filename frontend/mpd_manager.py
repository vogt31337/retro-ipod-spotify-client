import mpd
import time
from datastore import Datastore
from config import config
from PlayerInterface import FormalPlayerInterface, NowPlayingItem


def track_to_nowplaying(track, state, playlist_name='', progress=0., timestamp=time.time()) -> NowPlayingItem:
    context_name = playlist_name
    timestamp = timestamp
    duration = float(track['duration'])
    track_index = -1
    track_total = 0

    title = track['file']
    if 'title' in track:
        title = track['title']

    artist = 'Unknown artist'
    if 'artist' in track:
        artist = track['artist']

    album = 'Unknown album'
    if 'album' in track:
        album = track['album']

    is_repeat = False
    if 'repeat' in track and track['repeat'] == '1':
        is_repeat = True

    is_random = False
    if 'random' in track and track['random'] == '1':
        is_random = True

    is_single = False
    if 'single' in track and track['single'] == '1':
        is_single = True

    name = title
    return NowPlayingItem(name=name,
                          artist=artist,
                          album=album,
                          context_name=context_name,
                          state=state,
                          timestamp=timestamp,
                          progress=progress,
                          duration=duration,
                          track_index=track_index,
                          track_total=track_total,
                          is_repeat=is_repeat,
                          is_random=is_random,
                          is_single=is_single)


class mpd_manager(FormalPlayerInterface):
    def __init__(self, datastore: Datastore = None):
        # self.client = MPDClient()
        self.client: mpd.MPDClient = mpd.MPDClient()
        self.datastore: Datastore = datastore
        self.current_playlist: list = None
        self.current_playlist_name: str = 'Queue'

    def set_datastore(self, datastore: Datastore):
        self.datastore = datastore

    def check_mpd_connected(self):
        """
        Check if the async mpd client is connected, and connect if not.
        :return:
        """
        # if not self.client.connected:
        #     await self.client.connect(config.MPD_URL, config.MPD_PORT)
        try:
            self.client.connect(config.MPD_URL, config.MPD_PORT)
        except mpd.base.ConnectionError:
            pass

    def listplaylist(self, playlist):
        """
        Returns a list of the songs in the playlist.
        :param playlist:
        :return:
        """
        self.check_mpd_connected()
        self.current_playlist = self.client.listplaylistinfo(playlist)
        self.current_playlist_name = playlist
        return self.current_playlist

    def getArtist(self, name):
        """
        Get everything from this artist
        :param name:
        :return:
        """
        self.check_mpd_connected()
        return self.client.find('artist', name)

    def getArtists(self):
        """
        Function to return all artists from db
        :return:
        """
        self.check_mpd_connected()
        return self.client.list('artist')

    def play_artist(self, artist):
        """
        Create a playlist from all titles of this artist and play the first song
        :param artist:
        :return:
        """
        raise NotImplementedError

    def listplaylists(self):
        """
        List all available playlists
        :return:
        """
        self.check_mpd_connected()
        return self.client.listplaylists()

    def getAllAlbums(self):
        self.check_mpd_connected()
        return self.client.find('album', '')


    def play_previous(self):
        self.check_mpd_connected()
        self.client.previous()

    def play_next(self):
        self.check_mpd_connected()
        self.client.next()

    def toggle_play(self):
        self.check_mpd_connected()
        self.client.pause()

    def play(self, song=0):
        self.check_mpd_connected()
        self.client.play(song)

    def resume(self):
        self.check_mpd_connected()
        self.client.pause(1)

    def stop(self):
        self.check_mpd_connected()
        self.client.stop()

    def play_from_playlist(self, playlist_uri, track_uri, device_id=None):
        self.check_mpd_connected()
        self.client.load(playlist_uri)
        self.client.play(track_uri)

    def play_from_show(self, show_uri, episode_uri, device_id=None):
        raise NotImplementedError

    def update_status(self) -> NowPlayingItem:
        status = self.client.status()
        if not self.current_playlist:
            self.current_playlist = self.client.playlistinfo()
        track = self.current_playlist[int(status['song'])]

        time = 0.
        if 'time' in track:
            time = track['time']

        elapsed = -1.
        if 'elapsed' in status:
            elapsed = float(status['elapsed'])

        return track_to_nowplaying(track,
                                   playlist_name=self.current_playlist_name,
                                   progress=elapsed,
                                   timestamp=time,
                                   state=status['state'])