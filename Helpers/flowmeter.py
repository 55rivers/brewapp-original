import logger
import automationhat
import threading
import pigpio
from datetime import datetime, timedelta
import time
from collections import deque
import Helpers.configuration as config

class FlowMeter():
    """
        Initialize a new instance of the class FlowMeter
    """
    def __init__(self):
        logger.info("Flow Meter Initialized")
        automationhat.input.auto_light(False)

        self.currentTime = datetime.now()
        self.lastTime = datetime.now()
        self.lastTickTime = datetime.now()
        self.ticks = 0
        self.currentTicks = 0
        self.lastTicks = 0
        self.rate = 0

        self.updated = False

    """
        Opens the flow meter and starts the interrupt process
    """
    def start(self):
        try:
            self.running = True
            self.ticks = 0
            logger.info("Flow Meter Started")
            self.pi0 = pigpio.pi()
            self.pi0.set_mode(automationhat.INPUT_3, pigpio.INPUT)
            self.pi0.set_pull_up_down(automationhat.INPUT_3, pigpio.PUD_UP)
            logger.info("Start Time: " + datetime.now().strftime("%I:%M:%S.%f"))
            self.startTime = datetime.now()

            self.singleRate = 0
            self.rateArray = []
            self.flowing = False
            self.isBeeping = False

            self.lowestRate = 0

            self.rateDeque = deque()

            self.open()

            rateThread = threading.Thread(target=self.calculateRate)
            rateThread.daemon = True
            rateThread.start()

            avgThread = threading.Thread(target=self.averageRate)
            avgThread.daemon = True
            avgThread.start()

            #Used for testing only
            if config.get_value("dev", "isDev") == "True":
                testThread = threading.Thread(target=self.test)
                testThread.daemon = True
                testThread.start()

        except Exception as e:
            logger.error(str(e))

    def test(self):
        while self.running:
            self.ticks += 1
            time.sleep(0.3)

    """
        Handles the event raised when an interrupt occurs from the flow meter
    """
    def gpio_callback(self, gpio, level, tick):    
        self.ticks += 1            

    """
        Calculates the current flow rate using a deque
    """
    def calculateRate(self):
        try:
            while self.running:
                self.currentTime = datetime.now()
                self.currentTicks = self.ticks

                timediff = self.currentTime - self.lastTime
                self.lastTime = self.currentTime

                singleRate = (self.currentTicks - self.lastTicks) * timediff.total_seconds()

                if self.lowestRate > singleRate and singleRate > 0:
                    self.lowestRate = singleRate

                if singleRate > 0:
                    self.lastTickTime = datetime.now()

                if(len(self.rateDeque) > 10):
                    self.rateDeque.popleft()

                self.rateDeque.append(singleRate)

                time.sleep(1 - (datetime.now() - self.currentTime).total_seconds())

                self.lastTicks = self.currentTicks
                
        except Exception as e:
            logger.error("Calculate Rate: " + str(e))

    """
        Closes the flow meter and stops the interrupt process
    """
    def stop(self, alarm=0):
        self.cb.cancel()
        self.close()
        logger.info("End Time: " + datetime.now().strftime("%I:%M:%S.%f"))
        self.running = False
        self.alarm = alarm
        
        if self.alarm > 0:
            thread = threading.Thread(target=self.beep)
            thread.start()

    """
        Calculate the average flowrate
    """
    def averageRate(self):
        try:
            while self.running:
                # Set a timeout to check if the water is actually flowing
                if (datetime.now() - self.lastTickTime).total_seconds() > 5 or self.ticks <= 0 or self.stopped:
                    self.flowing = False
                else:
                    self.flowing = True

                rateTotal = 0

                for rate in self.rateDeque:
                    rateTotal += rate

                self.rate = rateTotal / len(self.rateDeque)

                if self.rate == 0 and self.flowing:
                    self.rate = rateTotal

                if self.rate == 0 and self.flowing:
                    self.rate = self.lowestRate

                time.sleep(0.5)
        except Exception as e:
            logger.error("Average Rate: " + str(e))

    """
        Sound off an alarm when the flow rate is closed
    """
    def beep(self):
        #if self.alarm == 1:
            #automationhat.output.one.on()
            #time.sleep(1)
            #automationhat.output.one.off()
        #else:
        automationhat.relay.three.on()
        self.isBeeping = True    
        time.sleep(15)
        automationhat.relay.three.off()
        self.isBeeping = False

    def stop_beep(self):
        automationhat.relay.three.off()
        self.isBeeping = False

    """
        Opens the solenoid valve
    """
    def open(self):
        automationhat.relay.one.on()
        self.stopped = False  
        self.cb = self.pi0.callback(automationhat.INPUT_3, pigpio.FALLING_EDGE, self.gpio_callback)

    """
        Closes the solenoid valve
    """
    def close(self):
        automationhat.relay.one.off()
        self.stopped = True
        self.cb.cancel()
        self.flowing = False
        self.lastTickTime -= timedelta(seconds=16)