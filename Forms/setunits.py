from gi.repository import Gtk

import Helpers.configuration as config
import Helpers.markup as markup
import logger

class SetUnits(Gtk.Window):
    """
        Initialize a new instance of the class SetUnits
    """
    def __init__(self):
        Gtk.Window.__init__(self, title="Set Units")
        self.set_size_request(800, 480)

        self.table = Gtk.Table(6, 6, True)
        self.table.set_col_spacings(10)

        box = Gtk.HBox()

        lblMain = markup.Label("Set Units", 30)

        lblUnits = markup.Label("Current Units: ", 25)

        self.lblCalibrate = markup.Label("Calibration is Required", size=14, color="Red")

        self.lblUnitsValue = markup.Label(config.get_value("app", "units"), size=25)

        btnMetric = markup.Button("Metric", callback=self.unitsChanged, value="Metric")

        btnImperial = markup.Button("Imperial", callback=self.unitsChanged, value="Imperial")

        btnBack = markup.Button("Back", callback=self.btnBack_clicked)

        box.pack_start(lblUnits, True, True, 0)
        box.pack_start(self.lblUnitsValue, True, True, 0)

        self.table.attach(lblMain, 0, 6, 0, 1)
        self.table.attach(box, 1, 5, 1, 2)
        #self.table.attach(lblUnits, 2, 3, 1, 2)
        #self.table.attach(self.lblUnitsValue, 3, 4, 1, 2)
        self.table.attach(btnMetric, 2, 3, 2, 3)
        self.table.attach(btnImperial, 3, 4, 2, 3)        
        self.table.attach(btnBack, 2, 4, 4, 5)

        self.add(self.table)
        self.show_all()
    
    """
        Handles the event raised when the units button is toggled
    """
    def unitsChanged(self, widget):
        config.set_value("app", "units", widget.value)
        self.lblUnitsValue.update(config.get_value("app", "units"))
        self.table.attach(self.lblCalibrate, 2, 4, 3, 4)
        self.show_all()
        config.set_value("calibration", "calibrated", False)

    """
        Handles the event raised when the back button is clicked
    """
    def btnBack_clicked(self, widget=None):
        self.destroy()