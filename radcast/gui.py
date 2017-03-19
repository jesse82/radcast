#!/usr/bin/env python2

"""gui.py: graphical user interface to radcast"""

from Tkinter import *
from tkFileDialog import askopenfilename
from radcast import logging
import mlt
import os
import yaml

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


class Settings:

    """Project settings, and preferences"""

    def __init__(self):

        try:  # if current directory exists
            self.project_dir = os.getcwd()
        except OSError:  # if not, go back a directory and try again
            os.chdir("..")
            self.project_dir = os.getcwd()

        # set initial values
        self.title = "UNTITLED"
        self.profile = "atsc_720p_2997"
        self.media_dir = None
        self.frame_rate = 30
        self.drop_frame = True
        self.jog_skip_frames = 8
        self.still_seconds = 6
        self.transition_length = int(self.frame_rate)
        self.pre_roll = int(self.frame_rate)

        try:  # if settings file exists in current dir, read into cfg

            with open(self.project_dir + "/settings.yml", 'r') as ymlfile:
                cfg = yaml.safe_load(ymlfile)

                # TODO deserialize implicitly instead of explicitly

                self.title = cfg.get('title', self.title)
                self.project_dir = cfg.get('project_dir', self.project_dir)
                self.media_dir = cfg.get('media_dir', self.media_dir)
                self.profile = cfg.get('profile', self.profile)
                self.frame_rate = cfg.get('frame_rate', self.frame_rate)
                self.pre_roll = int(cfg.get('pre_roll', self.pre_roll))
                self.drop_frame = cfg.get('drop_frame', self.drop_frame)
                self.jog_skip_frames = cfg.get('jog_skip_frames', self.jog_skip_frames)
                self.still_seconds = cfg.get('still_seconds', self.still_seconds)
                self.transition_length = int(cfg.get('transition_length', self.transition_length))

        except yaml.YAMLError, e:

            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                print("Error in settings file: (line %s, column %s)" % (
                    mark.line + 1, mark.column + 1)
                )

        except:

            print "No settings file detected."

        # set dependent variables
        self.still_frames = self.still_seconds * self.frame_rate
        self.mlt_profile = mlt.Profile(self.profile)

settings = Settings()


class Player:

    """MLT player https://www.mltframework.org/docs/framework/"""

    def __init__(self):

        self.current_clip = "NULL"

        # initialize mlt
        mlt.Factory().init()

        # initialize producer with NULL if no current_clip is available
        self.producer = mlt.Producer(settings.mlt_profile, self.current_clip)

        # initialize and start consumer
        self.consumer = mlt.Consumer(settings.mlt_profile, "sdl")
        self.consumer.set("rescale", "bicubic")
        self.consumer.set("resize", 1)
        self.consumer.set("real_time", 1)
        self.consumer.set("progressive", 1)
        self.connect_producer()

    def connect_producer(self):
        self.consumer.purge()
        self.producer.set_speed(0)
        self.consumer.connect(self.producer)
        #self.consumer.start()

    def stop(self):
        self.producer.set_speed(0)

    def pause(self):
        self.producer.set_speed(0)

    def play(self):
        self.producer.set_speed(1)

    def reverse(self):
        self.producer.set_speed(-1)

    def shuttle_forward(self):
        speed = self.producer.get_speed()
        if speed < 1:
            self.producer.set_speed(1)
        elif speed == 1:
            self.producer.set_speed(2)
        elif speed == 2:
            self.producer.set_speed(5)
        elif speed == 5:
            self.producer.set_speed(10)

    def shuttle_reverse(self):
        speed = self.producer.get_speed()
        if speed >= 0:
            self.producer.set_speed(-1)
        elif speed == -1:
            self.producer.set_speed(-2)
        elif speed == -2:
            self.producer.set_speed(-5)
        elif speed == -5:
            self.producer.set_speed(-10)

    def jog(self, amount):
        """Jog forward or reverse by negative or positive amount"""
        # pause playback if not paused already
        self.producer.set_speed(0)
        frame = self.producer.frame()
        self.producer.seek(frame + amount)

    def get_frame(self):
        return self.producer.frame()

    def length(self):
        return self.producer.get_length()

    def seek_frame(self, frame):
        length = self.length()
        if frame < 0:
            frame = 0
        elif frame >= length:
            frame = length - 1
        self.producer.set_speed(0)
        self.producer.seek(frame)

    def end(self):
        length = self.length()
        last_frame = length - 1
        self.seek_frame(last_frame)

    def load_file(self, path):
        self.producer = mlt.Producer(settings.mlt_profile, path)
        self.connect_producer()
        self.current_clip = path

    def is_stopped(self):
        if self.producer.get_speed() == 0:
            return True

    def toggle_play_pause(self):
        if self.is_stopped():
            self.producer.set_speed(1)
        else:
            self.producer.set_speed(0)

player = Player()


class MainFrame(Frame):
    """Collect info needed for podcast"""

    def __init__(self, parent):
        global filename
        Frame.__init__(self, parent)
        root.bind_class("Text", "<Control-a>", self.selectall)
        self.in_frame = 0
        self.out_frame = 0

        # create inner frames
        self.player_frame = Frame(root)
        self.main_frame = Frame(root)
        self.button_frame = Frame(root)

        # pack frames
        self.player_frame.pack()
        self.main_frame.pack()
        self.button_frame.pack()

        # validation goodness
        vcmd = parent.register(self.validate)

        if filename:
            file_label = Label(self.player_frame, text="File: %s" % filename)

            self.in_button = Button(self.player_frame, text="Set IN", command=self.set_in)
            self.in_label = Label(self.player_frame, text="(0)")

            self.out_button = Button(self.player_frame, text="Set OUT", command=self.set_out)
            self.out_label = Label(self.player_frame, text="(0)")

            player.load_file(filename)

            self.preview_in_button = Button(self.player_frame, text="Preview IN", command=self.preview_in)
            self.preview_out_button = Button(self.player_frame, text="Preview OUT", command=self.preview_out)

            file_label.pack(side=TOP)

            self.in_button.pack(side=LEFT)
            self.out_button.pack(side=RIGHT)

            self.in_label.pack(side=LEFT)
            self.out_label.pack(side=RIGHT)

            self.preview_in_button.pack(side=LEFT)
            self.preview_out_button.pack(side=RIGHT)

        else:
            app.open_file()

        # title
        Label(self.main_frame, text="Title", anchor=W).grid(row=1, sticky=W)
        self.title = Entry(self.main_frame, width=70, validate='key', validatecommand=(vcmd, '%P'))
        self.title.grid(row=2, pady=(4, 10), sticky=W)

        # description
        Label(self.main_frame, text="Description", anchor=W).grid(row=3, sticky=W)
        self.description = Text(self.main_frame, height=7, wrap=WORD)
        self.description.bind("<KeyRelease>", self.validate)
        self.description.grid(row=4, pady=(4,10), sticky=W)

        # buttons
        self.GO = Button(self.button_frame,
                         text="Upload Podcast",
                         command=self.go,
                         state=DISABLED)

        self.GO.pack({"side": "left"})

        self.QUIT = Button(self.button_frame)
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

    def preview_out(self):
        player.seek_frame(self.out_frame - 120)
        player.producer.set_in_and_out(self.in_frame, self.out_frame)
        player.play()

    def selectall(self, event):
        event.widget.tag_add("sel","1.0","end")

    def validate(self, P):
        """Insure user input is as correct as this model can be"""
        title = self.title.get().strip()
        description = self.description.get(1.0, END).strip()
        self.GO.config(state=(NORMAL if title and description else DISABLED))
        return True

    def go(self):
        """Run radcast commands"""

        title = self.title.get().strip()
        description = self.description.get(1.0, END).strip()

        if self.title and self.description:
            print("%s\n%s" % (title, description))

class Application(Frame):
    """Allows the user to set up podcast, choose an in/out point and upload"""

    # open the clip
    # choose in/out
    # preview beginning and ending for a quick quality check
    # hit the GO button

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_menu()
        self.open_file()
        self.player_frame()

    def about(self):
        pass

    def create_menu(self):
        """Create File and Help menus and their actions"""

        menu = Menu(root)
        root.config(menu=menu)

        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator='Ctrl+Q')

        help_menu = Menu(menu)
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
            filename = "/tmp/a.mp4"
            # move to status bar in a later version
        except TypeError, e:
            logging.error("Either the wrong filetype was chosen or no file was.")

    def player_frame(self):
        self.player_frame = Frame(root, width=650, height=400)
        self.player_frame.pack()
        self.player_frame.bind("<Shift-Right>", player.jog(+10))
        self.player_frame.bind("<Key>", self.keypress)
        self.player_frame.focus_set()

        # make a home for the SDL window
        os.environ['SDL_WINDOWID'] = str(self.player_frame.winfo_id())

        # update root so consumer can connect
        root.update()

        # start the consumer in the SDL frame
        player.consumer.start()

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
        if key == '<Shift-Right>' or key == 'Up':
            player.jog(+10)
        if key == '<Shift-Left>' or key == 'Down':
            player.jog(-10)
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
        print repr(event.keysym)




root = Tk()

app = Application(master=root)
main_frame = MainFrame(root)


# key bindings
root.bind('<Control-q>', quit)

app.mainloop()
root.destroy()
