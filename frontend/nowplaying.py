import tkinter as tk
from config import config
from PIL import ImageTk, Image
import time
from datetime import timedelta

from flattenAlpha import flattenAlpha
from marquee import Marquee
from PlayerInterface import FormalPlayerInterface
import threading


def run_async(self, fun):
    threading.Thread(target=fun, args=()).start()


class NowPlayingFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.inflated = False
        self.active = False
        self.update_time = False
        self.configure(bg=config.SPOT_BLACK)
        self.header_label = tk.Label(self, text="Now Playing", font=config.LARGEFONT, background=config.SPOT_BLACK,
                                     foreground=config.SPOT_GREEN)
        self.header_label.grid(sticky='we', padx=(0, 10))
        self.grid_columnconfigure(0, weight=1)
        divider = tk.Canvas(self)
        divider.configure(bg=config.SPOT_GREEN, height=config.DIVIDER_HEIGHT, bd=0, highlightthickness=0,
                          relief='ridge')
        divider.grid(row=1, column=0, sticky="we", pady=10, padx=(10, 30))
        contentFrame = tk.Canvas(self, bg=config.SPOT_BLACK, highlightthickness=0, relief='ridge')
        contentFrame.grid(row=2, column=0, sticky="nswe")
        contentFrame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.context_label = tk.Label(contentFrame, text="", font=config.MED_FONT, background=config.SPOT_BLACK,
                                      foreground=config.SPOT_GREEN)
        self.context_label.grid(row=0, column=0, sticky="w", padx=int(50 * config.SCALE))
        self.artist_label = tk.Label(contentFrame, text="", font=config.LARGEFONT, background=config.SPOT_BLACK,
                                     foreground=config.SPOT_GREEN)
        self.artist_label.grid(row=2, column=0, sticky="we", padx=(10, 30))
        self.album_label = tk.Label(contentFrame, text="", font=config.LARGEFONT, background=config.SPOT_BLACK,
                                    foreground=config.SPOT_GREEN)
        self.album_label.grid(row=3, column=0, sticky="we", padx=(10, 30))
        self.track_label = Marquee(contentFrame, text="")
        self.track_label.grid(row=1, column=0, sticky="we", padx=(30, 50))
        self.progress_frame = tk.Canvas(contentFrame, height=int(72 * config.SCALE), bg=config.SPOT_BLACK,
                                        highlightthickness=0)
        self.progress_frame.grid(row=4, column=0, sticky="we", pady=(int(52 * config.SCALE), 0), padx=(30, 50))
        self.frame_img = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/prog_frame.png')))
        self.time_frame = tk.Canvas(contentFrame, bg=config.SPOT_BLACK, highlightthickness=0)
        self.time_frame.grid(row=5, column=0, sticky="we", padx=0, pady=(10, 0))
        self.time_frame.grid_columnconfigure(0, weight=1)
        self.elapsed_time = tk.Label(self.time_frame, text="00:00", font=config.LARGEFONT, background=config.SPOT_BLACK,
                                     foreground=config.SPOT_GREEN)
        self.elapsed_time.grid(row=0, column=0, sticky="nw", padx=int(40 * config.SCALE))
        self.remaining_time = tk.Label(self.time_frame, text="-00:00", font=config.LARGEFONT,
                                       background=config.SPOT_BLACK, foreground=config.SPOT_GREEN)
        self.remaining_time.grid(row=0, column=1, sticky="ne", padx=int(60 * config.SCALE))
        self.cached_album = None
        self.cached_artist = None

    def update_now_playing(self, now_playing):
        if not self.inflated:
            parent_width = self.winfo_width()
            if parent_width > 2:
                self.midpoint = (parent_width / 2) - 40
                self.progress_width = self.frame_img.width()
                self.progress_start_x = self.midpoint - self.progress_width / 2
                self.progress = self.progress_frame.create_rectangle(self.progress_start_x, 0, self.midpoint,
                                                                     int(72 * config.SCALE), fill=config.SPOT_GREEN)
                self.progress_frame.create_image(self.midpoint, (self.frame_img.height() - 1) / 2, image=self.frame_img)
                self.inflated = True
        if not now_playing:
            return
        self.track_label.set_text(now_playing['name'])
        artist = now_playing['artist']
        if self.cached_artist != artist:
            truncd_artist = artist if len(artist) < 20 else artist[0:17] + "..."
            self.artist_label.configure(text=truncd_artist)
            self.cached_artist = artist
        album = now_playing['album']
        if self.cached_album != album:
            truncd_album = album if len(album) < 20 else album[0:17] + "..."
            self.album_label.configure(text=truncd_album)
            self.cached_album = album
        context_name = now_playing['context_name']
        truncd_context = context_name if context_name else "Now Playing"
        truncd_context = truncd_context if len(truncd_context) < 20 else truncd_context[0:17] + "..."
        self.header_label.configure(text=truncd_context)
        update_delta = 0 if not now_playing['is_playing'] else (time.time() - now_playing["timestamp"]) * 1000.0
        adjusted_progress_ms = now_playing['progress'] + update_delta
        adjusted_remaining_ms = max(0, now_playing['duration'] - adjusted_progress_ms)
        if self.update_time:
            progress_txt = ":".join(str(timedelta(milliseconds=adjusted_progress_ms)).split('.')[0].split(':')[1:3])
            remaining_txt = "-" + ":".join(
                str(timedelta(milliseconds=adjusted_remaining_ms)).split('.')[0].split(':')[1:3])
            self.elapsed_time.configure(text=progress_txt)
            self.remaining_time.configure(text=remaining_txt)
        self.update_time = not self.update_time
        if self.inflated:
            adjusted_progress_pct = min(1.0, adjusted_progress_ms / now_playing['duration'])
            self.progress_frame.coords(self.progress, self.progress_start_x, 0,
                                       self.progress_width * adjusted_progress_pct + self.progress_start_x,
                                       int(72 * config.SCALE))
        if (now_playing['track_index'] < 0):
            self.context_label.configure(text="")
            return
        context_str = str(now_playing['track_index']) + " of " + str(now_playing['track_total'])
        self.context_label.configure(text=context_str)


class NowPlayingPage:
    def __init__(self, previous_page, header, command, datastore):
        self.has_sub_page = False
        self.previous_page = previous_page
        self.command = command
        self.header = header
        self.live_render = NowPlayingRendering(datastore)
        self.is_title = False
        self.player: FormalPlayerInterface|None = datastore.current_player

    def play_previous(self):
        self.player.play_previous()
        self.live_render.refresh()

    def play_next(self):
        self.player.play_next()
        self.live_render.refresh()

    def toggle_play(self):
        self.player.toggle_play()
        self.live_render.refresh()

    def nav_prev(self):
        run_async(lambda: self.play_previous())

    def nav_next(self):
        run_async(lambda: self.play_next())

    def nav_play(self):
        run_async(lambda: self.toggle_play())

    def nav_up(self):
        pass

    def nav_down(self):
        pass

    def nav_select(self):
        return self

    def nav_back(self):
        return self.previous_page

    def render(self):
        if not self.command.has_run:
            self.command.run()
        return self.live_render


class NowPlayingRendering:
    def __init__(self, datastore):
        # super().__init__(config.NOW_PLAYING_RENDER)
        self.type = config.NOW_PLAYING_RENDER
        self.callback = None
        self.after_id = None
        self.datastore = datastore

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
        if self.after_id:
            self.app.after_cancel(self.after_id)
        self.callback(self.datastore.now_playing)
        self.after_id = self.app.after(500, lambda: self.refresh())

    def unsubscribe(self):
        # super().unsubscribe()
        self.callback = None
        self.app = None


class NowPlayingCommand:
    def __init__(self, runnable=lambda: ()):
        self.has_run = False
        self.runnable = runnable

    def run(self):
        self.has_run = True
        self.runnable()

