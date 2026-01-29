"""
pH Sensor Module
Monitors water acidity/alkalinity
"""
import random
import time
import config


class PHSensor:
    """Measures water pH (0-14 scale, 7 is neutral)"""
    
    def __init__(self, simulation_mode: bool = None, species_params: dict = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        self.start_time = time.time()
        
        # Use species-specific pH or default
        if species_params and 'ph_optimal' in species_params:
            self.sim_base_ph = species_params['ph_optimal']
        else:
            self.sim_base_ph = config.PH_OPTIMAL
        
        if not self.simulation_mode:
            self._init_real_sensor()
        else:
            print("🔬 pH sensor initialized in SIMULATION mode")
    
    def _init_real_sensor(self):
        """Initialize Atlas Scientific EZO-pH I2C sensor"""
        try:
            # Atlas Scientific EZO-pH Sensor
            # I2C Address: 0x63 (default)
            # Install: pip3 install smbus2
            
            import smbus2
            import time
            
            self.i2c_bus = smbus2.SMBus(1)  # I2C bus 1 on Raspberry Pi
            self.i2c_address = 0x63  # Atlas Scientific EZO-pH default
            
            # Test sensor connection - send 'I' (info) command
            self.i2c_bus.write_byte(self.i2c_address, ord('I'))
            time.sleep(0.3)  # Wait for response
            
            print("✅ Atlas Scientific EZO-pH I2C sensor initialized")
            print(f"   I2C Address: 0x{self.i2c_address:02x}")
            print("   Calibration data stored in sensor EEPROM")
            
        except Exception as e:
            print(f"❌ Failed to initialize I2C pH sensor: {e}")
            print("   Make sure sensor is connected to I2C bus")
            print("   Run: sudo i2cdetect -y 1")
            print("   Falling back to simulation mode")
            self.simulation_mode = True
    
    def read_ph(self) -> float:
        """Read pH value (0-14)"""
        if self.simulation_mode:
            return self._simulate_reading()
        else:
            return self._read_real_sensor()
    
    def _simulate_reading(self) -> float:
        """Simulate pH drift over time"""
        elapsed_minutes = (time.time() - self.start_time) / 60
        
        # pH drifts slightly as algae photosynthesize (consume CO2)
        drift = config.SIM_PH_DRIFT * elapsed_minutes
        noise = random.uniform(-0.1, 0.1)
        
        ph = self.sim_base_ph + drift + noise
        
        # Keep in realistic range
        ph = max(6.0, min(ph, 9.0))
        return round(ph, 2)
    
    def _read_real_sensor(self) -> float:
        """Read from Atlas Scientific EZO-pH I2C sensor"""
        try:
            import time
            
            # Send 'R' (read) command to sensor
            self.i2c_bus.write_byte(self.i2c_address, ord('R'))
            
            # Wait for sensor to process (Atlas Scientific needs ~900ms)
            time.sleep(1.0)
            
            # Read response (up to 31 bytes)
            response = self.i2c_bus.read_i2c_block_data(self.i2c_address, 0, 31)
            
            # First byte is status code
            # 1 = success, 2 = syntax error, 254 = still processing, 255 = no data
            if response[0] == 1:
                # Convert bytes to string, remove null bytes
                ph_string = ''.join(chr(b) for b in response[1:] if b != 0)
                ph_value = float(ph_string)
                return round(ph_value, 2)
            else:
                print(f"⚠️  pH sensor returned status code: {response[0]}")
                return 7.0
                
        except Exception as e:
            print(f"❌ Error reading I2C pH sensor: {e}")
            return 7.0
    
    def is_safe_range(self) -> bool:
        """Check if pH is in safe range for algae"""
        ph = self.read_ph()
        return config.PH_MIN_SAFE <= ph <= config.PH_MAX_SAFE
    
    def get_status(self) -> dict:
        """Get pH status"""
        ph = self.read_ph()
        return {
            'ph': ph,
            'safe': self.is_safe_range(),
            'mode': 'simulation' if self.simulation_mode else 'real'
        }
