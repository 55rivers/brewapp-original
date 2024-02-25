import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

import Forms.calibratemenu as calibratemenu
import Forms.setunits as setunits
import Forms.themes as themes
import Helpers.customizer as customizer
import Helpers.markup as markup
import logger

import Helpers.configuration as configuration

class Settings(Gtk.Window):
    #region Constructor
    """
        Initialize a new instance of the class Settings
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Settings")
        self.set_size_request(800, 480)

        table = Gtk.Table(12, 9, False)
        table.set_row_spacings(10)

        #Settings Box Configuration
        settingsLabel = markup.Label("Settings", 50)

        btnSetUnits = markup.Button("Set Units", callback=self.btnSetUnits_clicked)
        btnSetColorTheme = markup.Button("Set Color Theme", callback=self.btnSetColorTheme_clicked)
        btnBack = markup.Button("Back", callback=self.btnBack_clicked)
        btnCalibrateMenu = markup.Button("Calibrate", callback=self.btnCalibrateMenu_clicked)
        btnBluetooth = markup.Button("Set Bluetooth", callback=self.btnBluetooth_clicked)

        table.attach(settingsLabel, 0, 9, 0, 1)
        table.attach(btnSetUnits, 3, 6, 2, 3)
        table.attach(btnCalibrateMenu, 3, 6, 4, 5)
        table.attach(btnSetColorTheme, 3, 6, 6, 7)
        table.attach(btnBluetooth, 3, 6, 8, 9)        
        table.attach(btnBack, 3, 6, 10, 11)

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
        Handles the event raised when the blue tooth button is clicked
        !Not Implemented!
    """
    def btnBluetooth_clicked(self, widget=None):
        logger.info("Set Bluetooth Clicked")

    """
        Handles the event raised when the calibrate button is clicked
    """
    def btnCalibrateMenu_clicked(self, widget):
        try:            
            form = calibratemenu.CalibrateMenu()
            self.add(form)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    """
        Handles the event raised when the set units button is clicked
    """
    def btnSetUnits_clicked(self, widget=None):
        logger.info("Set Units Clicked")
        try:            
            form = setunits.SetUnits()
            self.add(form)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    """
        Handles the event raised when the set color theme button is clicked
    """
    def btnSetColorTheme_clicked(self , widget=None):
        logger.info("Set Color Theme Clicked")
        try:
            form = themes.Themes()
            self.add(form)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    #endregion