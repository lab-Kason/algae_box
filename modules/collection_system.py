"""
Auto-Shovel Collection System
Controls gravity-based algae collection mechanism
"""
import time
from typing import Optional
import config


class CollectionSystem:
    """
    Controls the auto-shovel collection mechanism:
    1. Close valve -> stop water flow
    2. Wait for settling (gravity pulls algae down)
    3. Open shovel -> collect settled algae at bottom
    4. Close shovel
    5. Open valve -> resume normal flow
    """
    
    def __init__(self, simulation_mode: bool = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        self.last_collection_time = 0
        self.is_collecting = False
        
        if not self.simulation_mode:
            self._init_hardware()
        else:
            print("🔬 Collection system initialized in SIMULATION mode")
    
    def _init_hardware(self):
        """Initialize GPIO pins for valve and shovel"""
        try:
            # TODO: Initialize GPIO
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(config.VALVE_PIN, GPIO.OUT)
            # GPIO.setup(config.SHOVEL_PIN, GPIO.OUT)
            # # Start with valve open (normal flow)
            # GPIO.output(config.VALVE_PIN, GPIO.HIGH)
            # GPIO.output(config.SHOVEL_PIN, GPIO.LOW)
            print("✅ Collection hardware initialized")
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
        print("🌊 STARTING MULTI-CYCLE COLLECTION SEQUENCE")
        print(f"   {config.COLLECTION_CYCLES} cycles for thorough harvesting")
        print("="*50)
        
        try:
            # Step 1: Close valve ONCE at the start
            print("1️⃣  Closing valve to stop water flow...")
            self._close_valve()
            time.sleep(2)
            
            # Multiple collection cycles
            for cycle in range(1, config.COLLECTION_CYCLES + 1):
                print(f"\n🔄 CYCLE {cycle}/{config.COLLECTION_CYCLES}")
                print("-" * 50)
                
                # Wait for settling
                print(f"   ⏳ Waiting {config.SETTLING_TIME}s for algae to settle...")
                if self.simulation_mode:
                    for i in range(3):
                        time.sleep(1)
                        print(f"      Settling... {i+1}s / {config.SETTLING_TIME}s (fast-forward in sim)")
                else:
                    time.sleep(config.SETTLING_TIME)
                
                # Open shovel to collect
                print(f"   🥄 Opening shovel to collect settled algae...")
                self._open_shovel()
                time.sleep(config.SHOVEL_OPEN_TIME)
                
                # Close shovel
                print(f"   ✅ Closing shovel (cycle {cycle} complete)")
                self._close_shovel()
                
                # Wait between cycles (except after last cycle)
                if cycle < config.COLLECTION_CYCLES:
                    print(f"   ⏸️  Waiting {config.CYCLE_INTERVAL}s before next cycle...")
                    print(f"      (Allows disturbed algae to re-settle)")
                    time.sleep(config.CYCLE_INTERVAL)
            
            # Final step: Open valve to resume flow
            print("\n" + "-" * 50)
            print("5️⃣  Opening valve to resume water flow...")
            self._open_valve()
            
            self.last_collection_time = time.time()
            print("✅ ALL CYCLES COMPLETE! Tank thoroughly harvested.")
            print("="*50 + "\n")
            
            return {
                'success': True,
                'message': f'Collection completed successfully ({config.COLLECTION_CYCLES} cycles)',
                'timestamp': time.time(),
                'cycles': config.COLLECTION_CYCLES
            }
            
        except Exception as e:
            print(f"❌ Collection failed: {e}")
            # Emergency: try to restore normal state
            self._open_valve()
            self._close_shovel()
            return {
                'success': False,
                'message': f'Collection failed: {e}'
            }
        finally:
            self.is_collecting = False
    
    def _close_valve(self):
        """Close valve to stop water flow"""
        if self.simulation_mode:
            print("   [SIM] Valve closed (flow stopped)")
        else:
            # TODO: Control valve GPIO
            # GPIO.output(config.VALVE_PIN, GPIO.LOW)
            pass
    
    def _open_valve(self):
        """Open valve to resume water flow"""
        if self.simulation_mode:
            print("   [SIM] Valve opened (flow resumed)")
        else:
            # TODO: Control valve GPIO
            # GPIO.output(config.VALVE_PIN, GPIO.HIGH)
            pass
    
    def _open_shovel(self):
        """Open shovel to collect algae"""
        if self.simulation_mode:
            print("   [SIM] Shovel opened (collecting algae)")
        else:
            # TODO: Control shovel servo/motor
            # Could be a servo at specific angle or DC motor
            # GPIO.output(config.SHOVEL_PIN, GPIO.HIGH)
            pass
    
    def _close_shovel(self):
        """Close shovel"""
        if self.simulation_mode:
            print("   [SIM] Shovel closed")
        else:
            # TODO: Control shovel GPIO
            # GPIO.output(config.SHOVEL_PIN, GPIO.LOW)
            pass
    
    def get_status(self) -> dict:
        """Get collection system status"""
        return {
            'is_collecting': self.is_collecting,
            'can_collect': self.can_collect(),
            'time_since_last_collection_min': (time.time() - self.last_collection_time) / 60,
            'mode': 'simulation' if self.simulation_mode else 'real'
        }
    
    def emergency_stop(self):
        """Emergency stop - restore safe state"""
        print("🚨 EMERGENCY STOP")
        self._open_valve()
        self._close_shovel()
        self.is_collecting = False


if __name__ == "__main__":
    # Test collection system
    print("Testing Collection System...")
    collector = CollectionSystem()
    
    print("\n📊 Initial status:")
    print(collector.get_status())
    
    print("\n▶️  Starting test collection...")
    result = collector.start_collection(force=True)
    print(f"\nResult: {result}")
    
    print("\n📊 Final status:")
    print(collector.get_status())
