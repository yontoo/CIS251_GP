#Written by: Tray Harris
#Handler module for the Reed Switch

import RPi.GPIO as GPIO
import time

reed =  14 #Reed switch signal pin (BCM)

#Setup GPIO numbering to BCM, set reed pin to input
GPIO.setmode(GPIO.BCM)
GPIO.setup(reed, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Poll for changes to the reed sensor. Cleanup pins on CTRL+C
try:
    while True:
        if (GPIO.input(reed)):
            print("Door Open")
            time.sleep(0.5)
        else:
            print("Door Closed")
            time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup(reed)