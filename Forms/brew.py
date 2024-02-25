from gi.repository import Gtk
from datetime import datetime

import time
import threading
import Helpers.markup as markup
import Helpers.configuration as config
import logger
import math

import Helpers.flowmeter as flowmeter

class Brew(Gtk.Window):
    """
        Initialize a new instance of the class Brew
    """
    def __init__(self, rate=0, hours=0, minutes=0, dispense="", quantity=0, preinf=0, auto=False):
        Gtk.Window.__init__(self)
        self.set_size_request(780, 460)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.is_metric = False
        self.auto = auto   

        if hours == 0 and minutes == 0:
            time = config.get_value("auto", "time")
            hours = int(time.split(":")[0])
            minutes = int(time.split(":")[1])
        else:
            time = str(hours).zfill(2) + ":" + str(minutes).zfill(2)

        if config.get_value("app", "units") == "Metric":
            self.is_metric = True

        if rate == 0:
            rate = float(config.get_value("auto", "rate"))

        if len(dispense) <= 0:
            dispense = config.get_value("auto", "water_level")

        self.hours = int(hours)
        self.minutes = int(minutes)
        self.targetDispense = float(dispense)
        self.targetRate = round(rate, 3)
        self.quantity = quantity
        self.preInf = preinf
        self.totalSeconds = 0

        self.initialize()

        if self.is_metric:
            rateLabel = "ml / min"
        else:
            rateLabel = "oz / min"

        table = Gtk.Table(6, 4, False)
        table.set_row_spacings(5)
        table.set_col_spacings(5)
        
        lblBrewing = markup.Label("Brewing", 40)

        targetBg = "#b3b3b4"
        currentBg = "#e6e7e6"
        labelBg = "#a13335"

        lblTarget = markup.BorderLabel("Target", size=20, color="Black", background=targetBg)
        self.lblTargetRate = markup.BorderLabel(str(self.targetRate), size=20, color="Black", background=targetBg)
        self.lblTargetTime = markup.BorderLabel(str(time), size=20, color="Black", background=targetBg)
        self.lblTargetDispensed = markup.BorderLabel(str(format(self.targetDispense, ".2f")), size=20, color="Black", background=targetBg)

        lblCurrent = markup.BorderLabel("Current", size=20, color="Black", background=currentBg)
        self.lblCurrentRate = markup.BorderLabel("", size=20, color="Black", background=currentBg)
        self.lblCurrentTime = markup.BorderLabel("00:00:00", size=20, color="Black", background=currentBg)
        self.lblCurrentDispensed = markup.BorderLabel("", size=20, color="Black", background=currentBg)
        self.lblExtractionRatio = markup.BorderLabel("0.00", size=20, color="Black", background=currentBg)

        lblRate = markup.BorderLabel(rateLabel, size=20, background=labelBg, align="left")
        lblTime = markup.BorderLabel("Brew Time", size=20, background=labelBg, align="left")
        lblDispensed = markup.BorderLabel("Total Dispensed", size=20, background=labelBg, align="left")
        lblExtraction = markup.BorderLabel("Extraction Ratio", size=20, background=labelBg, align="left")

        #Alarm/Stop Buttons
        lblAlarm = markup.BorderLabel("Alarm", size=20, color="White", background=labelBg)
        self.lblAlarmVal = markup.Button("On", callback=self.alarm_toggle)
        lblAutoStop = markup.BorderLabel("Auto Stop", size=20, color="White", background=labelBg)
        self.lblAutoStopVal = markup.Button("On", callback=self.autostop_toggle)

        btnBack = markup.Button("Back", callback=self.btnBack_clicked)

        btnStop = markup.Button("Stop", callback=self.btnStop_clicked)
        btnStop.value = 1

        table.attach(lblBrewing, 0, 1, 0, 1)
        table.attach(lblRate, 0, 1, 1, 2)
        table.attach(lblTime, 0, 1, 2, 3)
        table.attach(lblDispensed, 0, 1, 3, 4)
        table.attach(lblExtraction, 0, 2, 4, 5)

        table.attach(lblTarget, 1, 2, 0, 1)
        table.attach(self.lblTargetRate, 1, 2, 1, 2)
        table.attach(self.lblTargetTime, 1, 2, 2, 3)
        table.attach(self.lblTargetDispensed, 1, 2, 3, 4)
        

        table.attach(lblCurrent, 2, 3, 0, 1)
        table.attach(self.lblCurrentRate, 2, 3, 1, 2)
        table.attach(self.lblCurrentTime, 2, 3, 2, 3)
        table.attach(self.lblCurrentDispensed, 2, 3, 3, 4)
        table.attach(self.lblExtractionRatio, 2, 3, 4, 5)

        table.attach(lblAlarm, 3, 4, 0, 1)
        table.attach(self.lblAlarmVal, 3, 4, 1, 2)
        table.attach(lblAutoStop, 3, 4, 3, 4)
        table.attach(self.lblAutoStopVal, 3, 4, 4, 5)

        table.attach(btnBack, 0, 1, 5, 6)
        table.attach(btnStop, 1, 3, 5, 6)

        self.add(table)
        self.show_all()

        self.running = True
        self.alarm = 1
        self.autoStop = True

        self.startTime = datetime.now()

        self.meter = flowmeter.FlowMeter()
        
        self.timeThread = threading.Thread(target=self.timer)
        self.timeThread.daemon = True
        self.timeThread.start()

        self.variableThread = threading.Thread(target=self.updateVariables)
        self.variableThread.daemon = True
        self.variableThread.start()

        self.flowRateThread = threading.Thread(target=self.updateFlow)
        self.flowRateThread.daemon = True
        self.flowRateThread.start()

        self.lastTicks = 0

        self.totalSecondsStopped = 0

        self.meter.start()

    """
        Handles the event raised when the alarm is toggled
    """
    def alarm_toggle(self, widget):   
        if self.alarm == 1:
            widget.update("Off")
            self.alarm = 0

            if self.meter.isBeeping:
                self.meter.stop_beep()

        elif self.alarm == 0:
            widget.update("On")
            self.alarm = 1

    """
        Handles the event raised when the autostop button is toggled
    """
    def autostop_toggle(self, widget):
        if self.autoStop:
            widget.update("Off")
            self.autoStop = False
        else:
            widget.update("On")
            self.autoStop = True

    """
        Initialize  the "current" variables
    """
    def initialize(self):
        #logger.info("Initializing")
        self.timeInMinutes = self.hours * 60 + self.minutes
        self.currentDispensed = 0
        self.currentRate  = 0

        self.timeInMinutesRemaining = self.timeInMinutes

        self.sensorConstant = round(int(config.get_value("calibration", "water_level")) / float(config.get_value("calibration", "ticks")), 8)

        #logger.info("Sensor Constant: " + str(self.sensorConstant))

        #logger.info("Pre Infuse: " + str(self.preInf))

        if(self.auto):
            if self.is_metric:
                self.targetDispense = self.targetDispense + ((self.quantity * 2) - self.preInf)
                self.targetRate = (self.targetDispense * 1000) / self.timeInMinutes
            else:
                self.targetDispense = self.targetDispense + (((self.quantity * 2) / 8.35) - self.preInf)
                self.targetRate = (self.targetDispense * 128) / self.timeInMinutes

    """
        Handles the event raised when the back button is clicked
    """
    def btnBack_clicked(self, widget):
        if self.running:
            self.alarm = 0
            self.stop()
        self.destroy()

    """
        Handles the event raised when the stop button is clicked
    """
    def btnStop_clicked(self, widget):
        try:
            if widget.value == 1:
                self.meter.close()
                widget.update("Run")
                widget.value = 2
            else:
                self.meter.open()
                widget.update("Stop")
                widget.value = 1
        except Exception as e:
            logger.error(str(e))
        
    """
        Stop the brewing process
    """
    def stop(self):
        if self.running:
            self.running = False
            self.meter.stop(self.alarm)

            logger.info("Brewing Stopped")

    """
        Updates the timer if the UI needs updates
    """
    def timer(self):
        while self.running:
            time.sleep(0.1)

            if self.needsUpdated():
                self.lastTicks = self.meter.ticks  
                self.updateTime()

    """
        Checks if the UI needs updated. Returns true if the flow sensor is registering ticks
    """
    def needsUpdated(self):
        ret = True
        try:
            if not self.meter.flowing:
                ret = False
                self.totalSecondsStopped += float((datetime.now() - self.lastTimeStopped).microseconds / 1000000)
            
        except Exception as e:
            self.totalSecondsStopped = 0
            pass

        finally:
            if not ret:
                self.lastTimeStopped = datetime.now()
            return ret

    """
        Updates the timer label
    """
    def updateTime(self):
        try:
            self.lblCurrentTime.update(self.get_time_string())
        except Exception as e:
            logger.error("Update Time: " + str(e))

    """
        Updates the current dispensed and extraction ratio labels
    """
    def updateVariables(self):
        try:
            while self.running:
                self.currentDispensed = self.meter.ticks * self.sensorConstant

                if self.is_metric:
                    displayDispensed = round(self.currentDispensed / 1000, 2)
                    exr = round(displayDispensed / self.quantity, 2)
                else:
                    displayDispensed = round(self.currentDispensed / 128, 2)
                    exr = round(((displayDispensed * 8.35) * 2) / (2 * self.quantity), 2)

                if self.running and displayDispensed >= self.targetDispense and self.autoStop:
                    self.stop()

                self.lblCurrentDispensed.update(format(displayDispensed, ".2f"))
                self.lblExtractionRatio.update(format(exr, ".2f"))

                time.sleep(0.1)

        except Exception as e:
            logger.error(str(e))

    """
        Updates the current and target flow rates
    """
    def updateFlow(self):
        try:
            while self.running:
                self.currentRate = (self.meter.rate * 60) * self.sensorConstant

                self.lblCurrentRate.update(format(round(self.currentRate, 2), ".2f"))

                if self.is_metric:
                    self.dispenseRemaing = self.targetDispense - (self.currentDispensed / 1000)
                    remainingRate = (self.dispenseRemaing * 1000) / self.timeInMinutesRemaining
                else:
                    self.dispenseRemaing = self.targetDispense - (self.currentDispensed / 128)
                    remainingRate = (self.dispenseRemaing * 128) / self.timeInMinutesRemaining

                if self.running:
                    self.lblTargetRate.update(format(round(remainingRate, 2), ".2f"))
                
                time.sleep(1)
        except Exception as e:
            logger.info(str(e))

    """
        Gets the timer label string in a nice format
    """
    def get_time_string(self):
        duration = datetime.now() - self.startTime

        days, seconds = duration.days, duration.seconds - int(self.totalSecondsStopped)
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)

        self.timeInMinutesRemaining = self.timeInMinutes - ((duration.total_seconds() - self.totalSecondsStopped) / 60)

        return str(hours).zfill(2) + ":" + str(minutes).zfill(2) + ":" + str(seconds).zfill(2)        