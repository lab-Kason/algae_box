"""
Algae Box - Main Control System
Automated algae cultivation and collection
"""
import time
import csv
from datetime import datetime
from modules.turbidity_sensor import TurbiditySensor
from modules.ph_sensor import PHSensor
from modules.temperature_sensor import TemperatureSensor
from modules.collection_system import CollectionSystem
import config


class AlgaeBox:
    """Main controller for algae cultivation system"""
    
    def __init__(self):
        print("🌱 Initializing Algae Box System...")
        print(f"   Mode: {'SIMULATION' if config.SIMULATION_MODE else 'REAL HARDWARE'}")
        
        # Initialize sensors
        self.turbidity = TurbiditySensor()
        self.ph = PHSensor()
        self.temperature = TemperatureSensor()
        self.collector = CollectionSystem()
        
        # Initialize data logging
        self._init_logging()
        
        print("✅ System initialized!\n")
    
    def _init_logging(self):
        """Create CSV log file with headers"""
        try:
            with open(config.LOG_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'turbidity_ntu', 'ph', 'temperature_c',
                    'harvest_ready', 'collection_triggered', 'notes'
                ])
            print(f"📝 Logging to: {config.LOG_FILE}")
        except Exception as e:
            print(f"⚠️  Could not create log file: {e}")
    
    def read_all_sensors(self) -> dict:
        """Read all sensor values"""
        return {
            'turbidity': self.turbidity.get_status(),
            'ph': self.ph.get_status(),
            'temperature': self.temperature.get_status(),
            'collector': self.collector.get_status()
        }
    
    def log_data(self, data: dict, collection_triggered: bool = False, notes: str = ""):
        """Log sensor data to CSV"""
        try:
            with open(config.LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    data['turbidity']['turbidity_ntu'],
                    data['ph']['ph'],
                    data['temperature']['temperature_c'],
                    data['turbidity']['harvest_ready'],
                    collection_triggered,
                    notes
                ])
        except Exception as e:
            print(f"⚠️  Logging error: {e}")
    
    def display_status(self, data: dict):
        """Display current system status"""
        print("\n" + "="*60)
        print(f"📊 SYSTEM STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # Turbidity
        turb = data['turbidity']
        print(f"💧 Turbidity: {turb['turbidity_ntu']:.2f} NTU", end="")
        if turb['harvest_ready']:
            print(" ⚠️  HARVEST THRESHOLD REACHED!")
        else:
            remaining = config.TURBIDITY_HARVEST_THRESHOLD - turb['turbidity_ntu']
            print(f" ({remaining:.1f} NTU until harvest)")
        
        # pH
        ph = data['ph']
        status = "✅" if ph['safe'] else "❌"
        print(f"🧪 pH: {ph['ph']:.2f} {status}")
        
        # Temperature
        temp = data['temperature']
        status = "✅" if temp['safe'] else "❌"
        print(f"🌡️  Temperature: {temp['temperature_c']:.1f}°C {status}")
        
        # Collection system
        coll = data['collector']
        if coll['is_collecting']:
            print("🔄 Collection: IN PROGRESS")
        elif coll['can_collect']:
            print("✅ Collection: READY")
        else:
            print(f"⏳ Collection: Cooldown ({coll['time_since_last_collection_min']:.1f} min)")
        
        print("="*60)
    
    def check_and_collect(self, data: dict) -> bool:
        """
        Check if collection should be triggered
        Returns: True if collection was performed
        """
        turb = data['turbidity']
        ph = data['ph']
        temp = data['temperature']
        
        # Check conditions for safe collection
        if not turb['harvest_ready']:
            return False
        
        if not ph['safe']:
            print("⚠️  pH out of range - skipping collection for safety")
            return False
        
        if not temp['safe']:
            print("⚠️  Temperature out of range - skipping collection for safety")
            return False
        
        if not self.collector.can_collect():
            print("⏳ Collection on cooldown - waiting...")
            return False
        
        # All conditions met - start collection
        print("\n🎯 All conditions met for collection!")
        result = self.collector.start_collection()
        
        # Update turbidity sensor simulation to reflect collection
        if result['success'] and self.turbidity.simulation_mode:
            self.turbidity.simulate_collection()
        
        return result['success']
    
    def run_monitoring_loop(self, duration_minutes: int = None):
        """
        Main monitoring loop
        Args:
            duration_minutes: Run for specific time (None = run forever)
        """
        print("▶️  Starting monitoring loop...")
        print(f"   Reading sensors every {config.SENSOR_READ_INTERVAL}s")
        if duration_minutes:
            print(f"   Will run for {duration_minutes} minutes")
        else:
            print("   Press Ctrl+C to stop")
        print()
        
        start_time = time.time()
        iteration = 0
        
        try:
            while True:
                iteration += 1
                
                # Read all sensors
                data = self.read_all_sensors()
                
                # Display status
                self.display_status(data)
                
                # Check if collection needed
                collection_triggered = self.check_and_collect(data)
                
                # Log data
                self.log_data(data, collection_triggered)
                
                # If collection happened, wait one cycle time before next reading
                if collection_triggered:
                    print(f"\n⏸️  Waiting {config.CYCLE_INTERVAL}s (one cycle time) after collection...")
                    time.sleep(config.CYCLE_INTERVAL)
                
                # Check if duration limit reached
                if duration_minutes:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= duration_minutes:
                        print(f"\n⏱️  {duration_minutes} minute test complete!")
                        break
                
                # Wait before next reading
                print(f"\n⏸️  Waiting {config.SENSOR_READ_INTERVAL}s until next reading...")
                time.sleep(config.SENSOR_READ_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Error in monitoring loop: {e}")
            self.collector.emergency_stop()
        finally:
            print(f"\n📊 Total readings: {iteration}")
            print(f"📝 Data logged to: {config.LOG_FILE}")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════╗
    ║         ALGAE BOX CONTROL SYSTEM            ║
    ║    Automated Cultivation & Collection       ║
    ╚══════════════════════════════════════════════╝
    """)
    
    # Create system
    system = AlgaeBox()
    
    # Run monitoring loop
    # For testing: run for 2 minutes (remove duration arg to run forever)
    system.run_monitoring_loop(duration_minutes=6)


if __name__ == "__main__":
    main()
