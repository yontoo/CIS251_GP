##################
#
#
# Written by: 
#   Tray Harris
#
#
# Research and Development:
#   Luis Lopez-Rangel
#   Tray Harris
#
#
##################

import RPi.GPIO as GPIO
import time
import threading
from configparser import ConfigParser as cp
import sys
from picamera import PiCamera


GPIO.setmode(GPIO.BCM)

armed = False
tripped = False
running = True
first_time = False
pressed = False
config_file = cp()
config_file.read('./config.ini')
images_path = "/home/pi/CIS251/CIS251_GP/images"
#Variable for current number pressed on keypad
curr_num = 15
code = ''
camera = PiCamera()


#2d array for matrix keypad
matrix = [  [1,2,3],
            [4,5,6],
            [7,8,9],
            [0]     ]

#Pin numbers of sensors and keypad
row = [10,9,11,0]
col = [23,24,25]
reed = 14
pir = 4

#set up pins for use, start disarmed
def setup():
    global first_time

    #Check config.ini, if stored code is 0 then its the first time running
    config_file.read('./config.ini')
    if (config_file['PASSCODE']['code']) == '0':
        first_time = True

    #Setup pin for reed switch and PIR motion sensor
    GPIO.setup(reed, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pir, GPIO.IN)

    #Setup Column Pins of matrix keypad
    for j in range(3):
        GPIO.setup(col[j], GPIO.OUT)
        GPIO.output(col[j], 1)

    #Setup Row Pins of matrix keypad
    for i in range(4):
        GPIO.setup(row[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

    camera.resolution = (1024, 768)

    #Setup function thread
    keypad_thread = threading.Thread(target=keypad)

    #Start keypad thread
    keypad_thread.start()


#verify keypad input and arm
def validate():
    global code
    print("\nEnter 4 digit code: ", end='')
    while (True):

        if (pressed and curr_num != 0):
            code += str(curr_num)
            print(curr_num, end='')
        if (curr_num == 0 or len(code) == 4):
            if (len(code) < 4):
                print("\nEntered code too short. Try again.")
                code = ''
            else:
                config_file.read('./config.ini')
                if (code == str(config_file['PASSCODE']['code'])):
                    print("\nCorrect Code.")
                    code = ''
                    return True
                else:
                    print("\nWrong code. Try again.")
                    code = ''
            print("\nEnter 4 digit code: ", end='')
        time.sleep(0.1)

def reset_pass():
    global code
    choosing = False
    print("\nEnter new 4 digit code (1-9) and press 0 to enter: ", end='')
    while (True):

        if (pressed and curr_num != 0):
            code += str(curr_num)
            print(curr_num, end='')
        if (curr_num == 0 or len(code) == 4):
            if (len(code) < 4):
                print("\nEntered code too short. Try again.")
                code = ''
            else:
                config_file.read('./config.ini')
                print("\nYour new passcode will be " + code + ". Are you sure?\n0 for yes, 9 for no.")
                choosing = True
                while (choosing):
                    if (curr_num == 0):
                        config_file['PASSCODE']['code'] = code
                        with open('config.ini','w') as config_out:
                            config_file.write(config_out)
                        print("Passcode is now: " + code)
                        code = ''
                        choosing = False
                        print_menu()
                        time.sleep(2)
                        return
                    elif (curr_num == 9):
                        print("Re-enter new code.")
                        code = ''
                        choosing = False
            print("\nEnter new 4 digit code (1-9) and press 0 to enter: ", end='')
        time.sleep(0.1)

#alarm, turn on alarm led, record, notify etc
#PIR Motion Sensor research: Luis
def sys_armed():
    global tripped, armed
    has_printed= False
    while(armed):
            #If input goes high, alarm is tripped
            if (GPIO.input(reed) or GPIO.input(pir)):
                tripped = True
            if (curr_num == 0):
                if (validate()):
                    armed = False
                    main()
                    return
            time.sleep(0.1)
            while (tripped):
                if not (has_printed):
                    print("Alarm tripped! Verify to reset alarm.")
                    #take 5 pictures on alarm
                    for i in range(5):
                        time.sleep(2)    #Cam warmup time
                        camera.capture(images_path + "/" + str(int(time.time())) + '.jpg')
                    has_printed = True
                if (validate()):
                    tripped = False
                    has_printed = False
                    armed = False
                    main()
                    return

#function for getting keypad presses
def keypad():
    global curr_num, pressed
    while(running):
        for j in range(3):
            GPIO.output(col[j], 0)

            for i in range(4):
                if (GPIO.input(row[i])) == 0:
                    curr_num = matrix[i][j]
                    #print(curr_num)
                    time.sleep(0.01)
                    while(GPIO.input(row[i]) == 0):
                        pressed = True
                        pass
                    pressed = False
                    curr_num = 15

            GPIO.output(col[j], 1)
    return

def print_menu():
    print("""
Menu
-----------------
Press 1 to arm
Press 2 to reset code
Press 3 to turn off system
    """)

def main():
    global running, armed
    print_menu()
    while(running and not armed):
        if curr_num == 1:
            if(validate()):
                armed = True
                sys_arm_thread = threading.Thread(target=sys_armed)
                sys_arm_thread.start()
                print("System armed.")
        #reset passcode
        elif curr_num == 2:
            print("Verify to reset passcode.")
            if (validate()):
                reset_pass()

        elif curr_num == 3:
            #turn off system
            GPIO.cleanup()
            running = False
        time.sleep(0.1)
    if not (running):
        sys.exit()

setup()
main()
