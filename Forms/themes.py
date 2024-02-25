from gi.repository import Gtk
import logger

import Helpers.markup as markup
import Helpers.configuration as config
import Helpers.customizer as customizer

class Themes(Gtk.Window):
    #region Constructor
    """
        Initialize a new instance of the class Themes
    """
    def __init__(self):
        Gtk.Window.__init__(self)
        self.set_size_request(800, 480)
        self.set_position(Gtk.WindowPosition.CENTER)

        table = Gtk.Table(9, 9, False)
        table.set_row_spacings(10)
        table.set_col_spacings(10)

        lblMain = markup.Label("Set Color Theme", 30)

        self.lblCurrent = markup.Label("Current Theme: " + config.get_value("theme", "name"), 16)

        lblDefault = markup.Label("Default", 16)
        btnDefault = markup.Button("Light", 16, callback=self.btnTheme_clicked, value="BrewBomb")

        lblMarwaita = markup.Label("Yosemite", 16)
        btnMarwaitaLight = markup.Button("Light", 16, callback=self.btnTheme_clicked, value="Yosemite")
        btnMarwaitaDark = markup.Button("Dark", 16, callback=self.btnTheme_clicked, value="Yosemite")

        lblNumix = markup.Label("Numix", 16)
        btnNumixLight = markup.Button("Light", 16, callback=self.btnTheme_clicked, value="Numix")
        btnNumixDark = markup.Button("Dark", 16, callback=self.btnTheme_clicked, value="Numix")

        lblCoffee = markup.Label("Coffee", 16)
        btnCoffee = markup.Button("Dark", 16, callback=self.btnTheme_clicked, value="Coffee")

        lblLuna = markup.Label("Luna", 16)
        btnLuna = markup.Button("Light", 16, callback=self.btnTheme_clicked, value="Luna")

        btnBack = markup.Button("Back", 16, callback=self.btnBack_clicked)

        table.attach(lblMain, 0, 6, 0, 1)
        table.attach(self.lblCurrent, 0, 3, 1, 2)

        table.attach(lblDefault, 0, 2, 2, 3)
        table.attach(btnDefault, 2, 3, 2, 3)

        table.attach(lblCoffee, 0, 2, 3, 4)
        table.attach(btnCoffee, 3, 4, 3, 4)

        table.attach(lblNumix, 0, 2, 4, 5)
        table.attach(btnNumixLight, 2, 3, 4, 5)
        table.attach(btnNumixDark, 3, 4, 4, 5)

        table.attach(lblMarwaita, 0, 2, 5, 6)
        table.attach(btnMarwaitaLight, 2, 3, 5, 6)
        table.attach(btnMarwaitaDark, 3, 4, 5, 6)

        table.attach(lblLuna, 0, 2, 6, 7)
        table.attach(btnLuna, 2, 3, 6, 7)

        table.attach(btnBack, 2, 4, 7, 8)

        self.add(table)

        self.show_all()

    #endregion

    #region Event Handlers
    """
        Handles the event raised when the back button is clicked
    """
    def btnBack_clicked(self, widget=None):
        self.destroy()

    """
        Handles the event raised when one of the theme buttons has been clicked
    """
    def btnTheme_clicked(self, widget):
        try:
            if widget.get_child().get_text() == "Dark":
                config.set_value("theme", "use_dark_theme", True)
            else:  
                config.set_value("theme", "use_dark_theme", False)

            config.set_value("theme", "name", widget.value)
            theme = customizer.Customizer()
            theme.set_default_theme()
            self.lblCurrent.update("Current Theme: " + config.get_value("theme", "name"))
        except Exception as e:
            logger.error(str(e))

    #endregion
