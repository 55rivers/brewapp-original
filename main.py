#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import sys
import os

sys.path.insert(0, "/share/Forms")
sys.path.insert(0, "/share/Controls")
sys.path.insert(0, "/share/Helpers")

import logger
import Forms.settings as settings
import Forms.brew as brew
import Forms.process as process
import Helpers.customizer as customizer
import Helpers.markup as markup
import Helpers.configuration as config
import threading
import automationhat
import time

from pynput.mouse import Controller

class MainWindow(Gtk.Window):
    """
        Initialize a new instance of the class MainWindow
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Brew Time")
        self.set_size_request(800, 480)
        self.connect("destroy", self.quit_clicked)
        
        # Reset all relays
        try:
            automationhat.relay.one.off()
            automationhat.relay.two.off()
            automationhat.relay.three.off()
        except Exception as e:
            logger.error(e)

        try:
            self.mouse = Controller()
        except Exception as e:
            logger.error(e)

        try:
            theme = customizer.Customizer()
            theme.set_default_theme()
        except Exception as e:
            logger.error(str(e))

        self.table = Gtk.Table(12, 12, False)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)

        #Main Box Configuration
        label = markup.Label("55RCB Main Menu", size=50)

        buttonClose = markup.Button("Sleep", callback=self.quit_clicked, size=20)

        buttonAuto = markup.Button("Auto Brew", callback=self.auto_clicked, size=20)

        buttonSettings = markup.Button("Settings", callback=self.settings_clicked, size=20)

        buttonManual = markup.Button("Manual Brew", callback=self.manual_clicked, size=20)

        try:
            calibrated = (config.get_value("calibration", "calibrated") == "True")
            self.lblCalibration = markup.Label("Unit is not calibrated.  Please calibrate prior to brewing", 14, "red")
        except Exception as e:
            logger.error(str(e))

        self.table.attach(label, 0, 12, 0, 1)
        self.table.attach(buttonAuto, 5, 7, 3, 4)
        self.table.attach(buttonManual, 5, 7, 5, 6)

        if calibrated:            
            calibrated = config.get_value("calibration", "ticks") != "0"

        if not calibrated:
            config.set_value("calibration", "calibrated", str(False))
            self.table.attach(self.lblCalibration, 0, 12, 1, 2)

        self.table.attach(buttonSettings, 5, 7, 7, 8)

        if config.get_value("dev", "isDev") == "True":
            self.table.attach(buttonClose, 5, 7, 9, 10)

        self.sleep_button = Gtk.Button(label="")

        sleepthread = threading.Thread(target=self.stop_sleep)
        sleepthread.daemon = True
        sleepthread.start()
        
        self.add(self.table)
        logger.info("App Started")

    """
        Handles the event raised when the manual button is clicked
    """
    def manual_clicked(self, widget=None):
        logger.info("Manual Clicked")
        try:
            form = process.Process(auto=False)
            self.add(form)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    """
        Handles the event raised when the quit button is clicked
    """
    def quit_clicked(self, widget=None):
        logger.info("App Quit")
        """
        Gtk.main_quit()
        """
        #try:
            #os.system("sudo reboot")
        #except Exception as e:
            #logger.error(str(e))
        Gtk.main_quit()
        

    """
        Handles the event raised when the settings button is clicked
    """
    def settings_clicked(self, widget=None):
        logger.info("Settings Clicked")
        try:            
            form = settings.Settings()
            form.connect("destroy", self.settings_destroyed)
            self.add(form)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    def settings_destroyed(self, widget=None):
        try:
            calibrated = (config.get_value("calibration", "calibrated") == "True")

            if not calibrated:
                self.table.attach(self.lblCalibration, 0, 9, 1, 2)
            else:
                self.table.remove(self.lblCalibration)

            self.show_all()
        except Exception as e:
            logger.error(str(e))

    """
        Handles the event raised when the auto button is clicked
    """
    def auto_clicked(self, widget):
        logger.info("Auto Clicked")
        try:
            form = process.Process(auto=True)
            self.add(form)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    """
    Simulate a mouse movement to prevent sleeping
    """
    def stop_sleep(self):
        i = 0

        while True:
            i = (i + 1) % 2
            self.mouse.position = (i, 0)
            time.sleep(300)
        
try:
    win = MainWindow()
    win.show_all()
    Gtk.main()
except Exception as e:
    logger.error(str(e))
