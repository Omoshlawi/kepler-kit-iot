import network
import urequests
import utime
import usocket as socket

ssid = "ssid"
password = "password"

def connectToMyWifi():
    """
    Establishes a WiFi connection using the specified SSID and password.
    Uses station interface mode to connect to WiFi network. Blocks until 
    connection is established, printing status messages during connection attempt.
    Returns:
        None
    """

    print("Initiating connection to wifi ...")
    wlan = network.WLAN(network.STA_IF) # station interface mode
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("Connecting, please wait ....")
        utime.sleep_ms(1000)
    print("Connected! IP= ", wlan.ifconfig()[0])

def setUpWirelesAccesspoint():
    
    print("Setting up wireless access point on pico ...")
    accessPoint = network.WLAN(network.AP_IF) # Wireless Access Point
    accessPoint.config(ssid=ssid, password=password)
    accessPoint.active(True)
    while not accessPoint.isconnected():
        print("Waiting for Connections ....")
        utime.sleep_ms(1000)
    print("Connected! IP= ", accessPoint.ifconfig()[0])  



def queryInternetResource():
    try:
        connectToMyWifi()
        site = "https://jsonplaceholder.typicode.com/todos/1"
        print("query: ", site)
        r = urequests.get(site)
        print(r.json())
        r.close()
    except Exception as e:
        print("Error: Connection closed", e)

def open_socket():
    addr = socket.getaddrinfo("0.0.0.0", 80)
    address = addr[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(address) # Address is tuple with ip and port to bind,can be replaced by ("0.0.0.0", 80)
    s.listen(3) # Allow 3 connections
    print(f"Listing for incoming connections ...")
    return s

def setUpWebServer(setUpAccessPoint:bool = False):
    try: 
        if(setUpAccessPoint):
            setUpWirelesAccesspoint()
        else: 
            connectToMyWifi()
        s = open_socket()
        while True: 
            clientSockConnection, clieAddress = s.accept()
            print(f"Connected succesfully from {clieAddress[0]}:{clieAddress[1]}", )
            req = clientSockConnection.recv(1024).decode()
            # Send headers
            # send html body
            # Close connection
            clientSockConnection.send('Thank you for connecting'.encode())
            print(req)
            clientSockConnection.close()

    except Exception as e:
        clientSockConnection.close()
        print("Error", e)


setUpWebServer(True)