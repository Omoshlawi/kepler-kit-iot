from dht import DHT11 # Digital Humidity and Temperature sensor
from machine import Pin
import utime as time # time implementation for micropython


def readDHT11():
    import dht11_impl
    while True:
        time.sleep(5)
        pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
        sensor = dht11_impl.DHT11(pin)
        t  = (sensor.temperature)
        h = (sensor.humidity)
        print("Temperature: {}".format(sensor.temperature))
        print("Humidity: {}".format(sensor.humidity))

def readDHT11PredefinedLib():
    import dht
    while True:
        time.sleep(5)
        pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
        sensor = dht.DHT11(pin)
        sensor.measure()
        print("Temperature: {}".format(sensor.temperature))
        print("Humidity: {}".format(sensor.humidity))


def scanConnectListLogConfigAndDisconectWifi():
    import network
    if hasattr(network, "WLAN"):
        print("WLAN is available.")
        print("Scanning networks ...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        networks = wlan.scan()
        print("Available networks:")
        print("{:<4} {:<20} {:<10} {:<10} {:<10} {:<20} {}".format("#", "SSID", "Signal", "Security", "Channel", "BSSID(MAC)", "Hidden"))
        for i, n in enumerate(networks):
            bssid = ':'.join('{:02x}'.format(b) for b in n[1])
            print("{:<4} {:<20} {:<10} {:<10} {:<10} {:<20} {}".format(i+1, n[0].decode(), n[3], n[4], n[2], bssid, n[5]))

        print("Connecting to the network ...")
        wlan.connect("SSID", "PASSWORD")
        while not wlan.isconnected():
            print("Trying to connect to ", "Omosh", " ...")
            time.sleep(1)
            pass
        print("Connected to the network.")
        print("Network configuration: ", wlan.ifconfig())
    
        time.sleep(3600)
        print("Disconecting and forgeting network ...")
        wlan.disconnect()
        print("Network configuration: ", wlan.ifconfig())
        print("Network disconnected.")


def scanConnectListLogConfigAndDisconectBluetooth():
    import bluetooth
    import aioble
    print("Scanning bluetooth devices ...")
    bt = bluetooth.BLE()
    bt.active(True)
    mac_address = ':'.join('{:02x}'.format(b) for b in bt.config("mac")[1])
    print("Bluetooth MAC address:", mac_address)
    print("Scanning devices ...")


def lcd1602Display():
    from machine import I2C, Pin
    from lcd1602 import LCD
    import time
    import utime as time
    
    # Initialize I2C communication;
    print("Initialize I2C communication ...")
    i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=400000)

    # Create an LCD object for interfacing with the LCD1602 display
    print("Create an LCD object for interfacing with the LCD1602 display ...")
    lcd = LCD(i2c, 0x29)

    # Display the first message on the LCD
    # Use '\n' to create a new line.
    string = "SunFounder\n    LCD Tutorial"
    lcd.message(string)
    # Wait for 2 seconds
    time.sleep(2)
    # Clear the display
    lcd.clear()

    # Display the second message on the LCD
    string = "Hello\n  World!"
    lcd.message(string)
    # Wait for 5 seconds
    time.sleep(5)
    # Clear the display before exiting
    lcd.clear()

def lcd1602Display2():
    from lcd1602topteckboy import LCD
    from machine import I2C
    import utime as time
    
    upper = ['Juja', "Weitethie"]
    up = f"Current:{upper[0]} Next:{upper[1]} "
    
    stages = ["Allsops", "Juja", "Thika", "Weitethie", "Muthaiga", "Ruiru", "K-Roard", "KU", "Garden city", "Roysambu", "BuPass"]
    do = ", ".join(stages) + " "  # Adding space for smooth scrolling
    
    lcd = LCD()
    lcd.clear()
    
    up_index = 0
    do_index = 0
    up_length = len(up)
    do_length = len(do)

    while True:
        # Scroll first row
        lcd.write(0, 0, up[up_index:up_index + 16])  # Display 16 chars at a time
        up_index = (up_index + 1) % up_length  # Loop back when reaching the end
        
        # Scroll second row
        lcd.write(0, 1, do[do_index:do_index + 16])
        do_index = (do_index + 1) % do_length
        
        time.sleep(0.3)  # Adjust speed for smoother effect

if(__name__ == "__main__"):
    print("Starting ...")
    lcd1602Display2()