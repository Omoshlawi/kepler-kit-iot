import machine
import time

class LCD():
    """A class to control LCD1602 display via I2C interface.
    This class provides methods to initialize and control an LCD1602 display module
    using I2C communication. It supports common LCD1602 operations like writing text,
    clearing the screen, and controlling the backlight.
    Attributes:
        addr (int): I2C address of the LCD (typically 0x27 or 0x3F)
        blen (int): Backlight control (1=ON, 0=OFF)
        bus (machine.I2C): I2C bus object for communication
    Methods:
        scanAddress(addr): Scans for LCD at specified or default I2C addresses
        write_word(data): Writes a byte of data to the LCD
        send_command(cmd): Sends a command byte to the LCD
        send_data(data): Sends a data byte to the LCD
        clear(): Clears the LCD screen
        openlight(): Turns on the LCD backlight
        write(x, y, str): Writes a string at specified position (x,y)
        message(text): Writes a multi-line text message to the LCD
    Example:
        lcd = LCD()  # Initialize with default settings
        lcd.write(0, 0, "Hello")  # Write "Hello" at position (0,0)
        lcd.message("Hello\\nWorld")  # Write multiline text
    """

    def __init__(self, addr=None, blen=1):
        sda = machine.Pin(6)
        scl = machine.Pin(7)
        self.bus = machine.I2C(1,sda=sda, scl=scl, freq=400000)
        #print(self.bus.scan())
        self.addr = self.scanAddress(addr)
        self.blen = blen
        self.send_command(0x33) # Must initialize to 8-line mode at first
        time.sleep(0.005)
        self.send_command(0x32) # Then initialize to 4-line mode
        time.sleep(0.005)
        self.send_command(0x28) # 2 Lines & 5*7 dots
        time.sleep(0.005)
        self.send_command(0x0C) # Enable display without cursor
        time.sleep(0.005)
        self.send_command(0x01) # Clear Screen
        self.bus.writeto(self.addr, bytearray([0x08]))

    def scanAddress(self, addr):
        devices = self.bus.scan()
        if len(devices) == 0:
            raise Exception("No LCD found")
        if addr is not None:
            if addr in devices:
                return addr
            else:
                raise Exception(f"LCD at 0x{addr:2X} not found")
        elif 0x27 in devices:
            return 0x27
        elif 0x3F in devices:
            return 0x3F
        else:
            raise Exception("No LCD found")

    def write_word(self, data):
        temp = data
        if self.blen == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.bus.writeto(self.addr, bytearray([temp]))
    
    def send_command(self, cmd):
        # Send bit7-4 firstly
        buf = cmd & 0xF0
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_word(buf)

        # Send bit3-0 secondly
        buf = (cmd & 0x0F) << 4
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_word(buf)
    
    def send_data(self, data):
        # Send bit7-4 firstly
        buf = data & 0xF0
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_word(buf)

        # Send bit3-0 secondly
        buf = (data & 0x0F) << 4
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self.write_word(buf)
        time.sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.write_word(buf)
    
    def clear(self):
        self.send_command(0x01) # Clear Screen
        
    def openlight(self):  # Enable the backlight
        self.bus.writeto(self.addr,bytearray([0x08]))
        # self.bus.close()
    
    def write(self, x, y, str):
        if x < 0:
            x = 0
        if x > 15:
            x = 15
        if y < 0:
            y = 0
        if y > 1:
            y = 1

        # Move cursor
        addr = 0x80 + 0x40 * y + x
        self.send_command(addr)

        for chr in str:
            self.send_data(ord(chr))
    
    def message(self, text):
        #print("message: %s"%text)
        for char in text:
            if char == '\n':
                self.send_command(0xC0) # next line
            else:
                self.send_data(ord(char))