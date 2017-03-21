#!/usr/bin/env python2

import os
import yaml

"""settings.py: Gather project settings and preferences"""

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


class Settings:

    """Project settings, and preferences"""

    def __init__(self):

        try:  # if current directory exists
            self.project_dir = os.getcwd()
        except OSError:  # if not, go back a directory and try again
            os.chdir("..")
            self.project_dir = os.getcwd()

        # set initial values
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

settings = Settings()
