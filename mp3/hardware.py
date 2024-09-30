import time
import RPi.GPIO as GPIO
from ST7789 import ST7789

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
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(13, GPIO.OUT)
        self.backlight = GPIO.PWM(13, 500)
        self.screen_on()

    def screen_on(self):
        self.backlight.start(100) # start at 100%

    def screen_off(self):
        self.backlight.start(0) # start at 0%

    def screen_dim(self):
        self.backlight.start(20) # start at 20%

class Buttons():
    def __init__(self, frontend):
        self.BUTTONS = [5, 6, 16, 24]
        self.LABELS = ['A', 'B', 'X', 'Y']
        self.long_press_dur = 1 #(sec)
        self.but_press_time={
            "A": None,
            "B": None, 
            "X": None, 
            "Y": None}
        self.time_of_last_but_press = time.time()

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        for pin in self.BUTTONS:
            GPIO.add_event_detect(pin, GPIO.BOTH, self.handle_buttons, bouncetime=50)
        
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
        
    def handle_buttons(self, pin):
        label = self.LABELS[self.BUTTONS.index(pin)]
        
        
        # Disable buttons but exceptions on shutdown:
        if self.is_shutdown and label!="A":
            return

        # Button Press:
        self.time_of_last_but_press = time.time()
        if self.but_press_time[label]==None:
            self.press_functions[label]()
            self.but_press_time[label] = time.time()
            return
        
        # Button Released:
        press_duration = time.time()-self.but_press_time[label]
        self.but_press_time[label] = None
        self.release_functions[label](press_duration)


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
        self.but_press_time={
            "A": None,
            "B": None, 
            "X": None, 
            "Y": None}
        self.frontend.library.stop()
        self.frontend.display_splash()
        self.screen_off()
        self.is_shutdown = True

    def pseduo_wake(self):
        self.screen_on()
        self.frontend.startup_play()
        self.is_shutdown = False

#endregion
