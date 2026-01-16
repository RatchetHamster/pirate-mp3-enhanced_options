import time
from gpiozero import PWMLED, Button
from ST7789 import ST7789
import logging
#Logger:
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') #Change level of logging output here

DISPLAY_W = 240
DISPLAY_H = 240

#region ----- Classes -----

class Screen():
    def __init__(self):
        self.display = ST7789(
            rotation=90,
            port=0,
            cs=1,
            dc=9,
            backlight=None, #Modified as we will control this on shutdown
            spi_speed_hz=80 * 1000 * 1000
            )  
        self.DISPLAY_W = DISPLAY_W
        self.DISPLAY_H = DISPLAY_H

        # Backlight:
        self.backlight = PWMLED("BCM13", frequency=500)
        self.screen_on()

    def screen_on(self):
        self.backlight.value = 1.0 # start at 100%

    def screen_off(self):
        self.backlight.value = 0.0 # start at 0%

    def screen_dim(self):
        self.backlight.value = 0.2 # start at 20%

class Buttons():
    def __init__(self, frontend):
        self.PINS = [5, 6, 16, 24]
        self.LABELS = ['A', 'B', 'X', 'Y']
        self.BUTTONS = []
        self.was_held = {}
        self.pin_lookup = {}
        
        for pin, label in zip(self.PINS, self.LABELS):
            self.BUTTONS.append(Button(pin, pull_up=True, hold_time=2, hold_repeat=True))
            self.BUTTONS[-1].when_pressed = self.press_handle
            self.BUTTONS[-1].when_held = self.held_handle
            self.BUTTONS[-1].when_released = self.release_handle
            self.pin_lookup.update({pin: label})
            self.was_held.update({label: False})
        
        # Button call functions:
        self.press_functions={
            "A": frontend.buttonA_pressed,
            "B": frontend.buttonB_pressed,
            "X": frontend.buttonX_pressed,
            "Y": frontend.buttonY_pressed}
        self.held_functions={
            "A": frontend.buttonA_held,
            "B": frontend.buttonB_held,
            "X": frontend.buttonX_held,
            "Y": frontend.buttonY_held}
        self.release_functions={
            "A": frontend.buttonA_released,
            "B": frontend.buttonB_released,
            "X": frontend.buttonX_released,
            "Y": frontend.buttonY_released}

    def press_handle(self, btn):
        label = self.pin_lookup[btn.pin.number]
        logging.debug(f'Button {label} was pressed')
        if self.is_shutdown and label!="A":
            return
        logging.debug(f'Button {label} was pressed and triggered')
        self.press_functions[label]()

    def held_handle(self, btn):
        label = self.pin_lookup[btn.pin.number]
        logging.debug(f'Button {label} was held')
        if self.is_shutdown and label!="A":
            return
        logging.debug(f'Button {label} was held and triggered')
        btn.was_held = True
        self.held_functions[label]()

    def release_handle(self, btn):
        label = self.pin_lookup[btn.pin.number]
        logging.debug(f'Button {label} was released')
        if self.is_shutdown and label!="A":
            return
        if self.was_held[label]: 
            logging.debug(f'Button {label} was release, but was held so no trigger')
            btn.was_held[label] = False
            return
        logging.debug(f'Button {label} was release and triggered')
        self.held_functions[label]()
    

class Board(Screen, Buttons):
    def __init__(self, frontend):
        Screen.__init__(self)
        Buttons.__init__(self, frontend)
        self.frontend = frontend
        self.is_shutdown = False

    def pseduo_shutdown(self):
        # using "call(sudo shutdown -h now)" leaves the backlight pin high
        # so even if you turn off screen before shutdown, once pi is haulted 
        # the screen will persist. This stop command is therefore use to turn
        # the screen off and stop all playing audio. 
        # This also allows for a "wake" to be implimented - but the program
        # and pi are still running. 
        self.frontend.library.stop()
        self.frontend.display_splash()
        self.screen_off()
        self.is_shutdown = True

    def pseduo_wake(self):
        self.screen_on()
        self.frontend.startup_play()
        self.is_shutdown = False

#endregion


















