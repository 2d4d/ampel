# ampel

import pyb
from pyb import Accel,Pin, Timer
import time

#### Configuration

wackelgrenze=3.5
# Uhrzeit
h=18
m=32
s=0
# weekday is 0-6 for Mon-Sun
#day=0 # mon
#day=1 # tue
#day=2 # wed
#day=3 # thu
#day=4 # fri
#day=5 # sat
day=6 # sun
#######################################################
blinking=1
nacht=0
#LEDs
red=1
green=2
yellow=3
blue=4
blink_color=red

p = Pin('A15')
#    B4 = blue LED
#    A15 = yellow LED
#    A14 = green LED
#    A13 = red LED
tim = Timer(2, freq=1000)
ch = tim.channel(1, Timer.PWM, pin=p)

rtc = pyb.RTC()

def all_led_off():
    pyb.LED(red).off()
    pyb.LED(green).off()
    pyb.LED(blue).off()
    pyb.LED(yellow).off()
    # pwm off 
    ch.pulse_width_percent(0)


# Zeit lesen
def get_time():
    (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
    return hours, minutes, seconds, weekday

# Zeit setzen
def set_time(hours, minutes, seconds):
    rtc.datetime((2014, 5, 1, day, hours, minutes, seconds, 0) )


accel = Accel()
# get average of 5 measurement to avoid sensor noise:
achselschweiß=(accel.y() + accel.y() + accel.y() + accel.y() + accel.y() ) / 5
num_messungen = 2000
min_messungen = 1990

set_time(h,m,s)

all_led_off()

while True:
    stundles, minutles, sekundles, weekday = get_time()

    # Wochenende
    if weekday >= 5:
        if (stundles == 9 and minutles == 0 and sekundles == 0 ) or ( stundles == 15 and minutles == 0 and sekundles == 0 ):
            pyb.LED(green).off()
            blinking+=1
            nacht=0
            # avoid running into this branch once more in this sekundles==0
            time.sleep(1.1)
    # Schultag
    else:
        if (stundles == 7 and minutles == 0 and sekundles == 0 ) or ( stundles == 15 and minutles == 0 and sekundles == 0 ):
            pyb.LED(green).off()
            blinking+=1
            print('blinking+=1')
            nacht=0
            # avoid running into this branch once more in this sekundles==0
            time.sleep(1.1)

    # blink yellow before 18:00 if not blinking double
    if blinking < 2 and (stundles >= 15 and stundles < 18 ):
        blink_color = yellow
    else:
        blink_color = red
    
    # Nachtabschaltungszeugs
    if stundles == 21 and minutles == 30 and sekundles == 0:
        all_led_off()
        blinking=0
        nacht=1

    # Nachts nix checken, damit es nicht anfängt grün zu leuchten bei sensor glitch
    if nacht:
        time.sleep(0.5)
    else:

        # 2 mal nicht geöffnet, rot/blau blinken
        if blinking >= 2:
            pyb.LED(blue).on()
            time.sleep(0.15)
            pyb.LED(blue).off()
            pyb.LED(red).on()
            time.sleep(0.15)
            pyb.LED(red).off()
        elif blinking == 1:
            if  blink_color == yellow:
                #old: don't actually blink in yellow
                ###pyb.LED(yellow).on()
                
                # fade yellow led
                for bright in range(50,101):
                    ch.pulse_width_percent(bright)
                    time.sleep_ms(2)
                time.sleep_ms(95)
                for bright in range(100,50,-1):
                    ch.pulse_width_percent(bright)
                    time.sleep_ms(2)
                

            else:
                pyb.LED(red).on()
                time.sleep(0.15)
                pyb.LED(red).off()
                time.sleep(0.15)


        # Wackelprüfung
        # only care for y axis
        achsel=accel.y()

        #print(accel.x(), accel.y(), accel.z())

        # viele Messungen machen um Wackler und Fehlmessungen abzufangen
        count_wackels=0
        for lola in range(num_messungen):
            if abs(achselschweiß-achsel) > wackelgrenze:
                # hat gewackelt ...
                count_wackels += 1

        # Wirklich bewegt: nicht mehr blinken
        if count_wackels > min_messungen:
            print('blinking=0')
            blinking=0
            all_led_off()
            pyb.LED(green).on()
            time.sleep(1)
            achselschweiß=achsel

