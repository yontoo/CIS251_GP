# Written by: Tray Harris
# Code adapated from Gaven MacDonald's Matrix Keypad for Raspberry Pi tutorial
# https://www.youtube.com/watch?v=yYnX5QodqQ4

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

matrix = [  [1,2,3],
            [4,5,6],
            [7,8,9],
            [0]     ]

row = [10,9,11,0]
col = [23,24,25]

#Setup Column Pins
for j in range(3):
    GPIO.setup(col[j], GPIO.OUT)
    GPIO.output(col[j], 1)
#Setup Row Pins
for i in range(4):
    GPIO.setup(row[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

try:
        while(True):
            for j in range(3):
                GPIO.output(col[j], 0)

                for i in range(4):
                    if (GPIO.input(row[i])) == 0:
                        print(matrix[i][j])
                        time.sleep(0.2)
                        while(GPIO.input(row[i]) == 0):
                            pass
                
                GPIO.output(col[j], 1)
except KeyboardInterrupt:
    GPIO.cleanup(row)
    GPIO.cleanup(col)