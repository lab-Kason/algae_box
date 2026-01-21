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
        """Initialize DS18B20 or similar"""
        # TODO: Initialize 1-wire temperature sensor
        print("✅ Real temperature sensor initialized")
    
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
        """Read from real temperature sensor"""
        # TODO: Implement DS18B20 reading
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
