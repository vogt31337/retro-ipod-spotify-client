import re as re
from functools import lru_cache
from view_model import MenuPage, LineItem
from nowplaying import NowPlayingPage, NowPlayingCommand
from config import config
from mpd_manager import mpd_manager


class SingleArtistTrackPage(MenuPage):
    def __init__(self, track, previous_page, datastore):
        # Credit for code to remove emoticons from string: https://stackoverflow.com/a/49986645
        regex_pattern = re.compile(pattern="["
                                           u"\U0001F600-\U0001F64F"  # emoticons
                                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                           "]+", flags=re.UNICODE)

        super().__init__(regex_pattern.sub(r'', track['title']), previous_page, has_sub_page=True, datastore=datastore)
        self.track = track

    def page_content(self, index):
        element = list(self.track.items())[index]
        return LineItem(element[0] + ': ' + element[1])

    def total_size(self):
        return len(self.track.items())

    # def page_at(self, index):
    #     if type(self.datastore.current_player) is not mpd_manager:
    #         self.datastore.current_player = mpd_manager()
    #
    #     command = NowPlayingCommand(lambda: self.datastore.current_player.play_from_playlist(None,
    #                                                                                          self.track['file'],
    #                                                                                          None))
    #     return NowPlayingPage(self, self.track['title'], command, self.datastore)


class SingleArtistPage(MenuPage):
    def __init__(self, artist, previous_page, datastore):
        # Credit for code to remove emoticons from string: https://stackoverflow.com/a/49986645
        regex_pattern = re.compile(pattern="["
                                           u"\U0001F600-\U0001F64F"  # emoticons
                                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                           "]+", flags=re.UNICODE)

        super().__init__(regex_pattern.sub(r'', artist), previous_page, has_sub_page=True, datastore=datastore)
        self.artist = artist
        self.tracks = None

    def get_tracks(self):
        if self.tracks is None:
            self.tracks = self.datastore.current_player.getArtist(self.artist)
        return self.tracks

    def total_size(self):
        return len(self.get_tracks())

    def page_at(self, index):
        track = self.get_tracks()[index]
        if type(self.datastore.current_player) is not mpd_manager:
            self.datastore.current_player = mpd_manager()

        #command = NowPlayingCommand(lambda: self.datastore.current_player.play_from_playlist(self.playlist.uri, track.uri, None))
        #return NowPlayingPage(self, track['title'], command, self.datastore)
        return SingleArtistTrackPage(track, self, self.datastore)


class ArtistsPage(MenuPage):
    def __init__(self, previous_page, datastore):
        super().__init__("Artists", previous_page, has_sub_page=True, datastore=datastore)
        self.artists = self.get_content()

    def total_size(self):
        return len(self.artists)

    def get_content(self):
        return self.datastore.current_player.getArtists()

    @lru_cache(maxsize=15)
    def page_at(self, index):
        return SingleArtistPage(self.artists[index]['artist'], self, self.datastore)

    #def page_at(self, index):
        # play track
        #if type(self.datastore.current_player) is not mpd_manager:
        #    self.datastore.current_player = mpd_manager()
        #artist = self.datastore.current_player.getArtist(index)
        #command = NowPlayingCommand(lambda: self.datastore.current_player.play_artist(artist.uri))
        #return NowPlayingPage(self, artist.name, command, self.datastore)


class SinglePlaylistPage(MenuPage):
    def __init__(self, playlist, previous_page, datastore):
        # Credit for code to remove emoticons from string: https://stackoverflow.com/a/49986645
        regex_pattern = re.compile(pattern="["
                                           u"\U0001F600-\U0001F64F"  # emoticons
                                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                           "]+", flags=re.UNICODE)

        super().__init__(regex_pattern.sub(r'', playlist['title']), previous_page, has_sub_page=True, datastore=datastore)
        self.playlist = playlist
        self.tracks = None

    def get_tracks(self):
        if self.tracks is None:
            self.tracks = self.datastore.current_player.listplaylist(self.playlist.uri)
        return self.tracks

    def total_size(self):
        return self.playlist.track_count

    def page_at(self, index):
        track = self.get_tracks()[index]
        if type(self.datastore.current_player) is not mpd_manager:
            self.datastore.current_player = mpd_manager()

        command = NowPlayingCommand(lambda: self.datastore.current_player.play_from_playlist(self.playlist.uri, track.uri, None))
        return NowPlayingPage(self, track.title, command, self.datastore)


class PlaylistsPage(MenuPage):

    def __init__(self, previous_page, datastore=None):
        super().__init__(self.get_title(), previous_page, has_sub_page=True, datastore=datastore)
        self.playlists = self.get_content()
        # self.num_playlists = len(self.playlists)
        self.playlists.sort(key=self.get_idx)  # sort playlists to keep order as arranged in Spotify library

    def get_title(self):
        return "Playlists"

    def get_content(self):
        return self.datastore.current_player.listplaylists()

    def get_idx(self, e):  # function to get idx from UserPlaylist for sorting
        #if type(e) == spotify_manager.UserPlaylist:  # self.playlists also contains albums as it seems and they don't have the idx value
        #    return e.idx
        #else:
        #    return 0
        return 0

    def total_size(self):
        return len(self.playlists)

    @lru_cache(maxsize=15)
    def page_at(self, index):
        return SinglePlaylistPage(self.playlists[index], self, self.datastore)


class AlbumsPage(PlaylistsPage):
    def __init__(self, previous_page, datastore):
        super().__init__(previous_page, datastore=datastore)

    def get_title(self):
        return "Albums"

    def get_content(self):
        return self.datastore.current_player.getAllAlbums()


class ConfigEditPage(MenuPage):
    def __init__(self, title, previous_page, datastore):
        super().__init__(title, previous_page, datastore=datastore, has_sub_page=False)


class ConfigPage(MenuPage):
    def __init__(self, previous_page, datastore):
        super().__init__(self.get_title(), previous_page, datastore=datastore, has_sub_page=True)

    def get_title(self):
        return "MPD Config"

    def total_size(self):
        return 3

    def page_content(self, index):
        if index == 0:
            return LineItem("IP: " + str(config.MPD_URL))
        if index == 1:
            return LineItem("Port: " + str(config.MPD_PORT))
        if index == 2:
            return LineItem("PW: " + str(config.MPD_PW))

    # def page_at(self, index):
    #     if index == 0:
    #         return ConfigEditPage("IP: " + str(config.MPD_URL), config.MPD_URL)
    #     if index == 1:
    #         return ConfigEditPage("Port: " + str(config.MPD_PORT), config.MPD_PORT)
    #     if index == 2:
    #         return ConfigEditPage("PW: " + str(config.MPD_PW), config.MPD_PW)


class RootPage(MenuPage):
    def __init__(self, previous_page, datastore):
        super().__init__("MPD", previous_page, has_sub_page=True, datastore=datastore)
        self.datastore.current_player = mpd_manager()
        self.pages = [
            ArtistsPage(self, datastore),
            # AlbumsPage(self, datastore=datastore),
            # NewReleasesPage(self),
            PlaylistsPage(self, datastore=datastore),
            # ShowsPage(self),
            # SearchPage(self),
            ConfigPage(self, datastore=datastore),
            NowPlayingPage(self, "Now Playing", NowPlayingCommand(), datastore)
        ]
        self.index = 0
        self.page_start = 0

    def get_pages(self):
        if not self.datastore.now_playing:
            return self.pages[0:-1]
        return self.pages

    def total_size(self):
        return len(self.get_pages())

    def page_at(self, index):
        return self.get_pages()[index]
