import tkinter as tk
from PIL import ImageTk, Image
from config import config
from flattenAlpha import flattenAlpha
from nowplaying import NowPlayingItem


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.green_arrow_image = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_arrow_grn.png')))
        self.black_arrow_image = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_arrow_blk.png')))
        self.empty_arrow_image = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_arrow_empty.png')))
        self.play_image = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_play.png')))
        self.pause_image = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_pause.png')))
        self.space_image = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_space.png')))
        self.stop_image =  ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_stop.png')))
        self.wifi_image = ImageTk.PhotoImage(flattenAlpha(Image.open('assets/pod_wifi.png')))
        self.configure(bg=config.SPOT_BLACK)
        header_container = tk.Canvas(self, bg=config.SPOT_BLACK, highlightthickness=0, relief='ridge')
        header_container.grid(sticky='we')
        self.header_label = tk.Label(header_container, text="PiPod", font=config.LARGEFONT, background=config.SPOT_BLACK,
                                     foreground=config.SPOT_GREEN)
        self.header_label.grid(sticky='we', column=1, row=0, padx=(0, 10))
        self.play_indicator = tk.Label(header_container, image=self.space_image, background=config.SPOT_BLACK)
        self.play_indicator.grid(sticky='w', column=0, row=0, padx=(70 * config.SCALE, 0))
        self.wifi_indicator = tk.Label(header_container, image=self.space_image, background=config.SPOT_BLACK)
        self.wifi_indicator.grid(sticky='w', column=2, row=0, padx=(0, 90 * config.SCALE))
        header_container.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        divider = tk.Canvas(self)
        divider.configure(bg=config.SPOT_GREEN, height=config.DIVIDER_HEIGHT, bd=0, highlightthickness=0, relief='ridge')
        divider.grid(row=1, column=0, sticky="we", pady=10, padx=(10, 30))
        contentFrame = tk.Canvas(self, bg=config.SPOT_BLACK, highlightthickness=0, relief='ridge')
        contentFrame.grid(row=2, column=0, sticky="nswe")
        self.grid_rowconfigure(2, weight=1)
        listFrame = tk.Canvas(contentFrame)
        listFrame.configure(bg=config.SPOT_BLACK, bd=0, highlightthickness=0)
        listFrame.grid(row=0, column=0, sticky="nsew")
        contentFrame.grid_rowconfigure(0, weight=1)
        contentFrame.grid_columnconfigure(0, weight=1)

        # scrollbar
        self.scrollFrame = tk.Canvas(contentFrame)
        self.scrollFrame.configure(bg=config.SPOT_BLACK, width=int(50 * config.SCALE), bd=0, highlightthickness=4,
                                   highlightbackground=config.SPOT_GREEN)
        self.scrollBar = tk.Canvas(self.scrollFrame, bg=config.SPOT_GREEN, highlightthickness=0, width=int(20 * config.SCALE))
        self.scrollBar.place(in_=self.scrollFrame, relx=.5, y=int(10 * config.SCALE), anchor="n", relwidth=.6, relheight=.9)
        self.scrollFrame.grid(row=0, column=1, sticky="ns", padx=(0, 30), pady=(0, 10))

        self.listItems = []
        self.arrows = []
        for x in range(6):
            item = tk.Label(listFrame, text=" " + str(x), justify=tk.LEFT, anchor="w", font=config.LARGEFONT,
                            background=config.SPOT_BLACK, foreground=config.SPOT_GREEN, padx=(30 * config.SCALE))
            imgLabel = tk.Label(listFrame, image=self.green_arrow_image, background=config.SPOT_BLACK)
            imgLabel.image = self.green_arrow_image
            imgLabel.grid(row=x, column=1, sticky="nsw", padx=(0, 30))
            item.grid(row=x, column=0, sticky="ew", padx=(10, 0))
            self.listItems.append(item)
            self.arrows.append(imgLabel)
        listFrame.grid_columnconfigure(0, weight=1)
        # listFrame.grid_columnconfigure(1, weight=1)

    def show_scroll(self, index, total_count):
        scroll_bar_y_rel_size = max(0.9 - (total_count - config.MENU_PAGE_SIZE) * 0.06, 0.03)
        scroll_bar_y_raw_size = scroll_bar_y_rel_size * self.scrollFrame.winfo_height()
        percentage = index / (total_count - 1)
        offset = ((1 - percentage) * (scroll_bar_y_raw_size + int(20 * config.SCALE))) - (
                    scroll_bar_y_raw_size + int(10 * config.SCALE))
        self.scrollBar.place(in_=self.scrollFrame, relx=.5, rely=percentage, y=offset, anchor="n", relwidth=.66,
                             relheight=scroll_bar_y_rel_size)
        self.scrollFrame.grid(row=0, column=1, sticky="ns", padx=(0, 30), pady=(0, 10))

    def hide_scroll(self):
        self.scrollFrame.grid_forget()

    def set_header(self, header, now_playing: NowPlayingItem=None, has_wifi=False):
        truncd_header = header if len(header) < 20 else header[0:17] + "..."
        self.header_label.configure(text=truncd_header)
        play_image = self.space_image
        if now_playing is not None:
            if now_playing.state == 'play':
                play_image = self.play_image
            elif now_playing.state == 'pause':
                play_image = self.pause_image
            elif now_playing.state == 'stop':
                play_image = self.stop_image
            # play_image = self.play_image if now_playing.is_playing else self.pause_image
        self.play_indicator.configure(image=play_image)
        self.play_indicator.image = play_image
        wifi_image = self.wifi_image if has_wifi else self.space_image
        self.wifi_indicator.configure(image=wifi_image)
        self.wifi_indicator.image = wifi_image

    def set_list_item(self, index, text, line_type=config.LINE_NORMAL, show_arrow=False):
        bgColor = config.SPOT_GREEN if line_type == config.LINE_HIGHLIGHT else config.SPOT_BLACK
        txtColor = config.SPOT_BLACK if line_type == config.LINE_HIGHLIGHT else \
            (config.SPOT_GREEN if line_type == config.LINE_NORMAL else config.SPOT_WHITE)
        # TODO make text dynamically scrolling!
        truncd_text = text if len(text) < config.TEXT_TRUNCATION else text[0:config.TEXT_TRUNCATION-2] + "..."
        self.listItems[index].configure(background=bgColor, foreground=txtColor, text=truncd_text)
        arrow = self.arrows[index]
        arrow.grid(row=index, column=1, sticky="nsw", padx=(0, 30))
        arrowImg = self.empty_arrow_image if not show_arrow else \
            (self.black_arrow_image if line_type == config.LINE_HIGHLIGHT else self.green_arrow_image)
        arrow.configure(background=bgColor, image=arrowImg)
        arrow.image = arrowImg

