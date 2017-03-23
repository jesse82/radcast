#!/usr/bin/env python2

"""gui.py: graphical user interface to radcast"""

import os
import Tkinter as tk
import ttk
import tkFileDialog
from radcast import logging
from mlt_player import player

__copyright__ = "Copyright 2007, Josh Wheeler"
__license__ = "GPL"
__status__ = "Development"

#    radcast: radical podcast automation
#    Copyright (C) 2017 Josh Wheeler
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


class VideoFrame(tk.Frame):
    """SDL player window with indicators and in and out buttons"""
    def __init__(self, parent, width, height):
        tk.Frame.__init__(self, parent, width=width, height=height)
        self.frame = tk.Frame(parent, width=width, height=height)
        self.parent = parent

        self.frame.pack()

        self.in_out_frame = InOutFrame(self)
        self.in_out_frame.pack()

        # make a home for the SDL window
        os.environ['SDL_WINDOWID'] = str(self.frame.winfo_id())

        # update root so consumer can connect
        root.update()

        # create a progress bar underneath video
        self.progressbar = ttk.Progressbar(self, mode="determinate")
        self.progressbar["length"] = 650
        self.progressbar["value"] = 0
        self.progressbar.pack()

        # add counter label below progress bar
        self.counter_label = tk.Label(self)
        self.counter_label.pack(side=tk.TOP)

    def update_progress_bar(self):
        i = player.get_frame()
        self.progressbar["value"] = i
        self.counter_label["text"] = i
        if player.is_playing() and i < self.parent.maxlength:
            root.after(100, self.update_progress_bar)
        else:
            # clear in/out for preview out
            player.producer.set_in_and_out(-1, -1)  



class InOutFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.in_button = tk.Button(self, text="Set IN", command=self.set_in)
        self.in_label = tk.Label(self, text="(0)")

        self.out_button = tk.Button(self, text="Set OUT", command=self.set_out)
        self.out_label = tk.Label(self, text="(0)")

        self.preview_in_button = tk.Button(self, text="Preview IN", command=self.preview_in)
        self.preview_in_button["takefocus"] = tk.FALSE
        self.preview_in_button["state"] = "disabled"
        # self.preview_in_button["underline"] = 8

        self.preview_out_button = tk.Button(self, text="Preview OUT", command=self.preview_out)
        self.preview_out_button["takefocus"] = "false"
        self.preview_out_button["state"] = "disabled"
        # self.preview_out_button["underline"] = 8

        self.in_button.pack(side="left")
        self.out_button.pack(side="right")

        self.in_label.pack(side="left")
        self.out_label.pack(side="right")

        self.preview_in_button.pack(side="left")
        self.preview_out_button.pack(side="right")

    def set_in(self):
        clip.in_frame = player.get_frame()
        self.in_label.config(text="(%s)" % clip.in_frame)
        print("Set in frame to %s" % clip.in_frame)
        if clip.in_frame > 0:
            self.preview_in_button["state"] = "normal"

    def set_out(self):
        clip.out_frame = player.get_frame()
        self.out_label.config(text="(%s)" % clip.out_frame)
        print("Set out frame %s" % clip.out_frame)
        if clip.out_frame > 0:
            self.preview_out_button["state"] = "normal"

    def preview_in(self):
        player.seek_frame(clip.in_frame)
        player.play()
        self.parent.update_progress_bar()

    def preview_out(self):
        seek_to = clip.out_frame - 240
        print clip.out_frame
        if seek_to > 0:
            player.seek_frame(seek_to)
        player.producer.set_in_and_out(clip.in_frame, clip.out_frame)
        player.play()
        self.parent.update_progress_bar()


class InputFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.bind_class("Text", "<Control-a>", self.select_all)
        self.bind_class("Text", "<Tab>", self.set_focus)

        # validation goodness
        vcmd = parent.register(self.validate)

        # title
        tk.Label(self, text="Title", anchor="w").grid(row=1, sticky="w")
        self.title = tk.Entry(self, width=70, validate='key', validatecommand=(vcmd, '%P'))
        self.title.grid(row=2, pady=(4, 10), sticky="w")

        # description
        tk.Label(self, text="Description", anchor="w").grid(row=3, sticky="w")
        self.description = tk.Text(self, height=7, wrap="word")
        self.description.bind("<KeyRelease>", self.validate)
        self.description.grid(row=4, pady=(4, 10), sticky="w")

    def validate(self, P):
        """Insure user input is as correct as this model can be"""
        title = self.title.get().strip()
        description = self.description.get(1.0, "end").strip()
        if title and description:
            self.parent.GO["state"] = "normal"
        return True

    # events

    def set_focus(self, event):
        self.parent.focus_set

    def select_all(self, event):
        event.widget.tag_add("sel", "1.0", "end")


class MainFrame(tk.Frame):
    """Collect info needed for podcast"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # key bindings
        self.bind("<Key>", self.keypress)
        self.bind("<Shift-Right>", player.jog(+10))
        self.focus_set()

        self.bind_class("Button", "<space>", self.toggle_play_pause)

        # Need to rework bindings for the following to work
        # root.bind("<Alt-i>", self.preview_in())
        # root.bind("<Alt-o>", self.preview_out())

        # create frames within main frame
        self.video_frame = VideoFrame(self, width=650, height=400)
        self.input_frame = InputFrame(self)
        self.button_frame = tk.Frame(self)

        # pack frames
        self.video_frame.pack()
        self.input_frame.pack()
        self.button_frame.pack()

        # load file into player
        self.load_file()

        # main action buttons
        self.GO = tk.Button(self.button_frame,
                            text="Upload Podcast",
                            command=self.go,
                            state="disabled")
        self.GO.pack({"side": "left"})
        self.QUIT = tk.Button(self.button_frame)
        self.QUIT["text"] = "Quit",
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "right"})

    def load_file(self):
        """Load file into player"""

        if clip.filename:
            self.parent.statusbar["text"] = "File: %s" % clip.filename

            # load the file into the player
            player.load_file(clip.filename)

            # start the consumer in the SDL frame
            player.consumer.start()

            # set max length of progress bar
            self.maxlength = player.length() - 1
            self.video_frame.maxlength = self.maxlength
            self.video_frame.progressbar["maximum"] = self.maxlength

    def go(self):
        """Run radcast commands"""
        if clip.out_frame <= clip.in_frame:
            print "Set in and out"
        else:
            title = self.input_frame.title.get().strip()
            description = self.input_frame.description.get(1.0, tk.END).strip()
            print("%s\n%s" % (title, description))

    def toggle_play_pause(self, event):
        player.toggle_play_pause()
        self.video_frame.update_progress_bar()

    def keypress(self, event):
        key = event.keysym
        if "1" <= key <= "9":
            length = player.length()
            percent = int(key) * .100
            seek = int(length * percent)
            player.seek_frame(seek)
        if key == 'Left':
            player.jog(-1)
        if key == 'Right':
            player.jog(+1)
        if key == 'Next' or key == 'Up':
            player.jog(+24)
        if key == 'Prior' or key == 'Down':
            player.jog(-24)
        if key == 'l':
            player.shuttle_forward()
        if key == 'k':
            player.toggle_play_pause()
        if key == 'j':
            player.shuttle_reverse()
        if key == 'i':
            self.video_frame.in_out_frame.set_in()
        if key == 'o':
            self.video_frame.in_out_frame.set_out()
        if key == 'space':
            player.toggle_play_pause()
        if key == 'Home':
            player.seek_frame(0)
        if key == 'End':
            player.seek_frame(player.length())
        self.video_frame.update_progress_bar()
        print repr(event.keysym)
        self.video_frame.progressbar["value"] = player.get_frame()


class About(tk.Toplevel):
    """About the application"""

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent

        self.title = "About"

        self.ABOUT_TEXT = """
radcast: a radical podcast uploader

Copyright (C) 2017  Josh Wheeler 

This program comes with ABSOLUTELY NO WARRANTY;

This is free software, and you are welcome to redistribute it under certain conditions.
"""

        msg = tk.Message(self, text=self.ABOUT_TEXT, justify="center")
        msg.pack()

        button = tk.Button(self, text="got it", command=self.destroy)
        button.pack()

class MainMenu(tk.Menu):

    """Create File and Help menus and their actions"""

    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        self.parent = parent

        root.config(menu=self)

        file_menu = tk.Menu(self)
        self.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.parent.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator='Ctrl+Q')

        help_menu = tk.Menu(self)
        self.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about)

    def about(self):
        self.about = About(root)


class StatusBar(tk.Label):
    def __init__(self, parent, *args, **kwargs):
        tk.Label.__init__(self, parent, bd=1, relief="sunken", anchor="w")
        self.parent = parent


class Clip:
    """Clip object to be edited"""
    def __init__(self):
        self.filename = ""
        self.in_frame = 0
        self.out_frame = 0

clip = Clip()


class Application(tk.Frame):

    """Set up podcast, choose an in/out point and upload"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.statusbar = StatusBar(self)
        self.statusbar.pack(side="bottom", fill="x")
        self.menu = MainMenu(self)

        # open a file
        self.open_file()

    def open_file(self):
        """File chooser"""

        FILETYPES = [
            ('Movie files', ('.mov', '.mkv', '.avi', '.mp4', '.m4v', 'mpg', 'mpeg', 'mpv', 'mp2', 'm2v', 'mjpeg', 'webm', 'ogg', 'ogv', 'ogm')),
        ]

        try:
            clip.filename = tkFileDialog.askopenfilename(filetypes=FILETYPES)
            if clip.filename:
                self.main = MainFrame(self)
                self.main.pack(side="top", fill="both", expand=True)
        except TypeError, e:
            logging.error("Error opening file")


root = tk.Tk()

Application(root).pack(side="top", fill="both", expand=True)

# key bindings
root.bind('<Control-q>', quit)

# invoke button on the return key
root.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())

root.mainloop()

# clean up
root.destroy()
player.consumer.stop()
