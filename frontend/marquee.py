import tkinter as tk

from config import config

class Marquee(tk.Canvas):
    def __init__(self, parent, text, margin=2, borderwidth=0, relief='flat', fps=24):
        tk.Canvas.__init__(self, parent, highlightthickness=0, borderwidth=borderwidth, relief=relief,
                           background=config.SPOT_BLACK)
        self.fps = fps
        self.margin = margin
        self.borderwidth = borderwidth
        # start by drawing the text off screen, then asking the canvas
        # how much space we need. Use that to compute the initial size
        # of the canvas.
        self.saved_text = text
        self.text = self.create_text(0, -1000, text=text, font=config.LARGEFONT, fill=config.SPOT_GREEN, anchor="w",
                                     tags=("text",))
        (x0, y0, x1, y1) = self.bbox("text")
        self.width = (x1 - x0) + (2 * margin) + (2 * borderwidth)
        self.height = (y1 - y0) + (2 * margin) + (2 * borderwidth)
        self.configure(width=self.width, height=self.height)
        self.reset = True
        self.pause_ctr = 100
        self.after_id = None
        self.redraw()

    def set_text(self, text):
        if (self.saved_text == text):
            return
        self.saved_text = text
        self.itemconfig(self.text, text=text)
        (x0, y0, x1, y1) = self.bbox("text")
        self.width = (x1 - x0) + (2 * self.margin) + (2 * self.borderwidth)
        self.height = (y1 - y0) + (2 * self.margin) + (2 * self.borderwidth)
        self.configure(width=self.width, height=self.height)
        if (self.width > self.winfo_width()):
            self.coords("text", 100, self.winfo_height() / 2)
        else:
            self.coords("text", (self.winfo_width() / 2) - (self.width / 2), self.winfo_height() / 2)
        self.pause_ctr = 100
        self.reset = True
        self.redraw()

    def redraw(self):
        if self.after_id:
            self.after_cancel(self.after_id)
        (x0, y0, x1, y1) = self.bbox("text")
        win_width = self.winfo_width()
        if win_width < 2:
            pass
        elif self.width < win_width:
            self.coords("text", (win_width / 2) - (self.width / 2), self.winfo_height() / 2)
            return
        elif x1 < 0 or y0 < 0 or self.reset:
            self.reset = False
            self.animating = True
            x0 = 20
            y0 = int(self.winfo_height() / 2)
            self.pause_ctr = 100
            self.coords("text", x0, y0)
        elif self.pause_ctr > 0:
            self.pause_ctr = self.pause_ctr - 1
        else:
            self.move("text", -2, 0)
        self.after_id = self.after(int(1000 / self.fps), self.redraw)

