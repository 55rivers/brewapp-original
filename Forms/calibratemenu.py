import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, GLib

import threading
import time
from datetime import datetime
import automationhat
import Controls.numberpad as numberpad
import logger
import Helpers.markup as markup
import Helpers.configuration as config
import Helpers.flowmeter as flowmeter
import Forms.message as message

import pigpio

class CalibrateMenu(Gtk.Window):
    """
        Initialize a new instance of the class CalibrateMenu
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Calibrate Menu")
        self.set_size_request(760, 460)
        self.set_position(Gtk.WindowPosition.CENTER)

        GObject.threads_init()

        lblCalibrate = markup.Label("Calibration", 30)
        lblWater = markup.Label("Enter the amount of\rwater to calibrate to\r and press enter:", wrap=False, center=True)
        self.lblTicks = markup.Label("Open the water valve\rand press start.", wrap=False, center=True)
        #lblTicks = markup.Label("When the amount of\r water is dispensed, press\r calibrate.", wrap=False, center=True)
        self.btnBack = markup.Button("Back ", callback=self.back_clicked)
        self.btnCalibrate = markup.Button("Start", callback=self.calibrate_clicked, enabled=False)

        # Set the unit place holders
        if config.get_value("app", "units") == "Metric":
            txtPlaceHolder = "ml"
        else:
            txtPlaceHolder = "Oz"
        
        self.txtTicks = markup.TextBox(placeholder="Pulses")
        txtWaterLevel = markup.TextBox(placeholder=txtPlaceHolder, onfocus=self.txtWaterLevel_focus)

        table = Gtk.Table(6, 9, False)
        table.set_col_spacings(10)
        table.set_row_spacings(10)

        table.attach(lblCalibrate, 0, 9, 0, 1)
        table.attach(lblWater, 0, 5, 1, 2)
        table.attach(txtWaterLevel, 0, 5, 2, 3)
        table.attach(self.lblTicks, 0, 5, 3, 4)
        table.attach(self.txtTicks, 0, 5, 4, 5)

        box = Gtk.HBox(True)
        box.pack_start(self.btnBack, True, True, 5)
        box.pack_start(self.btnCalibrate, True, True, 0)
        table.attach(box, 0, 5, 5, 6)
        #table.attach(self.btnBack, 0, 2, 5, 6)
        #table.attach(self.btnCalibrate, 2, 5, 5, 6)

        self.pad = numberpad.NumberPad()
        self.pad.btnDone.connect("clicked", self.text_entered)
        table.attach(self.pad, 5, 9, 1, 6)

        self.calibrating = False
        self.add(table)
        self.meter = flowmeter.FlowMeter()
        self.btnBack.grab_focus()
        self.show_all()

    """
        Starts the calibration process
    """
    def calibrate(self):
        try:
            self.calibrating = True

            while self.calibrating:
                self.txtTicks.update(str(self.meter.ticks))
                time.sleep(0.15)
            
        except Exception as e:
            logger.error(str(e))
        
    """
        Cancels the calibration process
    """
    def cancel_calibrate(self):
        self.calibrating = False            
        self.meter.stop()    
        
        self.txtTicks.update(str(self.meter.ticks))
        self.btnBack.update(enabled=True)
        logger.info("Calibration Thread Ended")        
        self.btnCalibrate.update("Start")

        self.show_all()

        config.set_value("calibration", "calibrated", str(True))
        config.set_value("calibration", "water_level", self.txtWaterLevel.get_text())
        config.set_value("calibration", "ticks", str(self.meter.ticks))    

        try:
            form = message.Message(text="Unit has been calibrated")
            self.add(form)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    """
        Handles the event raised when the calibrate button is clicked
    """
    def calibrate_clicked(self, widget=None):
        try:
            if self.calibrating:
                logger.info("Cancel Calibrate Clicked")
                self.cancel_calibrate()
            else:
                self.btnCalibrate.stop_flash()
                time.sleep(0.5)
                #logger.info("Flash Stopped")
                #logger.info("Changing Button Text")
                self.lblTicks.update(text="When the amount of\r water is dispensed, press\r calibrate.")
                self.btnCalibrate.update("Calibrate")
                #logger.info("Finished Changing Button Text")
                #self.show_all()
                thread = threading.Thread(target=self.calibrate)
                thread.daemon = True
                thread.start()

                self.meter.start()

                logger.info("Calibration Thread Started")

        except Exception as e:
            logger.error(str(e))

    """
        Handles the event raised when the back button is clicked
    """
    def back_clicked(self, widget=None):
        self.destroy()

    """
        Handles the event raised when the water level text box gains focus
    """
    def txtWaterLevel_focus(self, widget):
        try:
            self.txtWaterLevel = widget
            self.pad.textbox = widget

        except Exception as e:
            logger.error(str(e))

    """
        Handles the event raised when the numberpad has been destroyed
    """
    def text_entered(self, widget):
        logger.info("Numberpad Destroyed")

        if self.pad.done:
            self.btnBack.grab_focus()
            
            if len(self.txtWaterLevel.get_text()) > 0:
                self.btnCalibrate.update(enabled=True)
                self.btnCalibrate.start_flash()