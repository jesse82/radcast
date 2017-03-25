#!/usr/bin/env python2

import os
import yaml
import logging

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

    """Settings and preferences"""

    def __init__(self):

        PROFILES = [
            "atsc_1080p_2398",
            "atsc_1080p_24",
            "atsc_1080p_2997",
            "atsc_1080p_30",
            "atsc_1080p_50",
            "atsc_1080p_5994",
            "atsc_1080p_60",
            "atsc_720p_2398",
            "atsc_720p_24",
            "atsc_720p_25",
            "atsc_720p_2997",
            "atsc_720p_30",
            "atsc_720p_50",
            "atsc_720p_5994",
            "atsc_720p_60",
            "dv_ntsc",
            "dv_ntsc_wide"
        ]

        # set initial minimum cfg values

        self.cfg = {
            "profile": "atsc_720p_2997",
            "jog_skip_frames": 30,
            "transition_length": 24,
        }

        try:  # if home directory exists
            self.home_dir = os.path.expanduser("~")
        except:
            logging.error("Cannot access home directory for settings file.")

        self.files_found = 0
        cfg_sources = [
            self.home_dir + "/.radcast",
            self.home_dir + "/.radcast.yml",
            self.home_dir + "/.config/radcast/settings.yml",
            self.home_dir + "/radcast/settings.yml",
        ]

        try:  # if settings file exists in first of cfg_sources, read cfg dict

            for c in cfg_sources:
                if os.path.isfile(c):
                    self.cfg = yaml.safe_load(open(c))
                    self.files_found += 1
                    logging.debug(
                        "Settings file(s) found: %s" % self.files_found
                    )
                    break

        except yaml.YAMLError, e:

            if hasattr(e, 'problem_mark'):
                mark = e.problem_mark
                logging.error(
                    "Error in settings file: (line %s, column %s)" %
                    (mark.line + 1, mark.column + 1)
                )

        except:

            if self.files_found < 1:  # create default settings file if none are found

                logging.debug("No settings file found. \
                Creating default settings file in ~/.radcast")

                try:
                    with open(self.home_dir + '/.radcast', 'w') as cfg_file:
                        yaml.dump(self.cfg, cfg_file, default_flow_style=False)
                except:
                    logging.error("Error writing settings file")

settings = Settings()
cfg = settings.cfg
