from machine import Pin, UART
import utime
from  gps_module import GPSModule
        
if __name__ == "__main__":
    gps = GPSModule()
    
    while True:
        if gps.update():
            data = gps.get_all_data()
            location = data['location']
            print(f"Location: {location}" )
            satelite = data['satellites']['satellites_in_view'] if data['satellites'] else None
            print(f"Satellites in view: {satelite}", )
            print(f"Data: {data}")
        utime.sleep_ms(100)
    
