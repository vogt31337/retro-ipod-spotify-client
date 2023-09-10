import tkinter as tk
import socket
import time
from select import select
from sys import platform
import os

import datastore
from config import config
from startpage import StartPage
from view_model import MenuPage
from search import SearchFrame, SearchResultsPage, SearchPage
from nowplaying import NowPlayingFrame, NowPlayingPage, NowPlayingCommand
from spotify_pages import RootPage as SpotifyPage
from mpd_pages import RootPage as MPDPage
from status import RootPage as StatusPage

wheel_position = -1
last_button = -1

last_interaction = time.time()
screen_on = True


DATASTORE = datastore.Datastore()


def screen_sleep():
    global screen_on
    screen_on = False
    os.system('xset -display :0 dpms force off')


def screen_wake():
    global screen_on
    screen_on = True
    os.system('xset -display :0 dpms force on')


class tkinterApp(tk.Tk):
    # __init__ function for class tkinterApp  
    def __init__(self, *args, **kwargs):
        # __init__ function for class Tk 
        tk.Tk.__init__(self, *args, **kwargs)

        if platform == 'darwin':
            self.geometry("320x240")
            config.SCALE = 0.3
        else:
            self.attributes('-fullscreen', True)
            config.SCALE = self.winfo_screenheight() / 930

        config.LARGEFONT = ("ChicagoFLF", int(72 * config.SCALE))
        config.MED_FONT = ("ChicagoFLF", int(52 * config.SCALE))
        # creating a container 
        container = tk.Frame(self)   
        container.pack(side = "top", fill = "both", expand = True)  
   
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
   
        # initializing frames to an empty array 
        self.frames = {}   
   
        # iterating through a tuple consisting 
        # of the different page layouts 
        for F in (StartPage, NowPlayingFrame, SearchFrame): 
   
            frame = F(container, self) 
   
            # initializing frame of that object from 
            # startpage, page1, page2 respectively with  
            # for loop 
            self.frames[F] = frame  
   
            frame.grid(row = 0, column = 0, sticky ="nsew") 
   
        self.show_frame(StartPage) 
   
    # to display the current frame passed as 
    # parameter 
    def show_frame(self, cont): 
        frame = self.frames[cont] 
        frame.tkraise() 


def processInput(app, input):
    global wheel_position, last_button, last_interaction
    position = input[2]
    button = input[0]
    button_state = input[1]
    if button == 29 and button_state == 0:
        wheel_position = -1
    elif wheel_position == -1:
        wheel_position = position
    elif position % 2 != 0:
        pass
    elif wheel_position <= 1 and position > 44:
        onDownPressed()
        wheel_position = position
    elif wheel_position >= 44 and position < 1:
        onUpPressed()
        wheel_position = position
    elif abs(wheel_position - position) > 6:
        wheel_position = -1
    elif wheel_position > position:
        onDownPressed()
        wheel_position = position
    elif wheel_position < position:
        onUpPressed()
        wheel_position = position
    
    if button_state == 0:
        last_button = -1
    elif button == last_button:
        pass
    elif button == 7:
        onSelectPressed()
        last_button = button
    elif button == 11:
        onBackPressed()
        last_button = button
    elif button == 10:
        onPlayPressed()
        last_button = button
    elif button == 8:
        onNextPressed()
        last_button = button
    elif button == 9:
        onPrevPressed()
        last_button = button
    
    now = time.time()
    if now - last_interaction > config.SCREEN_TIMEOUT_SECONDS:
        print("waking")
        screen_wake()
    last_interaction = now

    # app.frames[StartPage].set_list_item(0, "Test") 


def onKeyPress(event):
    c = event.keycode
    if c == config.UP_KEY_CODE:
        onUpPressed()
    elif c == config.DOWN_KEY_CODE:
        onDownPressed()
    elif c == config.RIGHT_KEY_CODE:
        onSelectPressed()
    elif c == config.LEFT_KEY_CODE:
        onBackPressed()
    elif c == config.NEXT_KEY_CODE:
        onNextPressed()
    elif c == config.PREV_KEY_CODE:
        onPrevPressed()
    elif c == config.PLAY_KEY_CODE:
        onPlayPressed()
    elif c == config.EXIT_KEY_CODE:
        exit()
    else:
        print("unrecognized key: ", c)


def update_search(q, ch, loading, results):
    global app, page
    search_page = app.frames[SearchFrame]
    if results is not None:
        page.render().unsubscribe()
        page = SearchResultsPage(page, results, DATASTORE)
        render(app, page.render())
    else:
        search_page.update_search(q, ch, loading)


def render_search(app, search_render):
    app.show_frame(SearchFrame)
    search_render.subscribe(app, update_search)


def render_menu(app, menu_render):
    app.show_frame(StartPage)
    page = app.frames[StartPage]
    if menu_render.total_count > config.MENU_PAGE_SIZE:
        page.show_scroll(menu_render.page_start, menu_render.total_count)
    else:
        page.hide_scroll()
    for (i, line) in enumerate(menu_render.lines):
        page.set_list_item(i, text=line.title, line_type = line.line_type, show_arrow = line.show_arrow) 
    page.set_header(menu_render.header, menu_render.now_playing, menu_render.has_internet)


def update_now_playing(now_playing):
    frame = app.frames[NowPlayingFrame]
    frame.update_now_playing(now_playing)


def render_now_playing(app, now_playing_render):
    app.show_frame(NowPlayingFrame)
    now_playing_render.subscribe(app, update_now_playing)


def render(app, render):
    if render.type == config.MENU_RENDER_TYPE:
        render_menu(app, render)
    elif render.type == config.NOW_PLAYING_RENDER:
        render_now_playing(app, render)
    elif render.type == config.SEARCH_RENDER:
        render_search(app, render)


def onPlayPressed():
    global page, app
    page.nav_play()
    render(app, page.render())


def onSelectPressed():
    global page, app
    if not page.has_sub_page:
        return
    page.render().unsubscribe()
    page = page.nav_select()
    render(app, page.render())


def onBackPressed():
    global page, app
    previous_page = page.nav_back()
    if previous_page:
        page.render().unsubscribe()
        page = previous_page
        render(app, page.render())


def onNextPressed():
    global page, app
    page.nav_next()
    render(app, page.render())


def onPrevPressed():
    global page, app
    page.nav_prev()
    render(app, page.render())


def onUpPressed():
    global page, app
    page.nav_up()
    render(app, page.render())


def onDownPressed():
    global page, app
    page.nav_down()
    render(app, page.render())


def app_main_loop():
    global app, page, loop_count, last_interaction, screen_on
    try:
        read_sockets = select(socket_list, [], [], 0)[0]
        for socket in read_sockets:
            data = socket.recv(128)
            processInput(app, data)
        loop_count += 1
        if loop_count >= 300:
            if time.time() - last_interaction > config.SCREEN_TIMEOUT_SECONDS and screen_on:
                screen_sleep()
            render(app, page.render())
            loop_count = 0
    except:
        pass
    finally:
        app.after(2, app_main_loop)


class RootPage(MenuPage):
    def __init__(self, previous_page):
        super().__init__("PiPod", previous_page, has_sub_page=True, datastore=DATASTORE)
        self.pages: list = [
            SpotifyPage(self, datastore=DATASTORE),
            MPDPage(self, datastore=DATASTORE),
            SearchPage(self),
            StatusPage(self, datastore=DATASTORE),
            NowPlayingPage(self, "Now Playing", None, DATASTORE)
        ]
        self.index = 0
        self.page_start = 0

    def get_pages(self):
        return self.pages

    def total_size(self):
        return len(self.get_pages())

    def page_at(self, index):
        return self.get_pages()[index]


if __name__ == '__main__':
    # Driver Code
    page = RootPage(None)
    app = tkinterApp()
    render(app, page.render())
    app.overrideredirect(True)
    app.overrideredirect(False)
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((config.UDP_IP, config.UDP_PORT))
    sock.setblocking(0)
    socket_list = [sock]
    loop_count = 0

    # --- start ---
    app.bind('<KeyPress>', onKeyPress)
    app.after(5, app_main_loop)
    app.mainloop()
