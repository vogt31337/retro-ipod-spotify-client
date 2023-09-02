import tkinter as tk
from config import config
from nowplaying import NowPlayingCommand, NowPlayingPage
from view_model import PlaceHolderPage, InMemoryPlaylistPage, MenuPage
import spotify_manager


class SearchFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=config.SPOT_BLACK)
        self.header_label = tk.Label(self, text ="Search", font = config.LARGEFONT, background=config.SPOT_BLACK, foreground=config.SPOT_GREEN)
        self.header_label.grid(sticky='we', padx=(0, 10))
        self.grid_columnconfigure(0, weight=1)
        divider = tk.Canvas(self)
        divider.configure(bg=config.SPOT_GREEN, height=config.DIVIDER_HEIGHT, bd=0, highlightthickness=0, relief='ridge')
        divider.grid(row = 1, column = 0, sticky ="we", pady=(10, int(160 * config.SCALE)), padx=(10, 30))
        contentFrame = tk.Canvas(self, bg=config.SPOT_BLACK, highlightthickness=0, relief='ridge')
        contentFrame.grid(row = 2, column = 0, sticky ="nswe")
        self.query_label = tk.Label(contentFrame, text ="", font = config.LARGEFONT, background=config.SPOT_BLACK, foreground=config.SPOT_GREEN)
        self.letter_label= tk.Label(contentFrame, text ="a", font = config.LARGEFONT, background=config.SPOT_GREEN, foreground=config.SPOT_BLACK)
        self.query_label.grid(row = 0, column = 0, sticky = "nsw", padx=(120,0))
        self.letter_label.grid(row = 0, column = 1, sticky = "nsw")
        contentFrame.grid_columnconfigure(1, weight=1)
        search_line = tk.Canvas(self)
        search_line.configure(bg=config.SPOT_GREEN, height=5, bd=0, highlightthickness=0, relief='ridge')
        search_line.grid(row = 3, column = 0, sticky ="we", pady=10, padx=120)
        self.loading_label = tk.Label(self, text ="", font = config.LARGEFONT, background=config.SPOT_BLACK, foreground=config.SPOT_WHITE)
        self.loading_label.grid(row = 4, column = 0, sticky ="we", pady=(int(100 * config.SCALE), 0))

    def update_search(self, query, active_char, loading):
        self.query_label.configure(text=query)
        self.letter_label.configure(text=active_char)
        loading_text = "Loading..." if loading else ""
        self.loading_label.configure(text=loading_text)


class SearchRendering:
    def __init__(self, query, active_char):
        # super().__init__(config.SEARCH_RENDER)
        self.type = config.SEARCH_RENDER
        self.query = query
        self.active_char = active_char
        self.loading = False
        self.callback = None
        self.results = None

    def get_active_char(self):
        return ' ' if self.active_char == 26 else chr(self.active_char + ord('a'))

    def subscribe(self, app, callback):
        if callback == self.callback:
            return
        new_callback = self.callback is None
        self.callback = callback
        self.app = app
        if new_callback:
            self.refresh()

    def refresh(self):
        if not self.callback:
            return
        self.callback(self.query, self.get_active_char(), self.loading, self.results)
        self.results = None

    def unsubscribe(self):
        # super().unsubscribe()
        self.callback = None
        self.app = None


class SearchResultsPage(MenuPage):
    def __init__(self, previous_page, results):
        super().__init__("Search Results", previous_page, has_sub_page=True)
        self.results = results
        tracks, albums, artists = len(results.tracks), len(results.albums), len(results.artists)
        # Add 1 to each count (if > 0) to make room for section header line items
        self.tracks = tracks + 1 if tracks > 0 else 0
        self.artists = artists + 1 if artists > 0 else 0
        self.albums = albums + 1 if albums > 0 else 0
        self.total_count = self.tracks + self.albums + self.artists
        self.index = 1
        # indices of the section header line items
        self.header_indices = [0, self.tracks, self.artists + self.tracks]

    def total_size(self):
        return self.total_count

    def page_at(self, index):
        if self.tracks > 0 and index == 0:
            return PlaceHolderPage("TRACKS", self, has_sub_page=False, is_title=True)
        elif self.artists > 0 and index == self.header_indices[1]:
            return PlaceHolderPage("ARTISTS", self, has_sub_page=False, is_title=True)
        elif self.albums > 0 and index == self.header_indices[2]:
            return PlaceHolderPage("ALBUMS", self, has_sub_page=False, is_title=True)
        elif self.tracks > 0 and index < self.header_indices[1]:
            track = self.results.tracks[index - 1]
            command = NowPlayingCommand(lambda: spotify_manager.play_track(track.uri))
            return NowPlayingPage(self, track.title, command, datastore)
        elif self.albums > 0 and index < self.header_indices[2]:
            artist = self.results.artists[index - (self.tracks + 1)]
            command = NowPlayingCommand(lambda: spotify_manager.play_artist(artist.uri))
            return NowPlayingPage(self, artist.name, command, datastore)
        else:
            album = self.results.albums[index - (self.artists + self.tracks + 1)]
            tracks = self.results.album_track_map[album.uri]
            return InMemoryPlaylistPage(album, tracks, self)

    def get_index_jump_up(self):
        if self.index + 1 in self.header_indices:
            return 2
        return 1

    def get_index_jump_down(self):
        if self.index - 1 in self.header_indices:
            return 2
        return 1


class SearchPage():
    def __init__(self, previous_page):
        self.header = "Search"
        self.has_sub_page = True
        self.previous_page = previous_page
        self.live_render = SearchRendering("", 0)
        self.is_title = False

    def nav_prev(self):
        self.live_render.query = self.live_render.query[0:-1]
        self.live_render.refresh()

    def nav_next(self):
        if len(self.live_render.query) > 15:
            return
        active_char = ' ' if self.live_render.active_char == 26 \
            else chr(self.live_render.active_char + ord('a'))
        self.live_render.query += active_char
        self.live_render.refresh()

    def nav_play(self):
        pass

    def nav_up(self):
        self.live_render.active_char += 1
        if self.live_render.active_char > 26:
            self.live_render.active_char = 0
        self.live_render.refresh()

    def nav_down(self):
        self.live_render.active_char -= 1
        if self.live_render.active_char < 0:
            self.live_render.active_char = 26
        self.live_render.refresh()

    def run_search(self, query):
        self.live_render.loading = True
        self.live_render.refresh()
        self.live_render.results = spotify_manager.search(query)
        self.live_render.loading = False
        self.live_render.refresh()

    def nav_select(self):
        spotify_manager.run_async(lambda: self.run_search(self.live_render.query))
        return self

    def nav_back(self):
        return self.previous_page

    def render(self):
        return self.live_render

