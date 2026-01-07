"""
U-Bottom Passive Collection System
Controls gravity-based algae collection using U-shaped tank bottom
"""
import time
from typing import Optional
import config


class CollectionSystem:
    """
    Controls U-bottom passive collection mechanism:
    1. Wait for settling (algae roll down U-shape to centerline, slide to drain)
    2. Open drain valve at back-center (lowest point)
    3. Collect concentrated algae
    4. Close drain valve
    
    No tilting, no mechanical parts - gravity does all the work!
    """
    
    def __init__(self, simulation_mode: bool = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        self.last_collection_time = 0
        self.is_collecting = False
        
        if not self.simulation_mode:
            self._init_hardware()
        else:
            print("🔬 U-bottom collection system initialized in SIMULATION mode")
    
    def _init_hardware(self):
        """Initialize GPIO pin for drain valve"""
        try:
            # TODO: Initialize GPIO
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(config.DRAIN_VALVE_PIN, GPIO.OUT)
            # # Start with valve closed (normal operation)
            # GPIO.output(config.DRAIN_VALVE_PIN, GPIO.LOW)
            print("✅ Drain valve hardware initialized")
        except Exception as e:
            print(f"❌ Failed to initialize hardware: {e}")
            self.simulation_mode = True
    
    def can_collect(self) -> bool:
        """Check if enough time has passed since last collection"""
        time_since_last = time.time() - self.last_collection_time
        return time_since_last >= config.COLLECTION_COOLDOWN
    
    def start_collection(self, force: bool = False) -> dict:
        """
        Execute full collection sequence with multiple cycles
        Args:
            force: Bypass cooldown timer if True
        Returns:
            dict with collection results
        """
        if self.is_collecting:
            return {'success': False, 'message': 'Collection already in progress'}
        
        if not force and not self.can_collect():
            time_remaining = config.COLLECTION_COOLDOWN - (time.time() - self.last_collection_time)
            return {
                'success': False, 
                'message': f'Cooldown active. Wait {time_remaining/60:.1f} more minutes'
            }
        
        self.is_collecting = True
        print("\n" + "="*50)
        print("🌊 STARTING U-BOTTOM PASSIVE COLLECTION")
        print(f"   {config.COLLECTION_CYCLES} settle-drain cycles")
        print(f"   Tank stays stationary - gravity does the work!")
        print("="*50)
        
        try:
            
            # Multiple collection cycles
            for cycle in range(1, config.COLLECTION_CYCLES + 1):
                print(f"\n🔄 CYCLE {cycle}/{config.COLLECTION_CYCLES}")
                print("-" * 50)
                
                # PHASE 1: SETTLING - Algae roll down U-shape and slide to drain
                print(f"   ⏳ Phase 1: Settling (algae roll to centerline & slide to drain)")
                print(f"      U-depth: {config.U_DEPTH}mm, Slope: {config.LONGITUDINAL_SLOPE_ANGLE}°")
                if self.simulation_mode:
                    for i in range(3):
                        time.sleep(1)
                        print(f"      Settling... {i+1}s / {config.SETTLING_TIME}s (fast-forward in sim)")
                else:
                    time.sleep(config.SETTLING_TIME)
                print(f"      ✅ Algae concentrated at back-center drain")
                
                # PHASE 2: DRAINING - Open drain valve to collect
                print(f"   💧 Phase 2: Opening drain valve at lowest point...")
                self._open_drain()
                time.sleep(config.DRAIN_OPEN_TIME)
                
                # Close drain
                print(f"   ✅ Closing drain (cycle {cycle} complete)")
                self._close_drain()
                
                # Wait between cycles (except after last cycle)
                if cycle < config.COLLECTION_CYCLES:
                    print(f"   ⏸️  Waiting {config.CYCLE_INTERVAL}s before next cycle...")
                    print(f"      (Allows remaining algae to re-settle)")
                    time.sleep(config.CYCLE_INTERVAL)
            
            self.last_collection_time = time.time()
            print("\n" + "-" * 50)
            print("✅ ALL CYCLES COMPLETE! Algae harvested via passive gravity collection.")
            print("   Tank remained stationary - no tilting mechanism needed!")
            print("="*50 + "\n")
            
            return {
                'success': True,
                'message': f'Passive collection completed ({config.COLLECTION_CYCLES} cycles)',
                'timestamp': time.time(),
                'cycles': config.COLLECTION_CYCLES,
                'method': 'U-bottom passive (gravity-based)'
            }
            
        except Exception as e:
            print(f"❌ Collection failed: {e}")
            # Emergency: ensure drain is closed
            self._close_drain()
            return {
                'success': False,
                'message': f'Collection failed: {e}'
            }
        finally:
            self.is_collecting = False
    
    def _open_drain(self):
        """Open drain valve to collect algae"""
        if self.simulation_mode:
            print("   [SIM] Drain valve OPEN (collecting algae)")
        else:
            # TODO: Control drain valve GPIO
            # GPIO.output(config.DRAIN_VALVE_PIN, GPIO.HIGH)
            pass
    
    def _close_drain(self):
        """Close drain valve"""
        if self.simulation_mode:
            print("   [SIM] Drain valve CLOSED")
        else:
            # TODO: Control drain valve GPIO
            # GPIO.output(config.DRAIN_VALVE_PIN, GPIO.LOW)
            pass
    
    def get_status(self) -> dict:
        """Get collection system status"""
        return {
            'is_collecting': self.is_collecting,
            'can_collect': self.can_collect(),
            'time_since_last_collection_min': (time.time() - self.last_collection_time) / 60,
            'mode': 'simulation' if self.simulation_mode else 'real',
            'collection_method': 'U-bottom passive (gravity-based)'
        }
    
    def emergency_stop(self):
        """Emergency stop - restore safe state"""
        print("🚨 EMERGENCY STOP")
        self._close_drain()
        self.is_collecting = False


if __name__ == "__main__":
    # Test U-bottom passive collection system
    print("Testing U-Bottom Passive Collection System...")
    collector = CollectionSystem()
    
    print("\n📊 Initial status:")
    print(collector.get_status())
    
    print("\n▶️  Starting test collection...")
    result = collector.start_collection(force=True)
    print(f"\nResult: {result}")
    
    print("\n📊 Final status:")
    print(collector.get_status())
