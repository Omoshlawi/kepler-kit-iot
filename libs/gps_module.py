from machine import UART, Pin
from collections import namedtuple
import utime

# Define data structures for different NMEA sentence types
GPGGA = namedtuple('GPGGA', ['timestamp', 'latitude', 'lat_direction', 
                            'longitude', 'lon_direction', 'fix_quality',
                            'num_satellites', 'hdop', 'altitude', 
                            'altitude_units', 'geoid_separation',
                            'geoid_units', 'age_dgps', 'dgps_id'])

GPRMC = namedtuple('GPRMC', ['timestamp', 'status', 'latitude', 'lat_direction',
                            'longitude', 'lon_direction', 'speed_knots',
                            'true_course', 'date', 'magnetic_variation',
                            'variation_direction', 'mode_indicator'])

GPVTG = namedtuple('GPVTG', ['true_track', 't', 'magnetic_track', 'm',
                            'speed_knots', 'n', 'speed_kmh', 'k', 'mode'])

GPGSV = namedtuple('GPGSV', ['total_messages', 'message_num', 'satellites_in_view',
                            'satellites'])

SatelliteInfo = namedtuple('SatelliteInfo', ['prn', 'elevation', 'azimuth', 'snr'])

class GPSModule:
    def __init__(self, uart_id=0, baudrate=9600, tx_pin=0, rx_pin=1):
        """
        Initialize the GPS parser with UART configuration.
        
        Args:
            uart_id: UART interface ID (default 0)
            baudrate: Baud rate for GPS communication (default 9600)
            tx_pin: TX pin number (default 0)
            rx_pin: RX pin number (default 1)
        """
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.buffer = ''
        self.last_valid_data = {
            'GGA': None,
            'RMC': None,
            'VTG': None,
            'GSV': None
        }
        
    def update(self):
        """
        Read data from UART and process NMEA sentences.
        Returns True if new valid data was processed.
        """
        new_data = False
        
        while self.uart.any():
            try:
                data = self.uart.read().decode('utf-8') # type:ignore
                self.buffer += data
                # Process complete sentences from buffer
                while '\r\n' in self.buffer:
                    sentence, self.buffer = self.buffer.split('\r\n', 1)
                    if self._validate_checksum(sentence):
                        self._parse_nmea_sentence(sentence)
                        new_data = True
                        
            except UnicodeError:
                # Handle decoding errors
                self.buffer = ''
                
        return new_data
    
    def _validate_checksum(self, sentence):
        """
        Validate NMEA sentence checksum.
        
        Args:
            sentence: Complete NMEA sentence including $ and *checksum
            
        Returns:
            bool: True if checksum is valid
        """
        if not sentence.startswith('$') or '*' not in sentence:
            return False
            
        try:
            data, checksum = sentence[1:].split('*')
            calculated = 0
            for char in data:
                calculated ^= ord(char)
            return f"{calculated:02X}" == checksum.upper()
        except:
            return False
    
    def _parse_nmea_sentence(self, sentence):
        """
        Parse a valid NMEA sentence and update last_valid_data.
        """
        try:
            sentence_type = sentence[3:6]  # Get sentence type (GGA, RMC, etc.)
            fields = sentence.split(',')
            
            if sentence_type == 'GGA':
                self.last_valid_data['GGA'] = self._parse_gga(fields) # type: ignore
            elif sentence_type == 'RMC':
                self.last_valid_data['RMC'] = self._parse_rmc(fields) # type: ignore
            elif sentence_type == 'VTG':
                self.last_valid_data['VTG'] = self._parse_vtg(fields) # type: ignore
            elif sentence_type == 'GSV':
                self._parse_gsv(fields)
        except Exception as e:
            # Silently handle parsing errors to maintain robustness
            pass
    
    def _parse_gga(self, fields):
        """Parse GGA (Global Positioning System Fix Data) sentence."""
        try:
            return GPGGA(
                timestamp=fields[1],
                latitude=fields[2],
                lat_direction=fields[3],
                longitude=fields[4],
                lon_direction=fields[5],
                fix_quality=fields[6],
                num_satellites=fields[7],
                hdop=fields[8],
                altitude=fields[9],
                altitude_units=fields[10],
                geoid_separation=fields[11],
                geoid_units=fields[12],
                age_dgps=fields[13] if len(fields) > 13 else '',
                dgps_id=fields[14] if len(fields) > 14 else ''
            )
        except:
            return None
    
    def _parse_rmc(self, fields):
        """Parse RMC (Recommended Minimum Specific GNSS Data) sentence."""
        try:
            return GPRMC(
                timestamp=fields[1],
                status=fields[2],
                latitude=fields[3],
                lat_direction=fields[4],
                longitude=fields[5],
                lon_direction=fields[6],
                speed_knots=fields[7],
                true_course=fields[8] if len(fields) > 8 else None,  # Bearing
                date=fields[9],
                magnetic_variation=fields[10] if len(fields) > 10 else '',
                variation_direction=fields[11] if len(fields) > 11 else '',
                mode_indicator=fields[12] if len(fields) > 12 else ''
            )
        except:
            return None
    
    def _parse_vtg(self, fields):
        """Parse VTG (Course Over Ground and Ground Speed) sentence."""
        try:
            return GPVTG(
                true_track=fields[1] if len(fields) > 1 else None,  # True bearing
                t=fields[2],
                magnetic_track=fields[3] if len(fields) > 3 else None,  # Magnetic bearing
                m=fields[4],
                speed_knots=fields[5],
                n=fields[6],
                speed_kmh=fields[7],
                k=fields[8],
                mode=fields[9] if len(fields) > 9 else ''
            )
        except:
            return None
    
    def _parse_gsv(self, fields):
        """Parse GSV (Satellites in View) sentence."""
        try:
            total_messages = int(fields[1])
            message_num = int(fields[2])
            satellites_in_view = int(fields[3])
            
            # Parse satellite info (4 satellites per message)
            satellites = []
            for i in range(4):
                idx = 4 + i*4
                if len(fields) > idx + 3 and fields[idx]:
                    satellites.append(SatelliteInfo(
                        prn=fields[idx],
                        elevation=fields[idx+1],
                        azimuth=fields[idx+2],
                        snr=fields[idx+3] if len(fields) > idx+3 else ''
                    ))
            
            # Initialize or update GSV data
            if self.last_valid_data['GSV'] is None or message_num == 1:
                self.last_valid_data['GSV'] = { # type: ignore
                    'total_messages': total_messages,
                    'satellites_in_view': satellites_in_view,
                    'satellites': satellites
                } 
            else:
                self.last_valid_data['GSV']['satellites'].extend(satellites)
        except:
            pass
    
    def get_location(self):
        """Get the latest location data from RMC or GGA sentences."""
        rmc = self.last_valid_data['RMC']
        gga = self.last_valid_data['GGA']
        vtg = self.last_valid_data['VTG']
        # Prefer VTG direction if available, fall back to RMC
        direction = None
        if vtg and vtg.true_track:
            direction = vtg.true_track
        elif rmc and rmc.true_course:
            direction = rmc.true_course
        
        if rmc and rmc.status == 'A':  # 'A' = Active, 'V' = Void  Prefer RMC if active
            return {
                'latitude': self._convert_to_decimal(rmc.latitude, rmc.lat_direction),
                'longitude': self._convert_to_decimal(rmc.longitude, rmc.lon_direction),
                'timestamp': rmc.timestamp,
                'date': rmc.date,
                'speed': rmc.speed_knots,
                'direction_degrees': direction
            }
        elif gga and gga.fix_quality != '0':  # 0 = invalid fix Fallback to GGA
            return {
                'latitude': self._convert_to_decimal(gga.latitude, gga.lat_direction),
                'longitude': self._convert_to_decimal(gga.longitude, gga.lon_direction),
                'timestamp': gga.timestamp,
                'altitude': gga.altitude,
                'direction_degrees': direction
            }
        return None
    
    def _convert_to_decimal(self, value, direction):
        """
        Convert NMEA latitude/longitude (DDMM.MMMM) to decimal degrees.
        
        Args:
            value: NMEA formatted coordinate string
            direction: 'N', 'S', 'E', or 'W'
            
        Returns:
            float: Decimal degrees coordinate
        """
        if not value or not direction:
            return None
            
        try:
            degrees = float(value[:2]) if direction in ['N', 'S'] else float(value[:3])
            minutes = float(value[2 if direction in ['N', 'S'] else 3:])
            decimal = degrees + (minutes / 60.0)
            if direction in ['S', 'W']:
                decimal *= -1
            return decimal
        except:
            return None
    
    def get_satellites(self):
        """Get satellite information from GSV sentences."""
        gsv = self.last_valid_data.get('GSV')
        if gsv:
            return {
                'satellites_in_view': gsv['satellites_in_view'],
                'satellites': gsv['satellites']
            }
        return None
    
    def get_all_data(self):
        """Get all parsed data as a dictionary."""
        return {
            'location': self.get_location(),
            'satellites': self.get_satellites(),
            'gga': self.last_valid_data['GGA'],
            'rmc': self.last_valid_data['RMC'],
            'vtg': self.last_valid_data['VTG'],
            'gsv': self.last_valid_data['GSV']
        }

# Example usage
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