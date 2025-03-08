from simple_umqtt import MQTTClient
import utime as time
import network
import binascii
import machine
import uasyncio as asyncio

# Publish test messages e.g. with:
# mosquitto_pub -t foo_topic -m hello


def connectToNetwork(ssid:str, password:str):
    print("Initiating connection to wifi ...")
    wlan = network.WLAN(network.STA_IF) # station interface mode
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("Connecting, please wait ....")
        time.sleep_ms(1000)
    myIp = wlan.ifconfig()[0]
    print("Connected! IP= ", myIp)

 
# Received messages from subscriptions will be delivered to this callback
def sub_cb(topic, msg):
    from lcd1602topteckboy import LCD
    topic = topic.decode()
    msg = msg.decode()
    print(f"{topic=}, {msg=}")
    lcd = LCD()
    lcd.clear()
    if(msg == "cls"):
        return
    lcd.write(0,0, msg)

def sub_loop(c:MQTTClient, topic:bytes = b"topic"):
    try:
        c.set_callback(sub_cb)
        c.connect()
        print("Connection succefull")
        print(f"Connected to Brocker at {c.server}: {1883} (Mosquitto) ....")
        c.subscribe(topic)
        print(f"Subscribed to {topic}, waiting for message....")
        while True:
            if False: # if true then it will block excection 
                # Blocking wait for message
                c.wait_msg()
            else:
                # Non-blocking wait for message
                c.check_msg()
                # Then need to sleep to avoid 100% CPU usage (in a real
                # app other useful actions would be performed instead)
                time.sleep_ms(100)

        c.disconnect()
    except Exception as e:
        c.disconnect()
        print("Error occured: ", e)

def pub_loop(c:MQTTClient, topic:bytes = b"topic"):
    try:
        c.connect()
        print("Connected to %s, waiting for command" % c.server)
        while True:
            command = input(":>> ")
            c.publish(topic, command.encode())
            time.sleep_ms(100)

        c.disconnect()
    except Exception as e:
        c.disconnect()
        print("Error occured: ", e)


def main(serverAddress:str="localhost", clientId: bytes=b"umqtt_client"):
    c = MQTTClient(client_id=clientId, server=serverAddress)
    topic = b"OMOSH"
    sub_loop(c,topic)




if __name__ == "__main__":
    connectToNetwork(ssid="Omosh", password="password")
    CLIENT_ID = binascii.hexlify(machine.unique_id())
    SERVER = "192.168.1.102"
    main(serverAddress=SERVER, clientId=CLIENT_ID, )
