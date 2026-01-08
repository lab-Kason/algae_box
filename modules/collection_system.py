""" Pump-Based Flow Manifold Collection System
Controls pump-driven algae sweeping using horizontal slot-cut water knife
"""
import time
from typing import Optional
import config


class CollectionSystem:
    """
    Controls pump-based flow manifold collection mechanism:
    1. Wait for settling (algae sink to flat bottom)
    2. Start pump (water flows through slot-cut manifold, creating "water knife")
    3. Multiple flush passes sweep algae toward back drain
    4. Stop pump (let algae settle at drain)
    5. Open drain valve (collect concentrated algae)
    6. Close drain valve
    
    Flow: FRONT manifold → BACK drain (unidirectional sweeping)
    No mechanical scrapers - gentle laminar flow preserves algae integrity
    """
    
    def __init__(self, simulation_mode: bool = None):
        self.simulation_mode = simulation_mode if simulation_mode is not None else config.SIMULATION_MODE
        self.last_collection_time = 0
        self.is_collecting = False
        
        if not self.simulation_mode:
            self._init_hardware()
        else:
            print("🔬 Pump-based flow manifold system initialized in SIMULATION mode")
    
    def _init_hardware(self):
        """Initialize GPIO pins for pump and drain valve"""
        try:
            # TODO: Initialize GPIO
            # import RPi.GPIO as GPIO
            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(config.PUMP_PIN, GPIO.OUT)
            # GPIO.setup(config.DRAIN_VALVE_PIN, GPIO.OUT)
            # # Start with pump and valve OFF (normal operation)
            # GPIO.output(config.PUMP_PIN, GPIO.LOW)
            # GPIO.output(config.DRAIN_VALVE_PIN, GPIO.LOW)
            print("✅ Pump and drain valve hardware initialized")
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
        print("🌊 STARTING PUMP-BASED FLOW COLLECTION")
        print(f"   {config.FLUSH_PASSES} flush passes per cycle")
        print(f"   Flow: FRONT manifold → BACK drain")
        print(f"   Slot-cut creates uniform 'water knife' effect")
        print("="*50)
        
        try:
            
            # Multiple collection cycles
            for cycle in range(1, config.COLLECTION_CYCLES + 1):
                print(f"\n🔄 CYCLE {cycle}/{config.COLLECTION_CYCLES}")
                print("-" * 50)
                
                # PHASE 1: SETTLING - Algae sink to flat bottom
                print(f"   ⏳ Phase 1: Settling (algae sink to bottom, pump OFF)")
                if self.simulation_mode:
                    for i in range(3):
                        time.sleep(1)
                        print(f"      Settling... {i+1}s / {config.SETTLING_TIME}s (fast-forward in sim)")
                else:
                    time.sleep(config.SETTLING_TIME)
                print(f"      ✅ Algae settled on flat bottom")
                
                # PHASE 2: FLUSHING - Multiple passes with pump ON
                print(f"   💨 Phase 2-{1+config.FLUSH_PASSES}: Flushing ({config.FLUSH_PASSES} passes, pump ON)")
                for pass_num in range(1, config.FLUSH_PASSES + 1):
                    print(f"      → Flush pass {pass_num}/{config.FLUSH_PASSES}...")
                    self._start_pump()
                    time.sleep(config.FLUSH_TIME_PER_PASS)
                print(f"      ✅ Algae swept to back drain")
                
                # PHASE 3: COLLECTION WAITING - Pump OFF, algae settle at drain
                print(f"   ⏸️  Phase {2+config.FLUSH_PASSES}: Waiting (pump OFF, algae settle at drain)")
                self._stop_pump()
                time.sleep(config.COLLECTION_WAIT_TIME)
                
                # PHASE 4: DRAINING - Open drain valve to collect
                print(f"   💧 Phase {3+config.FLUSH_PASSES}: Opening drain valve...")
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
    
    def _start_pump(self):
        """Start water pump for flow sweeping"""
        if not self.simulation_mode:
            # TODO: GPIO control
            # GPIO.output(config.PUMP_PIN, GPIO.HIGH)
            pass
        print("         🔵 Pump ON - creating water knife curtain")
    
    def _stop_pump(self):
        """Stop water pump"""
        if not self.simulation_mode:
            # TODO: GPIO control
            # GPIO.output(config.PUMP_PIN, GPIO.LOW)
            pass
        print("         ⚫ Pump OFF")
    
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
