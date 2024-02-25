import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, GLib

import Helpers.markup as markup
 
class Message(Gtk.Window):
    def __init__(self, text=""):
        Gtk.Window.__init__(self)
        self.set_size_request(460, 230)
        
        self.set_position(Gtk.WindowPosition.CENTER)

        self.label = markup.Label(text=text)

        frame = Gtk.Frame()
        box = Gtk.VBox(True)

        self.btnClose = markup.Button(text="Close", callback=self.close)

        box.pack_start(self.label, True, True, 0)
        box.pack_start(self.btnClose, True, True, 0)
        
        box.add(self.btnClose)
        box.add(self.label)

        frame.add(box)

        self.add(frame)

        self.show_all()

    def close(self, widget):
        self.destroy()