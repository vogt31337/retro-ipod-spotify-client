class config:
    SCALE = 1
    TEXT_TRUNCATION = 25

    LARGEFONT = ("ChicagoFLF", int(72 * SCALE))
    MED_FONT = ("ChicagoFLF", int(52 * SCALE))

    SPOT_GREEN = "#1DB954"
    SPOT_BLACK = "#191414"
    SPOT_WHITE = "#FFFFFF"

    UDP_IP = "127.0.0.1"
    UDP_PORT = 9090

    DIVIDER_HEIGHT = 3

    # UP_KEY_CODE = 8255233 if platform == "darwin" else 111
    UP_KEY_CODE = 40
    # DOWN_KEY_CODE = 8320768 if platform == "darwin" else 116
    DOWN_KEY_CODE = 38
    # LEFT_KEY_CODE = 8124162 if platform == "darwin" else 113
    LEFT_KEY_CODE = 37
    # RIGHT_KEY_CODE = 8189699 if platform == "darwin" else 114
    RIGHT_KEY_CODE = 39
    # PREV_KEY_CODE = 2818092 if platform == "darwin" else 0
    PREV_KEY_CODE = 17
    # NEXT_KEY_CODE = 3080238 if platform == "darwin" else 0
    NEXT_KEY_CODE = 18
    # PLAY_KEY_CODE = 3211296 if platform == "darwin" else 0
    PLAY_KEY_CODE = 13

    EXIT_KEY_CODE = 27

    SCREEN_TIMEOUT_SECONDS = 60

    MENU_PAGE_SIZE = 6

    # Screen render types
    MENU_RENDER_TYPE = 0
    NOW_PLAYING_RENDER = 1
    SEARCH_RENDER = 2

    # Menu line item types
    LINE_NORMAL = 0
    LINE_HIGHLIGHT = 1
    LINE_TITLE = 2

    MPD_URL = "127.0.0.1"
    MPD_PORT = 6600
    MPD_PW = None
