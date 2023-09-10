import re as re
from functools import lru_cache
from spotify_manager import spotify_manager
from view_model import MenuPage
from nowplaying import NowPlayingCommand, NowPlayingPage
from search import SearchPage

SPOTIFY_MANAGER = spotify_manager()


class ShowsPage(MenuPage):
    def __init__(self, previous_page):
        super().__init__(self.get_title(), previous_page, has_sub_page=True)
        self.shows = self.get_content()
        self.num_shows = len(self.shows)

    def get_title(self):
        return "Podcasts"

    def get_content(self):
        return SPOTIFY_MANAGER.datastore.getAllSavedShows()

    def total_size(self):
        return self.num_shows

    @lru_cache(maxsize=15)
    def page_at(self, index):
        return SingleShowPage(self.shows[index], self)


class PlaylistsPage(MenuPage):
    def __init__(self, previous_page, datastore):
        super().__init__(self.get_title(), previous_page, has_sub_page=True, datastore=datastore)
        self.playlists = self.get_content()
        self.num_playlists = len(self.playlists)
        self.playlists.sort(key=self.get_idx)  # sort playlists to keep order as arranged in Spotify library

    def get_title(self):
        return "Playlists"

    def get_content(self):
        return self.datastore.getAllSavedPlaylists()

    def get_idx(self, e):  # function to get idx from UserPlaylist for sorting
        if type(e) == spotify_manager.UserPlaylist:  # self.playlists also contains albums as it seems and they don't have the idx value
            return e.idx
        else:
            return 0

    def total_size(self):
        return self.num_playlists

    @lru_cache(maxsize=15)
    def page_at(self, index):
        return SinglePlaylistPage(self.playlists[index], self)


class AlbumsPage(PlaylistsPage):
    def __init__(self, previous_page, datastore):
        super().__init__(previous_page, datastore)

    def get_title(self):
        return "Albums"

    def get_content(self):
        # return self.datastore.getAllSavedAlbums()
        return SPOTIFY_MANAGER.datastore.getAllSavedAlbums()


class NewReleasesPage(PlaylistsPage):
    def __init__(self, previous_page, datastore):
        super().__init__(previous_page, datastore)

    def get_title(self):
        return "New Releases"

    def get_content(self):
        return SPOTIFY_MANAGER.datastore.getAllNewReleases()


class ArtistsPage(MenuPage):
    def __init__(self, previous_page, datastore):
        super().__init__("Artists", previous_page, has_sub_page=True)
        self.datastore = datastore

    def total_size(self):
        return self.datastore.getArtistCount()

    def page_at(self, index):
        # play track
        artist = self.datastore.getArtist(index)
        command = NowPlayingCommand(lambda: self.datastore.current_player.play_artist(artist.uri))
        self.datastore.current_player = SPOTIFY_MANAGER
        return NowPlayingPage(self, artist.name, command, self.datastore)


class SinglePlaylistPage(MenuPage):
    def __init__(self, playlist, previous_page, datastore):
        # Credit for code to remove emoticons from string: https://stackoverflow.com/a/49986645
        regex_pattern = re.compile(pattern="["
                                           u"\U0001F600-\U0001F64F"  # emoticons
                                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                           "]+", flags=re.UNICODE)

        super().__init__(regex_pattern.sub(r'', playlist.name), previous_page, has_sub_page=True)
        self.playlist = playlist
        self.tracks = None
        self.datastore = datastore

    def get_tracks(self):
        if self.tracks is None:
            self.tracks = SPOTIFY_MANAGER.datastore.getPlaylistTracks(self.playlist.uri)
        return self.tracks

    def total_size(self):
        return self.playlist.track_count

    def page_at(self, index):
        track = self.get_tracks()[index]
        command = NowPlayingCommand(lambda: self.datastore.current_player.play_from_playlist(self.playlist.uri, track.uri, None))
        self.datastore.current_player = SPOTIFY_MANAGER
        return NowPlayingPage(self, track.title, command, self.datastore)


class SingleShowPage(MenuPage):
    def __init__(self, show, previous_page, datastore):
        super().__init__(show.name, previous_page, has_sub_page=True)
        self.show = show
        self.episodes = None
        self.datastore = datastore

    def get_episodes(self):
        if self.episodes is None:
            self.episodes = SPOTIFY_MANAGER.datastore.getShowEpisodes(self.show.uri)
        return self.episodes

    def total_size(self):
        return self.show.episode_count

    def page_at(self, index):
        episode = self.get_episodes()[index]
        command = NowPlayingCommand(lambda: self.datastore.current_player.play_from_show(self.show.uri, episode.uri, None))
        self.datastore.current_player = SPOTIFY_MANAGER
        return NowPlayingPage(self, episode.name, command, self.datastore)


class SingleTrackPage(MenuPage):
    def __init__(self, track, previous_page, playlist=None, album=None):
        super().__init__(track.title, previous_page, has_sub_page=False)
        self.track = track
        self.playlist = playlist
        self.album = album

    def render(self):
        r = super().render()
        print("render track")
        context_uri = self.playlist.uri if self.playlist else self.album.uri
        spotify_manager.play_from_playlist(context_uri, self.track.uri, None)
        return r


class SingleEpisodePage(MenuPage):
    def __init__(self, episode, previous_page, show=None):
        super().__init__(episode.name, previous_page, has_sub_page=False)
        self.episode = episode
        self.show = show

    def render(self):
        r = super().render()
        print("render episode")
        context_uri = self.show.uri
        spotify_manager.play_from_show(context_uri, self.episode.uri, None)
        return r


class SavedTracksPage(MenuPage):
    def __init__(self, previous_page):
        super().__init__("Saved Tracks", previous_page, has_sub_page=True)

    def total_size(self):
        return SPOTIFY_MANAGER.datastore.getSavedTrackCount()

    def page_at(self, index):
        # play track
        return SingleTrackPage(SPOTIFY_MANAGER.datastore.getSavedTrack(index), self)


class RootPage(MenuPage):
    def __init__(self, previous_page, datastore=None):
        super().__init__("Spotify", previous_page, has_sub_page=True, datastore=datastore)
        SPOTIFY_MANAGER.set_datastore(datastore)
        self.pages = [
            ArtistsPage(self, datastore),
            AlbumsPage(self, datastore),
            NewReleasesPage(self, datastore),
            PlaylistsPage(self, datastore),
            ShowsPage(self),
            SearchPage(self),
            NowPlayingPage(self, "Now Playing", NowPlayingCommand(), datastore)
        ]
        self.index = 0
        self.page_start = 0

    def get_pages(self):
        if not SPOTIFY_MANAGER.datastore.now_playing:
            return self.pages[0:-1]
        return self.pages

    def total_size(self):
        return len(self.get_pages())

    def page_at(self, index):
        return self.get_pages()[index]

