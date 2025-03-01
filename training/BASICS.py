# ADC => Analog to digitial converter; for reading analog values
# PWM => Pulse width modulation; for generating PWM signals (analogWrite)
# Pin => GPIO pin; for reading/writing digital values
# RTC => Real time clock; for getting/setting time and date
# SPI => Serial peripheral interface; for communicating with other devices using SPI protocol
# Timer => for creating timers; for calling functions at regular intervals (setTimeout/setInterval)
# UART => for serial communication; for reading/writing serial data (Serial)
# WDT => Watchdog timer; for resetting the device if it gets stuck (watchdog)
# I2C => Inter-integrated circuit; for communicating with other devices using I2C protocol

from machine import Pin, ADC, PWM
from time import sleep
from random import random


def blink():
    # LED is connected to GPIO 25 and also connected to inbuilt LED
    # You can also use any other GPIO pin out of the 28 GPIO pins
    pin = Pin("LED", Pin.OUT)

    print("LED starts flashing...")
    while True:
        try:
            pin.toggle()
            sleep(1) 
        except KeyboardInterrupt:
            break
    pin.off()
    print("Finished.")


def read_analog():
    # adc = ADC("A0") // Same as GPIO 26 (labeled AO on the board) and on hover it shows (ADC Channel 0)
    adc = ADC(26)

    print("Reading analog value...")
    while True:
        try:
            value = adc.read_u16()
            print(value)
            sleep(1)
        except KeyboardInterrupt:
            break
    print("Finished.")


def map_(value, fromLow, fromHigh, toLow, toHigh):
    """
    Re-maps a number from one range to another.
    That is, a value of fromLow would get mapped to toLow,
    a value of fromHigh to toHigh, values in-between to values in-between, etc.

    Works by simply ploting and finding the slope of the line between the two points
    where the two points are (fromLow(x1), toLow(y1)) and (fromHigh(x2), toHigh(y2)) hence 
    i.e fromLow -> toLow and fromHigh -> toHigh where -> is the mapping
    
    Get the equestion of the line between the two points
    y = mx + c where m is the slope and c is the y-intercept x is the value to be mapped and y is the mapped value


    """

    # Can  be derived by relationships from eqation of the line
    return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow

def writeAnalogOutputUsingPWM():
    # PWM is connected to GPIO 18
    # NB: Never use same PWM e.g PMW0 A in GPIO 16 and PWM0 A in GPIO 0 to to write different analog values
    # The PWM signal will be the same for both pins
    # freq is the rate at which you are turning on and off the signal
    # duty is the percentage of time the signal is on
    # Ini this case freq is 1000Hz and period is 1/1000 = 1ms (f=1/T) 
    # towards 0 pwm is off and towards 65550 pwm is on 
    outPin = Pin(16, Pin.OUT)
    analogOut = PWM(outPin, freq=1000, duty_u16=0)
    # analogOut.duty_u16(0)

    print("PWM starts...")
    while True:
        try:
            voltage = float(input("What voltage woul you like? "))
            mapped = map_(voltage, 0, 3.3, 0, 65550)
            analogOut.duty_u16(int(mapped))
            pwm = voltage * (65550/3.3)
            analogOut.duty_u16(int(pwm))
            print(f"Voltage: {voltage=}, PWM: {pwm=}, Mapped: {mapped=}")
            sleep(1)
        except KeyboardInterrupt:
            break
    analogOut.deinit()
    print("Finished.")


def dimmablePotentiometer():
    # Setup potentiometer and LED pins
    potPin = Pin(27, Pin.IN)
    ledPin = Pin(16, Pin.OUT)
    # Setup ADC because we gonna read analog value from potentiometer and PWM becasue we gonna write analog value to LED
    pot = ADC(potPin)
    led = PWM(ledPin, freq=1000, duty_u16=0)

    while True:
        try:
           potValue = pot.read_u16()
           led.duty_u16(potValue)
           sleep(0.1) 
        except KeyboardInterrupt:
            break
    print("Finished.")



def rgbLEDDigital():
    redLedPin = Pin(20, Pin.OUT)
    greenLedPin = Pin(19, Pin.OUT)
    blueLedPin = Pin(18, Pin.OUT)

    while True:
        try:
            redLedPin.on()
            sleep(1)
            # redLedPin.off()

            greenLedPin.on()
            sleep(1)
            # greenLedPin.off()

            blueLedPin.on()
            sleep(1)
            # blueLedPin.off()

            # redLedPin.on()
            sleep(1)
            redLedPin.off()

            # greenLedPin.on()
            sleep(1)
            greenLedPin.off()

            # blueLedPin.on()
            sleep(1)
            blueLedPin.off()
        except KeyboardInterrupt:
            break
    print("Finished")


def controlRGBLED():
    redLedPin = Pin(20, Pin.OUT)
    greenLedPin = Pin(19, Pin.OUT)
    blueLedPin = Pin(18, Pin.OUT)

    redLed = PWM(redLedPin, freq=1000, duty_u16=0)
    greenLed = PWM(greenLedPin, freq=1000, duty_u16=0)  
    blueLed = PWM(blueLedPin, freq=1000, duty_u16=0)
    red = 0
    green = 0
    blue = 0
    colorsCodes = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (0, 255, 255),
        (255, 0, 255),
        (255, 255, 0),
        (255, 255, 255),
        (0, 0, 0),
        (255, 165, 0)
            ]
    print(""""
    \r__________________[RGB LED PWM]__________________
    Choose Colors:
    \r 1. Red
    \r 2. Green
    \r 3. Blue
    \r 4 Cyan
    \r 5. Magenta
    \r 6. Yellow
    \r 7. White
    \r 8. Black
    \r 9. oRANGE
    \rPress Ctrl + C to stop the program
    """)
    while True:
        
        try:
            choice = int(input("Enter your choice: "))
            color = colorsCodes[choice - 1]
            red, green, blue = color
            red = int(map_(red, 0, 255, 0, 65550))
            green = int(map_(green, 0, 255, 0, 65550))
            blue = int(map_(blue, 0, 255, 0, 65550))
            redLed.duty_u16(red)
            greenLed.duty_u16(green)
            blueLed.duty_u16(blue)
        except KeyboardInterrupt:
            break
    redLed.deinit()
    greenLed.deinit()
    blueLed.deinit()
    print("Finished.")


def buttonAndPullUpResistor():
    buttonPin = Pin(17, Pin.IN, Pin.PULL_UP)
    ledPin = Pin(16, Pin.OUT)
    print("PRESS and HOLD the button to turn on the LED...")
    while True:
        try:
            if buttonPin.value() == 0:
                ledPin.on()
            else:
                ledPin.off()
            sleep(0.1)
        except KeyboardInterrupt:
            break
    print("Finished.")



def pushButtonToggleLED():
    buttonPin = Pin(17, Pin.IN, Pin.PULL_UP)
    ledPin = Pin(16, Pin.OUT)
    print("Press and release the button to toggle the LED...")
    while True:
        try:
            if buttonPin.value() == 0:
                ledPin.toggle()
            print("LED is ON" if ledPin.value() == 1 else "LED is OFF")
            sleep(0.3)
        except KeyboardInterrupt:
            break
    print("Finished.")



def pushButtonToggle2():
    buttonPin = Pin(17, Pin.IN, Pin.PULL_UP)
    ledPin = Pin(16, Pin.OUT)
    btnNow = 1
    btnOld = 1
    print("Press and release the button to toggle the LED...")
    while True:
        btnNow = buttonPin.value()
        try:
            if btnNow == 1 and btnOld == 0:
                ledPin.toggle()
            btnOld = btnNow
            print("LED is ON" if ledPin.value() == 1 else "LED is OFF")
            sleep(0.3)
        except KeyboardInterrupt:
            break
    print("Finished.")



pushButtonToggleLED()