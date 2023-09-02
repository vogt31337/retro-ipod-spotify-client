import mpd
# from mpd.asyncio import MPDClient
from config import config
from PlayerInterface import FormalPlayerInterface


class mpd_manager(FormalPlayerInterface):
    def __init__(self, datastore=None):
        # self.client = MPDClient()
        self.client = mpd.MPDClient()
        self.datastore = datastore
        pass

    def set_datastore(self, datastore):
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
        return self.client.listplaylist(playlist)

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
        raise NotImplementedError

    def play_from_show(self, show_uri, episode_uri, device_id=None):
        raise NotImplementedError
