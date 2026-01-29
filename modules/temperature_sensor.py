"""
Temperature Sensor Module
Monitors water temperature
"""
import random
import time
import config


class TemperatureSensor:
    """Measures water temperature in Celsius"""
    
    def __init__(self, simulation_mode: bool = None, species_params: dict = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        
        # Use species-specific temperature or default
        if species_params and 'temp_optimal' in species_params:
            self.sim_base_temp = species_params['temp_optimal']
        else:
            self.sim_base_temp = config.TEMP_OPTIMAL
        
        if not self.simulation_mode:
            self._init_real_sensor()
        else:
            print("🔬 Temperature sensor initialized in SIMULATION mode")
    
    def _init_real_sensor(self):
        """Initialize DS18B20 1-Wire temperature sensor"""
        try:
            # DS18B20 uses 1-Wire protocol via GPIO4
            # Enable 1-Wire: sudo raspi-config → Interface Options → 1-Wire → Enable
            # Sensors appear in: /sys/bus/w1/devices/
            
            import glob
            
            # Find DS18B20 device
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28*')[0]  # DS18B20 starts with '28'
            self.device_file = device_folder + '/w1_slave'
            
            # Test reading
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
                if 'YES' in lines[0]:
                    print("✅ DS18B20 1-Wire temperature sensor initialized")
                    print(f"   Device: {device_folder.split('/')[-1]}")
                else:
                    raise Exception("Sensor not responding correctly")
                    
        except IndexError:
            print("❌ DS18B20 not found. Is 1-Wire enabled?")
            print("   Run: sudo raspi-config → Interface → 1-Wire → Enable")
            print("   Check wiring: GPIO4, 3.3V, GND, 4.7kΩ pullup resistor")
            print("   Falling back to simulation mode")
            self.simulation_mode = True
        except Exception as e:
            print(f"❌ Failed to initialize DS18B20: {e}")
            print("   Falling back to simulation mode")
            self.simulation_mode = True
    
    def read_celsius(self) -> float:
        """Read temperature in Celsius"""
        if self.simulation_mode:
            return self._simulate_reading()
        else:
            return self._read_real_sensor()
    
    def _simulate_reading(self) -> float:
        """Simulate temperature with small variations"""
        # Small random fluctuation around optimal
        variation = random.uniform(-config.SIM_TEMP_VARIATION, config.SIM_TEMP_VARIATION)
        temp = self.sim_base_temp + variation
        return round(temp, 1)
    
    def _read_real_sensor(self) -> float:
        """Read from DS18B20 1-Wire temperature sensor"""
        try:
            # Read raw data from sensor file
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
            
            # Check if reading is valid (CRC check passed)
            if 'YES' not in lines[0]:
                print("⚠️  DS18B20 CRC check failed, retrying...")
                return self._read_real_sensor()  # Retry
            
            # Extract temperature from second line
            # Format: "... t=23500" (temperature in millidegrees Celsius)
            temp_pos = lines[1].find('t=')
            if temp_pos != -1:
                temp_string = lines[1][temp_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return round(temp_c, 1)
            else:
                print("⚠️  Could not parse DS18B20 temperature")
                return 25.0
                
        except Exception as e:
            print(f"❌ Error reading DS18B20: {e}")
            return 25.0
    
    def is_safe_range(self) -> bool:
        """Check if temperature is in safe range"""
        temp = self.read_celsius()
        return config.TEMP_MIN_SAFE <= temp <= config.TEMP_MAX_SAFE
    
    def get_status(self) -> dict:
        """Get temperature status"""
        temp = self.read_celsius()
        return {
            'temperature_c': temp,
            'safe': self.is_safe_range(),
            'mode': 'simulation' if self.simulation_mode else 'real'
        }
