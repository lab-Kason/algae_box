"""
Turbidity Sensor Module
Supports both real sensor and simulation mode
"""
import random
import time
from typing import Optional
import config


class TurbiditySensor:
    """
    Measures water turbidity (cloudiness) in NTU units.
    Higher turbidity = more algae in water.
    """
    
    def __init__(self, simulation_mode: bool = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        self.start_time = time.time()
        self.sim_base_turbidity = 10.0  # Starting turbidity for simulation
        self.last_collection_time = None  # Track when collection happened
        
        if not self.simulation_mode:
            self._init_real_sensor()
        else:
            print("🔬 Turbidity sensor initialized in SIMULATION mode")
    
    def _init_real_sensor(self):
        """Initialize real hardware sensor (when you get it)"""
        try:
            # TODO: Initialize ADC and sensor pin
            # Example for MCP3008:
            # import busio
            # import digitalio
            # import board
            # import adafruit_mcp3xxx.mcp3008 as MCP
            # from adafruit_mcp3xxx.analog_in import AnalogIn
            # 
            # spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            # cs = digitalio.DigitalInOut(board.D5)
            # mcp = MCP.MCP3008(spi, cs)
            # self.channel = AnalogIn(mcp, MCP.P0)
            print("✅ Real turbidity sensor initialized")
        except Exception as e:
            print(f"❌ Failed to initialize real sensor: {e}")
            print("   Falling back to simulation mode")
            self.simulation_mode = True
    
    def read_ntu(self) -> float:
        """
        Read turbidity in NTU (Nephelometric Turbidity Units)
        Returns: turbidity value (0-200 NTU typical range)
        """
        if self.simulation_mode:
            return self._simulate_reading()
        else:
            return self._read_real_sensor()
    
    def _simulate_reading(self) -> float:
        """
        Simulate algae growth over time
        - Starts low
        - Gradually increases (algae multiplying)
        - Adds realistic noise
        - Reduces after collection
        """
        elapsed_minutes = (time.time() - self.start_time) / 60
        
        # Simulate algae growth: exponential at first, then linear
        growth = config.SIM_ALGAE_GROWTH_RATE * elapsed_minutes
        
        # If collection happened, reduce turbidity
        if self.last_collection_time is not None:
            time_since_collection = (time.time() - self.last_collection_time) / 60
            # Multi-cycle collection removes more algae
            reduction_factor = config.TURBIDITY_REDUCTION_PER_CYCLE ** config.COLLECTION_CYCLES
            # Calculate what growth would have been at collection time
            growth_at_collection = config.SIM_ALGAE_GROWTH_RATE * ((self.last_collection_time - self.start_time) / 60)
            # Apply reduction and then add new growth since collection
            growth = (growth_at_collection * reduction_factor) + (config.SIM_ALGAE_GROWTH_RATE * time_since_collection)
        
        # Add random fluctuation (mimics real sensor noise)
        noise = random.uniform(-config.SIM_TURBIDITY_NOISE, config.SIM_TURBIDITY_NOISE)
        
        turbidity = self.sim_base_turbidity + growth + noise
        
        # Clamp to realistic range
        turbidity = max(config.TURBIDITY_MIN, min(turbidity, config.TURBIDITY_MAX))
        
        return round(turbidity, 2)
    
    def _read_real_sensor(self) -> float:
        """Read from actual hardware sensor"""
        try:
            # TODO: Read voltage from ADC and convert to NTU
            # Typical conversion (varies by sensor model):
            # voltage = self.channel.voltage
            # ntu = self._voltage_to_ntu(voltage)
            # return ntu
            pass
        except Exception as e:
            print(f"❌ Error reading sensor: {e}")
            return 0.0
    
    def _voltage_to_ntu(self, voltage: float) -> float:
        """
        Convert sensor voltage to NTU
        Calibration curve depends on your specific sensor
        This is a placeholder - you'll calibrate with known standards
        """
        # Example calibration (adjust based on your sensor datasheet)
        # Many sensors: High voltage = low turbidity
        if voltage > 4.5:
            return 0  # Clear water
        elif voltage < 2.5:
            return 200  # Very cloudy
        else:
            # Linear interpolation (real curve may be non-linear)
            return (4.5 - voltage) / 2.0 * 200
    
    def is_harvest_ready(self, threshold: Optional[float] = None) -> bool:
        """
        Check if turbidity exceeds harvest threshold
        Args:
            threshold: Custom threshold in NTU (uses config default if None)
        Returns:
            True if ready to harvest
        """
        if threshold is None:
            threshold = config.TURBIDITY_HARVEST_THRESHOLD
        
        current = self.read_ntu()
        return current >= threshold
    
    def get_status(self) -> dict:
        """Get detailed sensor status"""
        turbidity = self.read_ntu()
        return {
            'turbidity_ntu': turbidity,
            'harvest_ready': self.is_harvest_ready(),
            'mode': 'simulation' if self.simulation_mode else 'real',
            'threshold': config.TURBIDITY_HARVEST_THRESHOLD
        }
    
    def simulate_collection(self):
        """Called by main system when collection happens to update simulation"""
        if self.simulation_mode:
            self.last_collection_time = time.time()
            print(f"   📉 Turbidity sensor: Simulating {config.COLLECTION_CYCLES}-cycle collection effect")


if __name__ == "__main__":
    # Test the sensor
    print("Testing Turbidity Sensor...")
    sensor = TurbiditySensor()
    
    for i in range(5):
        status = sensor.get_status()
        print(f"\n📊 Reading {i+1}:")
        print(f"   Turbidity: {status['turbidity_ntu']:.2f} NTU")
        print(f"   Harvest ready: {status['harvest_ready']}")
        print(f"   Mode: {status['mode']}")
        time.sleep(2)
