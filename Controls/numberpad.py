from gi.repository import Gtk
import logger
import Helpers.markup as markup
class NumberPad(Gtk.HBox):
    def __init__(self, header="Enter Value"):
        try:
            Gtk.HBox.__init__(self, True)
            #Gtk.Table.__init__(self, 4, 4, True)

            self.set_size_request(365, 360)
            self.set_name("tblNumPad")
            
            current = 1

            table = Gtk.Table(4, 4, True)

            self.buttons = [
                markup.BorderButton("1", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("2", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("3", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("4", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("5", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("6", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("7", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("8", callback=self.btnNumber_clicked, styleclass="numberpad"),
                markup.BorderButton("9", callback=self.btnNumber_clicked, styleclass="numberpad")
            ]

            i = 0
            j = 3

            for button in self.buttons:
                if i >= 3:
                    i = 0
                    j -= 1
                table.attach(button, i, i + 1, j - 1, j)
                i += 1

            btn0 = markup.BorderButton("0", callback=self.btnNumber_clicked, styleclass="numberpad")
            self.btnDone = markup.BorderButton("Enter", callback=self.btnDone_clicked, styleclass="numberpad")
            btnDelete = markup.BorderButton("Del", callback=self.btnDelete_clicked, styleclass="numberpad")
            btnPeriod = markup.BorderButton(".", callback=self.btnNumber_clicked, styleclass="numberpad")
            btnColon = markup.BorderButton(":", callback=self.btnNumber_clicked, styleclass="numberpad")

            table.attach(btnColon, 0, 1, 3, 4)
            table.attach(btn0, 1, 2, 3, 4)
            table.attach(btnDelete, 3, 4, 0, 2)
            table.attach(self.btnDone, 3, 4, 2, 4)
            table.attach(btnPeriod, 2, 3, 3, 4)

            self.textbox = None

            self.pack_start(table, True, True, 0)

            self.set_hexpand(False)

            self.show_all()
            
        except Exception as e:
            logger.error(str(e))

    def btnDelete_clicked(self, widget):
        try:
            # place holder for delete button
            self.textbox.set_text(self.textbox.get_text()[:-1])
        except Exception as e:
            logger.error(str(e))

    def btnDone_clicked(self, widget):
        self.done = True
        self.btnDone.is_flashing = False
        self.btnDone.stop_flash()

    def btnNumber_clicked(self, widget=None):

        if not self.btnDone.is_flashing:
            self.btnDone.is_flashing = True
            self.btnDone.start_flash()

        try:
            self.textbox.set_text(self.textbox.get_text() + widget.get_child().get_text())

        except Exception as e:
            logger.error(str(e))