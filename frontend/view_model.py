import re as re
from config import config
from nowplaying import NowPlayingPage, NowPlayingCommand
import threading


def run_async(self, fun):
    threading.Thread(target=fun, args=()).start()


class LineItem:
    def __init__(self, title="", line_type=config.LINE_NORMAL, show_arrow=False):
        self.title = title
        self.line_type = line_type
        self.show_arrow = show_arrow


class MenuRendering:
    def __init__(self, header="", lines=[], page_start=0, total_count=0):
        # super().__init__(config.MENU_RENDER_TYPE)
        self.type = config.MENU_RENDER_TYPE
        self.lines = lines
        self.header = header
        self.page_start = page_start
        self.total_count = total_count

        # TODO: Fix concept of now playing, since it will be able to hold more than just spoitfy
        # self.now_playing = spotify_manager.DATASTORE.now_playing
        self.now_playing = None

        # TODO: use a python library for stats and stuff
        # self.has_internet = spotify_manager.has_internet
        self.has_internet = False

    def unsubscribe(self):
        pass


class MenuPage:
    def __init__(self, header, previous_page, has_sub_page, is_title=False, datastore=None):
        self.index = 0
        self.page_start = 0
        self.header = header
        self.has_sub_page = has_sub_page
        self.previous_page = previous_page
        self.is_title = is_title
        self.datastore = datastore

    def total_size(self):
        return 0

    def page_at(self, index):
        return None

    def page_content(self, index):
        return None

    def nav_prev(self):
        run_async(lambda: self.datastore.current_player.play_previous())

    def nav_next(self):
        run_async(lambda: self.datastore.current_player.play_next())

    def nav_play(self):
        run_async(lambda: self.datastore.current_player.toggle_play())

    def get_index_jump_up(self):
        return 1

    def get_index_jump_down(self):
        return 1

    def nav_up(self):
        jump = self.get_index_jump_up()
        if self.index >= self.total_size() - jump:
            return
        if self.index >= self.page_start + config.MENU_PAGE_SIZE - jump:
            self.page_start = self.page_start + jump
        self.index = self.index + jump

    def nav_down(self):
        jump = self.get_index_jump_down()
        if self.index <= (jump - 1):
            return
        if self.index <= self.page_start + (jump - 1):
            self.page_start = self.page_start - jump
            if self.page_start == 1:
                self.page_start = 0
        self.index = self.index - jump

    def nav_select(self):
        return self.page_at(self.index)

    def nav_back(self):
        return self.previous_page

    def render(self):
        lines = []
        total_size = self.total_size()
        for i in range(self.page_start, self.page_start + config.MENU_PAGE_SIZE):
            if i < total_size:
                page = self.page_at(i)
                if page is not None:
                    line_type = config.LINE_TITLE if page.is_title else \
                        config.LINE_HIGHLIGHT if i == self.index else config.LINE_NORMAL
                    lines.append(LineItem(page.header, line_type, page.has_sub_page))
                else:
                    content = self.page_content(i)
                    if content is not None:
                        lines.append(content)
                    else:
                        lines.append(LineItem())
            else:
                lines.append(LineItem())

        return MenuRendering(lines=lines, header=self.header, page_start=self.index, total_count=total_size)


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
            self.tracks = self.datastore.getPlaylistTracks(self.playlist.uri)
        return self.tracks

    def total_size(self):
        return self.playlist.track_count

    def page_at(self, index):
        track = self.get_tracks()[index]
        command = NowPlayingCommand(lambda: self.datastore.current_player.play_from_playlist(self.playlist.uri, track.uri, None))
        return NowPlayingPage(self, track.title, command, self.datastore)


class SingleArtistPage(MenuPage):
    def __init__(self, artistName, previous_page):
        super().__init__(artistName, previous_page, has_sub_page=True)


class InMemoryPlaylistPage(SinglePlaylistPage):
    def __init__(self, playlist, tracks, previous_page):
        super().__init__(playlist, previous_page)
        self.tracks = tracks


class PlaceHolderPage(MenuPage):
    def __init__(self, header, previous_page, has_sub_page=True, is_title=False):
        super().__init__(header, previous_page, has_sub_page, is_title)
