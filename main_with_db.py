"""
Algae Box - Main Control System with Database Integration
Automated algae cultivation and collection with API support
"""
import time
from datetime import datetime
from modules.turbidity_sensor import TurbiditySensor
from modules.ph_sensor import PHSensor
from modules.temperature_sensor import TemperatureSensor
from modules.collection_system import CollectionSystem
from database import db, Tank, SensorReading, CollectionEvent
from recommendations import RecommendationEngine
import config


class AlgaeBoxWithDB:
    """Main controller for algae cultivation system with database integration"""
    
    def __init__(self, tank_id: int = None):
        print("🌱 Initializing Algae Box System with Database...")
        print(f"   Mode: {'SIMULATION' if config.SIMULATION_MODE else 'REAL HARDWARE'}")
        
        # Initialize database
        db.init_db()
        
        # Get or create tank
        self.tank_id = tank_id
        if not self.tank_id:
            self.tank_id = self._get_default_tank()
        
        # Initialize sensors
        self.turbidity = TurbiditySensor()
        self.ph = PHSensor()
        self.temperature = TemperatureSensor()
        self.collector = CollectionSystem()
        
        print(f"✅ System initialized for Tank ID: {self.tank_id}\n")
    
    def _get_default_tank(self) -> int:
        """Get or create default tank"""
        session = db.get_session()
        try:
            tank = session.query(Tank).first()
            if not tank:
                # Create default tank
                tank = Tank(
                    name="Main Tank",
                    algae_type="Chlorella",
                    volume_liters=100,
                    status="active"
                )
                session.add(tank)
                session.commit()
                print(f"✅ Created default tank: {tank.name}")
            return tank.id
        finally:
            session.close()
    
    def read_all_sensors(self) -> dict:
        """Read all sensor values"""
        return {
            'turbidity': self.turbidity.get_status(),
            'ph': self.ph.get_status(),
            'temperature': self.temperature.get_status(),
            'collector': self.collector.get_status()
        }
    
    def log_data_to_db(self, data: dict):
        """Log sensor data to database"""
        session = db.get_session()
        try:
            reading = SensorReading(
                tank_id=self.tank_id,
                ph=data['ph']['ph'],
                temperature_c=data['temperature']['temperature_c'],
                turbidity_ntu=data['turbidity']['turbidity_ntu'],
                ph_safe=data['ph']['safe'],
                temperature_safe=data['temperature']['safe'],
                harvest_ready=data['turbidity']['harvest_ready']
            )
            session.add(reading)
            session.commit()
        except Exception as e:
            print(f"⚠️  Database logging error: {e}")
            session.rollback()
        finally:
            session.close()
    
    def log_collection_event(self, turbidity_before: float, turbidity_after: float, 
                            duration: int, success: bool, notes: str = ""):
        """Log collection event to database"""
        session = db.get_session()
        try:
            # Estimate collected amount based on turbidity reduction
            reduction_percent = (turbidity_before - turbidity_after) / turbidity_before if turbidity_before > 0 else 0
            estimated_ml = reduction_percent * 100  # Rough estimate
            
            event = CollectionEvent(
                tank_id=self.tank_id,
                turbidity_before=turbidity_before,
                turbidity_after=turbidity_after,
                duration_seconds=duration,
                success=success,
                estimated_amount_ml=estimated_ml,
                notes=notes
            )
            session.add(event)
            session.commit()
        except Exception as e:
            print(f"⚠️  Collection logging error: {e}")
            session.rollback()
        finally:
            session.close()
    
    def display_status(self, data: dict):
        """Display current system status"""
        print("\n" + "="*60)
        print(f"📊 SYSTEM STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Tank ID: {self.tank_id}")
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
    
    def show_recommendations(self, data: dict):
        """Display recommendations based on current readings"""
        session = db.get_session()
        try:
            # Get tank and species info
            from database import Tank as TankModel, AlgaeSpecies
            tank = session.query(TankModel).filter_by(id=self.tank_id).first()
            species = session.query(AlgaeSpecies).filter_by(name=tank.algae_type).first()
            
            # Create mock reading object
            class ReadingMock:
                def __init__(self, data):
                    self.ph = data['ph']['ph']
                    self.temperature_c = data['temperature']['temperature_c']
                    self.turbidity_ntu = data['turbidity']['turbidity_ntu']
            
            reading = ReadingMock(data)
            recommendations = RecommendationEngine.analyze(reading, species, tank.volume_liters)
            
            if recommendations:
                print("\n💡 RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    severity_icon = {
                        'critical': '🚨',
                        'action_required': '⚠️',
                        'warning': '⚡',
                        'ok': '✅'
                    }.get(rec.severity, 'ℹ️')
                    
                    print(f"\n{i}. {severity_icon} [{rec.category.upper()}] {rec.issue}")
                    print(f"   → {rec.action}")
                    if rec.details and rec.severity in ['critical', 'action_required']:
                        print(f"   ℹ️  {rec.details}")
        except Exception as e:
            print(f"⚠️  Could not generate recommendations: {e}")
        finally:
            session.close()
    
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
        turbidity_before = turb['turbidity_ntu']
        
        result = self.collector.start_collection()
        
        # Update turbidity sensor simulation to reflect collection
        if result['success'] and self.turbidity.simulation_mode:
            self.turbidity.simulate_collection()
        
        # Log collection event
        turbidity_after = self.turbidity.get_status()['turbidity_ntu']
        self.log_collection_event(
            turbidity_before=turbidity_before,
            turbidity_after=turbidity_after,
            duration=result['duration'],
            success=result['success'],
            notes="Automated collection triggered by system"
        )
        
        return result['success']
    
    def run_monitoring_loop(self, duration_minutes: int = None, show_recs: bool = True):
        """
        Main monitoring loop with database logging
        Args:
            duration_minutes: Run for specific time (None = run forever)
            show_recs: Show recommendations each iteration
        """
        print("▶️  Starting monitoring loop with database logging...")
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
                
                # Show recommendations
                if show_recs:
                    self.show_recommendations(data)
                
                # Check if collection needed
                collection_triggered = self.check_and_collect(data)
                
                # Log data to database
                self.log_data_to_db(data)
                
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
            import traceback
            traceback.print_exc()
            self.collector.emergency_stop()
        finally:
            print(f"\n📊 Total readings: {iteration}")
            print(f"💾 Data logged to database: algae_box.db")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════╗
    ║         ALGAE BOX CONTROL SYSTEM            ║
    ║    Automated Cultivation & Collection       ║
    ║         With Database Integration           ║
    ╚══════════════════════════════════════════════╝
    """)
    
    # Create system (will use default tank or create one)
    system = AlgaeBoxWithDB()
    
    # Run monitoring loop
    # For testing: run for 2 minutes (remove duration arg to run forever)
    system.run_monitoring_loop(duration_minutes=2)


if __name__ == "__main__":
    main()
