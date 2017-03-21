#!/usr/bin/env python2

"""gui.py: graphical user interface to radcast"""

import os
import Tkinter as tk
import ttk
from tkFileDialog import askopenfilename
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

filename = "Choose a file"


class MainFrame(tk.Frame):
    """Collect info needed for podcast"""

    def __init__(self, parent):
        global filename
        tk.Frame.__init__(self, parent)
        self.in_frame = 0
        self.out_frame = 0

        # Need to rework bindings to make the following work
        # root.bind("<Alt-i>", self.preview_in())
        # root.bind("<Alt-o>", self.preview_out())

        root.bind_class("Text", "<Control-a>", self.select_all)
        root.bind_class("Text", "<Tab>", self.set_focus)
        root.bind_class("Button", "<space>", self.toggle_play_pause)

        # create inner frames
        self.player_frame = tk.Frame(root)
        self.main_frame = tk.Frame(root)
        self.button_frame = tk.Frame(root)

        # pack frames
        self.player_frame.pack()
        self.main_frame.pack()
        self.button_frame.pack()

        # validation goodness
        vcmd = parent.register(self.validate)

        status_bar = tk.Label(root, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        if filename:
            status_bar["text"] = "File: %s" % filename

            self.current_frame = tk.Label(self.player_frame)
            self.current_frame.pack(side=tk.TOP)

            self.in_button = tk.Button(self.player_frame, text="Set IN", command=self.set_in)
            self.in_label = tk.Label(self.player_frame, text="(0)")

            self.out_button = tk.Button(self.player_frame, text="Set OUT", command=self.set_out)
            self.out_label = tk.Label(self.player_frame, text="(0)")

            player.load_file(filename)

            # set max length of progress bar
            self.maxlength = player.length() - 1
            app.progressbar["maximum"] = self.maxlength

            self.preview_in_button = tk.Button(self.player_frame, text="Preview IN", command=self.preview_in)
            self.preview_in_button["takefocus"] = tk.FALSE
            # self.preview_in_button["underline"] = 8

            self.preview_out_button = tk.Button(self.player_frame, text="Preview OUT", command=self.preview_out)
            self.preview_out_button["takefocus"] = tk.FALSE
            # self.preview_out_button["underline"] = 8

            self.in_button.pack(side=tk.LEFT)
            self.out_button.pack(side=tk.RIGHT)

            self.in_label.pack(side=tk.LEFT)
            self.out_label.pack(side=tk.RIGHT)

            self.preview_in_button.pack(side=tk.LEFT)
            self.preview_out_button.pack(side=tk.RIGHT)

        else:
            app.open_file()

        # title
        tk.Label(self.main_frame, text="Title", anchor=tk.W).grid(row=1, sticky=tk.W)
        self.title = tk.Entry(self.main_frame, width=70, validate='key', validatecommand=(vcmd, '%P'))
        self.title.grid(row=2, pady=(4, 10), sticky=tk.W)

        # description
        tk.Label(self.main_frame, text="Description", anchor=tk.W).grid(row=3, sticky=tk.W)
        self.description = tk.Text(self.main_frame, height=7, wrap=tk.WORD)
        self.description.bind("<KeyRelease>", self.validate)
        self.description.grid(row=4, pady=(4,10), sticky=tk.W)

        # buttons
        self.GO = tk.Button(self.button_frame,
                            text="Upload Podcast",
                            command=self.go,
                            state=tk.DISABLED)

        self.GO.pack({"side": "left"})

        self.QUIT = tk.Button(self.button_frame)
        self.QUIT["text"] = "Quit",
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "right"})

    def set_in(self):
        self.in_frame = player.get_frame()
        self.in_label.config(text="(%s)" % self.in_frame)
        print("Set in frame to %s" % self.in_frame)
        app.player_frame.focus_set()

    def set_out(self):
        self.out_frame = player.get_frame()
        self.out_label.config(text="(%s)" % self.out_frame)
        print("Set out frame %s" % self.out_frame)
        app.player_frame.focus_set()

    def preview_in(self):
        player.seek_frame(self.in_frame)
        player.play()
        app.update_progress_bar()

    def preview_out(self):
        seek = self.out_frame - 120
        print self.out_frame
        if seek > 0:
            player.seek_frame(seek)
        player.producer.set_in_and_out(self.in_frame, self.out_frame)
        player.play()
        app.update_progress_bar()
        # need to clear in and out here
        # player.producer.set_in_and_out(-1, -1)

    def select_all(self, event):
        event.widget.tag_add("sel","1.0","end")

    def toggle_play_pause(self, event):
        player.toggle_play_pause()
        app.update_progress_bar()

    def set_focus(self, event):
        app.player_frame.focus_set

    def validate(self, P):
        """Insure user input is as correct as this model can be"""
        title = self.title.get().strip()
        description = self.description.get(1.0, tk.END).strip()
        if title and description:
            self.GO["state"] = tk.NORMAL
        return True

    def go(self):
        """Run radcast commands"""
        if self.in_frame <= self.out_frame:
            print "Set in and out"
        else:
            title = self.title.get().strip()
            description = self.description.get(1.0, tk.END).strip()
            print("%s\n%s" % (title, description))


class Application(tk.Frame):
    """Allows the user to set up podcast, choose an in/out point and upload"""

    # open the clip
    # choose in/out
    # preview beginning and ending for a quick quality check
    # hit the GO button

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.create_menu()
        self.open_file()
        self.player_frame()

    def about(self):
        pass

    def create_menu(self):
        """Create File and Help menus and their actions"""

        menu = tk.Menu(root)
        root.config(menu=menu)

        file_menu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator='Ctrl+Q')

        help_menu = tk.Menu(menu)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about)

    def open_file(self):
        """File chooser"""
        global filename

        FILETYPES = [
            ('Movie files', ('.mov', '.mkv', '.avi', '.mp4', '.m4v', 'mpg', 'mpeg', 'mpv', 'mp2', 'm2v', 'mjpeg', 'webm', 'ogg', 'ogv', 'ogm')),
        ]

        try:
            # filename = askopenfilename(filetypes=FILETYPES)
            filename = "/tmp/a.mp4"  # for debugging
        except TypeError, e:
            logging.error("Either the wrong filetype was chosen or no file was.")

    def player_frame(self):
        self.player_frame = tk.Frame(root, width=650, height=400)
        self.player_frame.pack()
        self.player_frame.bind("<Shift-Right>", player.jog(+10))
        self.player_frame.bind("<Key>", self.keypress)
        self.player_frame.focus_set()

        # set up progress bar underneath video
        self.progressbar = ttk.Progressbar(root, length=650, mode="determinate")
        self.progressbar.pack()
        self.progressbar["value"] = 0

        # set up scale for scrubbing through player
        s = ttk.Scale(root, orient=tk.HORIZONTAL, length=650, from_=1.0, to=100.0)
        s["from"] = 1.0
        s["to"] = 100

        # make a home for the SDL window
        os.environ['SDL_WINDOWID'] = str(self.player_frame.winfo_id())

        # update root so consumer can connect
        root.update()

        # start the consumer in the SDL frame
        player.consumer.start()

    def update_progress_bar(self):
        frame = player.get_frame()
        self.progressbar["value"] = frame
        main_frame.current_frame["text"] = frame
        if player.is_playing() and frame < main_frame.maxlength:
            self.after(100, self.update_progress_bar)

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
            main_frame.set_in()
        if key == 'o':
            main_frame.set_out()
        if key == 'space':
            player.toggle_play_pause()
        if key == 'Home':
            player.seek_frame(0)
        if key == 'End':
            player.seek_frame(player.length())

        self.update_progress_bar()

        print repr(event.keysym)
        self.progressbar["value"] = player.get_frame()


root = tk.Tk()

app = Application(master=root)
main_frame = MainFrame(root)

# key bindings
root.bind('<Control-q>', quit)

# invoke the button on the return key
root.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())

app.mainloop()
root.destroy()
player.consumer.stop()
