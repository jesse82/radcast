#!/usr/bin/env python2

"""gui.py: graphical user interface to radcast"""

from Tkinter import *

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


class InfoFrame(Frame):
    """Collect info needed for podcast"""

    def __init__(self, parent):

        Frame.__init__(self, parent)

        self.info_frame = Frame(root)
        self.info_frame.pack(padx=20, pady=20)

        self.button_frame = Frame(root)
        self.button_frame.pack()

        # title
        Label(self.info_frame, text="Title", anchor=W).grid(row=0, sticky=W)
        self.title = Entry(self.info_frame, width=70)
        self.title.grid(row=1, pady=(4,10), sticky=W)

        # description
        Label(self.info_frame, text="Description", anchor=W).grid(row=3, sticky=W)
        self.description = Text(self.info_frame, height=7, wrap=WORD)
        self.description.grid(row=4, pady=(4,10), sticky=W)

        self.GO = Button(self.button_frame, text="Upload Podcast", command=self.go)
        self.GO.pack({"side": "left"})

        self.QUIT = Button(self.button_frame)
        self.QUIT["text"] = "Quit",
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "right"})

    def go(self):
        # TODO Validate user input

        title = self.title.get().strip()
        description = self.description.get(1.0, END).strip()

        if self.title and self.description:
            print("%s\n%s" % (self.title, self.description))


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
        self.create_widgets()
        root.bind_class("Text", "<Control-a>", self.selectall)

    def selectall(self, event):
        event.widget.tag_add("sel","1.0","end")

    def open_file(self):
        pass

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
        file_menu.add_command(label="Exit", command=self.quit)

        help_menu = Menu(menu)
        menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.about)

    def create_widgets(self):
        self.info_frame = InfoFrame(root)




root = Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
