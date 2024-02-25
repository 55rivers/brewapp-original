from gi.repository import Gtk
import logger

import Helpers.configuration as configuration

class Customizer():
    """
        Initialize a new instance of the class Customizer
    """
    def __init__(self):
        self.Theme = "Numix"

    """
        Sets the default theme if no theme is saved
    """
    def set_default_theme(self):
        try:
            settings = Gtk.Settings.get_default()
            settings.set_property("gtk-theme-name", configuration.get_value("theme", "name"))
            settings.set_property("gtk-application-prefer-dark-theme", configuration.get_value("theme", "use_dark_theme") == "True")
            settings.set_property("gtk-font-name", "Humanst521")
        except Exception as e:
            logger.error(str(e))