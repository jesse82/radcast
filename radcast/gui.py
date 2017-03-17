#!/usr/bin/env python2

import Tkinter as tk

__author__ = "Josh Wheeler"
__copyright__ = "Copyright 2007, Josh Wheeler"
__license__ = "MIT"
__maintainer__ = "Josh Wheeler"
__email__ = "mantlepro@gmail.com"
__status__ = "Development"


class Application(tk.Frame):

    def __init__(self, master=None):
        tk. Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def say_hi(self):
        print "hi there, everyone!"

    def createWidgets(self):
        self.QUIT = tk.Button(self)
        self.QUIT["text"] = "QUIT"
        self.QUIT["command"] =  self.quit

        self.QUIT.pack({"side": "left"})

        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello",
        self.hi_there["command"] = self.say_hi

        self.hi_there.pack({"side": "left"})

root = tk.Tk()
app = Application(master=root)
app.mainloop()
root.destroy()
