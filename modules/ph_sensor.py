"""
pH Sensor Module
Monitors water acidity/alkalinity
"""
import random
import time
import config


class PHSensor:
    """Measures water pH (0-14 scale, 7 is neutral)"""
    
    def __init__(self, simulation_mode: bool = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        self.start_time = time.time()
        self.sim_base_ph = config.PH_OPTIMAL
        
        if not self.simulation_mode:
            self._init_real_sensor()
        else:
            print("🔬 pH sensor initialized in SIMULATION mode")
    
    def _init_real_sensor(self):
        """Initialize real pH probe"""
        # TODO: Initialize ADC for pH probe
        print("✅ Real pH sensor initialized")
    
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
        """Read from real pH probe"""
        # TODO: Implement real sensor reading
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
