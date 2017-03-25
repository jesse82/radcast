import mlt
from settings import settings

"""mlt_player.py: MLT-based player for radcast"""

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


class Player:

    """MLT player https://www.mltframework.org/docs/framework/"""

    def __init__(self):

        self.current_clip = "NULL"

        # initialize mlt
        mlt.Factory().init()
        self.mlt_profile = mlt.Profile(settings.cfg["profile"])

        # initialize producer with NULL if no current_clip is available
        self.producer = mlt.Producer(self.mlt_profile, self.current_clip)

        # initialize and start consumer
        self.consumer = mlt.Consumer(self.mlt_profile, "sdl")
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
        self.producer.seek(frame)

    def end(self):
        length = self.length()
        last_frame = length - 1
        self.seek_frame(last_frame)

    def load_file(self, path):
        self.producer = mlt.Producer(self.mlt_profile, path)
        self.connect_producer()
        self.current_clip = path

    def is_stopped(self):
        if self.producer.get_speed() == 0:
            return True

    def is_playing(self):
        if self.producer.get_speed() != 0:
            return True

    def toggle_play_pause(self):
        if self.is_stopped():
            self.producer.set_speed(1)
        else:
            self.producer.set_speed(0)

player = Player()
