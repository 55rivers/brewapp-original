from gi.repository import Gtk, Gdk, GObject, Pango, GLib

import Helpers.configuration as configuration
import automationhat
import time
import logger
import RPi.GPIO as GPIO
import threading

class BorderButton(Gtk.Frame):
    """
    Initialize a new instance of Button
    """
    def __init__(self, text, size=0, enabled=True, color="", callback=None, value="", styleclass=""):
        Gtk.Frame.__init__(self)

        self.button = Button(text, size, enabled, color, callback, value, styleclass)

        self.is_flashing = False

        #self.button.set_border_width(0)

        #boxcolor = Gdk.RGBA()
        #boxcolor.parse("#4e0210")
        #self.override_background_color(Gtk.StateType.NORMAL, boxcolor)

        self.add(self.button)

    def connect(self, signal, callback):
        self.button.connect(signal, callback)

    """
    Handles the event raised when the button is clicked, sounding off a beep
    """
    def btn_click(self, widget):
        automationhat.output.one.on()
        time.sleep(0.05)
        automationhat.output.one.off()

    """
    Starts the flash process, initializing a thread
    """
    def start_flash(self):
        self.button.start_flash()
        # try:
        #     flashThread = threading.Thread(target=self.__flash)
        #     flashThread.daemon = True
        #     flashThread.start()
        # except Exception as e:
        #     logger.error(str(e))
    
    def stop_flash(self):
        self.button.stop_flash()
        #self.is_flashing = False

    """
    Flash the button text on and off
    """
    def __flash(self):
        text = self.get_child().get_text()
        self.is_flashing = True

        while self.is_flashing:
            self.update(text)
            time.sleep(0.5)
            self.update("")
            time.sleep(0.5)

        # Reset if the loop breaks
        self.update(text)

    """
    Updates the button text and sensitivity
    """
    def update(self, text=None, enabled=None):
        self.button.update(text, enabled)
        #if text is not None:
            #GLib.idle_add(self.get_child().set_markup, "<span " + self.setColor + "font='" + str(self.size) + "'>" + text + "</span>")

        #if enabled is not None:
            #self.set_sensitive(enabled)

class Button(Gtk.Button):
    """
    Initialize a new instance of Button
    """
    def __init__(self, text, size=0, enabled=True, color="", callback=None, value="", styleclass=""):
        Gtk.Button.__init__(self, label="")

        self.is_flashing = False

        if size == 0:
            size = configuration.get_value("theme", "button_font_size")

        self.setColor = ""

        if len(color) > 0:
            self.setColor = "color='" + color + "' "
            
        self.size = size
        self.enabled = enabled
        self.text = text

        self.update(text=text, enabled=enabled)
        self.connect("clicked", self.btn_click)

        if len(styleclass) > 0:
            #self.get_style_context().add_class(styleclass)
            self.set_name(styleclass)
            #logger.info(self.get_style_context().get_border_color(Gtk.StateType.NORMAL))
        
        if callback is not None:
            self.connect("clicked", callback)

        self.value = value

    """
    Handles the event raised when the button is clicked, sounding off a beep
    """
    def btn_click(self, widget):
        automationhat.output.one.on()
        time.sleep(0.05)
        automationhat.output.one.off()

    """
    Starts the flash process, initializing a thread
    """
    def start_flash(self):
        self.is_flashing = False
        
        try:
            flashThread = threading.Thread(target=self.__flash)
            flashThread.daemon = True
            flashThread.start()
        except Exception as e:
            logger.error(str(e))

    def stop_flash(self):
        self.is_flashing = False
    
    """
    Flash the button text on and off
    """
    def __flash(self):
        try:
            text = self.get_child().get_text()
            self.is_flashing = True

            empty_text = ""

            while self.is_flashing:
                self.update(text)
                time.sleep(0.5)
                if not self.is_flashing:
                    break

                self.update(empty_text)
                time.sleep(0.5)

            # Reset if the loop breaks
            self.update(text)
        except Exception as e:
            logger.error(str(e))

    """
    Updates the button text and sensitivity
    """
    def update(self, text=None, enabled=None):
        try:
            if text is not None:
                GLib.idle_add(self.get_child().set_markup, "<span " + self.setColor + "font='" + str(self.size) + "'>" + text + "</span>")

            if enabled is not None:
                self.set_sensitive(enabled)
        except Exception as e:
            logger.error(str(e))

class Label(Gtk.Label):
    """
    Initialize a new instance of Label
    """
    def __init__(self, text, size=0, color="", wrap=False, xalign=None, center=False):
        if xalign is None:
            Gtk.Label.__init__(self)
        else:
            Gtk.Label.__init__(self, xalign=xalign)

        if size == 0:
            size = configuration.get_value("theme", "label_font_size")

        setColor = ""

        if len(color) > 0:
            setColor = "color='" + color + "' "

        self.setColor = setColor
        self.size = size
        self.text = text

        self.padding = ""

        if wrap:
            self.set_line_wrap(wrap)
            self.set_line_wrap_mode(Pango.WrapMode.WORD)
            self.padding = "font_stretch='ultracondensed'"

        if center:
            self.set_justify(Gtk.Justification.CENTER)

        self.update(text)

    """
    Updates the label text
    """
    def update(self, text):
        GLib.idle_add(self.set_markup, "<span " + self.padding + " " + self.setColor + "font='" + str(self.size) + "'>" + str(text) + "</span>")

class BorderLabel(Gtk.Box):
    """
    Initialize a new instance of BorderLabel
    """
    def __init__(self, text, size=0, color="", background="", align="center"):
        Gtk.Box.__init__(self)

        if len(background) > 0:
            try:
                boxcolor = Gdk.RGBA()
                boxcolor.parse(background)
                self.override_background_color(Gtk.StateType.NORMAL, boxcolor)
            except Exception as e:
                logger.error(str(e))
    
        setColor = ""

        if len(color) > 0:
            setColor = "color='" + color + "' "

        if align == "left":
            self.label = Label(text, size, color, xalign=0.0)
        else:
            self.label = Label(text, size, color)

        if align == "left":
            alignContainer = Gtk.Alignment()
            self.label.set_justify(Gtk.Justification.LEFT)
            alignContainer.add(self.label)
            self.pack_start(alignContainer, True, True, 0)
        else:
            self.pack_start(self.label, True, True, 0)

    """
    Updates the label text
    """
    def update(self, text):
        self.label.update(text)

class TextBox(Gtk.Entry):
    """
    Initialize a new instance of TextBox
    """
    def __init__(self, size=0, placeholder="", onfocus=None, args=None):
        Gtk.Entry.__init__(self)

        GObject.threads_init()

        if size == 0:
            size = 16

        self.placeholder = placeholder

        self.modify_font(Pango.FontDescription(str(size)))
        self.set_placeholder_text(placeholder)

        if onfocus is not None:
            if args is not None:
                self.connect("grab-focus", onfocus, args)
            else:
                self.connect("grab-focus", onfocus)

    """
    Updates the text box text
    """
    def update(self, text):
        GLib.idle_add(self.set_text, text)

    def start_flash(self):
        flashThread = threading.Thread(target=self.__flash)
        flashThread.daemon = True
        flashThread.start()

    def stop_flash(self):
        self.is_flashing = False

    def __flash(self):
        try:
            #text = self.get_child().get_text()
            self.is_flashing = True

            while self.is_flashing:
                GLib.idle_add(self.set_placeholder_text, self.placeholder)
                self.show_all()
                if not self.is_flashing:
                    break
                time.sleep(0.5)
                GLib.idle_add(self.set_placeholder_text, "")
                self.show_all()
                if not self.is_flashing:
                    break
                time.sleep(0.5)

            # Reset if the loop breaks
            GLib.idle_add(self.set_placeholder_text, self.placeholder)
        except Exception as e:
            logger.error(str(e))
