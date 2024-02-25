from gi.repository import Gtk
import automationhat
import threading
import time
import logger
import Controls.numberpad as numberpad

import Helpers.markup as markup
import Helpers.configuration as config
import Forms.brew as brew

class Process(Gtk.Window):
    #region Constructor
    """
        Initialize a new instance of the class Process
    """
    def __init__(self, auto=False):
        Gtk.Window.__init__(self, title="Auto Menu")
        
        self.set_size_request(760, 440)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.currenttext = None

        if auto:
            wintype = "Auto"
        else:
            wintype = "Manual"

        if config.get_value("app", "units") == "Metric":
            self.isMetric = True
        else:
            self.isMetric = False

        self.auto = auto

        self.table = Gtk.Table(6, 9, False)
        self.table.set_row_spacings(10)
        self.table.set_col_spacings(10)

        self.lblHeader = markup.Label(wintype + " Menu", 30)

        self.dispenseEntered = False
        self.coffeeEntered = False
        self.timeEntered = False
        self.preInfuse = False

        self.btnback = markup.Button("Cancel", callback=self.btnback_clicked)

        self.btnrun = markup.Button("Run", callback=self.btnrun_clicked, enabled=False)

        if config.get_value("app", "units") == "Metric":
            lblWater = "Liters"
            lblCoffee = "Kilograms"
            lblRate = "HH:MM"
        else:
            lblWater = "Gallons"
            lblCoffee = "Pounds"
            lblRate = "gal/min"

        lblDuration = "HH:MM"

        #Boxes
        lblyield = markup.Label("Yield")
        self.txtyield = markup.TextBox(placeholder=lblWater, onfocus=self.txt_clicked, args="Yield")

        lblqty = markup.Label("Coffee Qty")
        self.txtqty = markup.TextBox(placeholder=lblCoffee, onfocus=self.txt_clicked, args="Coffee Quantity")
        
        lbltime = markup.Label("Brew Time")
        self.txttime = markup.TextBox(placeholder=lblDuration, onfocus=self.txt_clicked, args="Time")

        if self.auto:
            lblinfuse = markup.Label("Pre Infuse")
            self.table.attach(self.lblHeader, 0, 9, 0, 1)
            self.table.attach(lblyield, 0, 2, 1, 2)
            self.table.attach(self.txtyield, 2, 5, 1, 2)
            self.table.attach(lblqty, 0, 2, 3, 4)
            self.table.attach(self.txtqty, 2, 5, 3, 4)
            self.table.attach(lbltime, 0, 2, 2, 3)
            self.table.attach(self.txttime, 2, 5, 2, 3)
            self.table.attach(lblinfuse, 0, 2, 4, 5)
            self.txtInfused = markup.TextBox(placeholder=lblWater, onfocus=self.txt_clicked, args="Infuse Amount")
            self.table.attach(self.txtInfused, 2, 5, 4, 5)
            self.show_all()
        else:
            lblFlowRate = markup.Label("Flow / Min")
            self.table.attach(self.lblHeader, 0, 9, 0, 1)
            self.table.attach(lblyield, 0, 2, 1, 2)
            self.table.attach(self.txtyield, 2, 5, 1, 2)
            self.table.attach(lbltime, 0, 2, 2, 3)
            self.table.attach(self.txttime, 2, 5, 2, 3)
            self.table.attach(lblqty, 0, 2, 4, 5)
            self.table.attach(self.txtqty, 2, 5, 4, 5)            
            self.txtRate = markup.TextBox()
            self.table.attach(lblFlowRate, 0, 2, 3, 4)
            self.table.attach(self.txtRate, 2, 5, 3, 4)

        # self.table.attach(self.lblHeader, 0, 9, 0, 1)
        # self.table.attach(lblyield, 0, 2, 1, 2)
        # self.table.attach(self.txtyield, 2, 5, 1, 2)
        # self.table.attach(lblqty, 0, 2, 3, 4)
        # self.table.attach(self.txtqty, 2, 5, 3, 4)
        # self.table.attach(lbltime, 0, 2, 2, 3)
        # self.table.attach(self.txttime, 2, 5, 2, 3)

        self.txtyield.start_flash()
        
        box = Gtk.HBox(True)
        box.pack_start(self.btnback, True, True, 10)
        box.pack_start(self.btnrun, True, True, 0)
        self.table.attach(box, 0, 5, 5, 6)
        #self.table.attach(self.btnback, 0, 2, 5, 6)
        #self.table.attach(self.btnrun, 2, 5, 5, 6)

        self.pad = numberpad.NumberPad()
        self.pad.btnDone.connect("clicked", self.text_entered)
        self.table.attach(self.pad, 5, 9, 1, 6, xoptions=Gtk.AttachOptions.EXPAND, xpadding=0)

        if config.get_value("calibration", "calibrated") == "False":
            lblCalibrate = markup.Label("Calibration is Required", size=14, color="Red")
            self.table.attach(lblCalibrate, 0, 9, 5, 6)

        self.btnback.grab_focus()

        self.add(self.table)
        self.show_all()

    #endregion

    #region Event Handlers
    """
        Handles the event raised when the back button is clicked
    """
    def btnback_clicked(self, widget):
        self.btnrun.is_flashing = False
        self.destroy()

    """
        Handles the event raised when the infuse button is toggled on
    """
    def btnInfuse_clicked(self, widget):
        self.preInfuse = True
        logger.info("Infused Clicked")
        self.table.remove(self.btnInfuseYes)
        self.table.remove(self.btnInfuseNo)

        self.txtInfused = markup.TextBox()
        self.txtInfused.connect("grab-focus", self.txt_clicked, "Infuse Amount")
        self.table.attach(self.txtInfused, 5, 7, 4, 5)
        self.show_all()
        
        self.txtInfused.grab_focus()

    """
        Handles the event raised when the run button is clicked
    """
    def btnrun_clicked(self, widget):
        try:            
            water = self.txtyield.get_text()
            duration = self.txttime.get_text()
            hours = int(duration.split(":")[0])
            minutes = int(duration.split(":")[1])
            qty = float(self.txtqty.get_text())
            if(not self.auto):
                rate = float(self.txtRate.get_text())
            else:
                rate = 0

            if self.auto and len(self.txtInfused.get_text()) > 0:
                infuse = float(self.txtInfused.get_text())
            else:
                infuse = 0

            logger.info("Brew Starting")

            form = brew.Brew(rate=rate, hours=hours, minutes=minutes, dispense=water, quantity=qty, preinf=infuse, auto=self.auto)
            form.connect("destroy", self.brew_destroyed)
            self.btnrun.stop_flash()
            self.add(form)
            self.table.set_visible(False)
            self.show_all()
        except Exception as e:
            logger.error(str(e))

    def brew_destroyed(self, widget):
        self.btnrun.is_flashing = False
        self.table.set_visible(True)
        self.btnrun.update(text="Run")
        self.validate()

    """
        Handles the event raised when a text box gains focus
    """
    def txt_clicked(self, widget, header):
        self.currenttext = widget
        self.pad.textbox = self.currenttext
        self.currenttext.stop_flash()
        
    """
        Handles the event raised when a number pad is destroyed
    """
    def text_entered(self, widget):
        try:
            self.btnrun.stop_flash()

            if self.pad.done:
                if self.currenttext == self.txtyield:
                    self.dispenseEntered = True
                elif self.currenttext == self.txttime:
                    self.timeEntered = True
                elif self.currenttext == self.txtqty:
                    self.coffeeEntered = True

                if self.dispenseEntered and self.timeEntered and self.coffeeEntered and self.validate():
                    if not self.auto:
                        self.updateFlow()         

                    self.btnrun.update(enabled=True)

                    if not self.btnrun.is_flashing:
                        self.btnrun.start_flash()

            if len(self.txtyield.get_text()) <= 0:
                self.txtyield.start_flash()
            elif len(self.txttime.get_text()) <= 0:
                self.txttime.start_flash()
            elif len(self.txtqty.get_text()) <= 0:
                self.txtqty.start_flash()
            elif self.auto and len(self.txtInfused.get_text()) <= 0:
                self.txtInfused.start_flash()

            self.btnback.grab_focus()

        except Exception as e:
            logger.error(str(e))

    #endregion

    #region Methods
    """
        Updates the flow rate
    """
    def updateFlow(self):
        dispensed = float(self.txtyield.get_text())
        quantity = float(self.txtqty.get_text())
        hours = int(self.txttime.get_text().split(":")[0])
        minutes = int(self.txttime.get_text().split(":")[1])

        if self.isMetric:
            flowrate = (dispensed * 1000) / ((hours * 60) + minutes)
        else:
            flowrate = (dispensed * 128) / ((hours * 60) + minutes)

        self.txtRate.set_text(str(round(flowrate, 3)))

        self.show_all()

    def validate(self):
        ret = True

        #logger.info("validating")

        # check water input
        try:
            water = float(self.txtyield.get_text())
        except Exception as e:
            logger.error(str(e))
            ret = False

        # check time input
        try:
            duration = self.txttime.get_text()
            hours = int(duration.split(":")[0])
            minutes = int(duration.split(":")[1])
        except Exception as e:
            logger.error(str(e))
            ret = False

        # check coffee quantity input
        try:
            qty = float(self.txtqty.get_text())
        except Exception as e:
            logger.error(str(e))
            ret = False

        if not ret:
            self.btnrun.is_flashing = False

        if self.auto:
            if len(self.txtInfused.get_text()) <= 0:
                ret = False

        #logger.info("Valid: " + str(ret))

        return ret

    #endregion