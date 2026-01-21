"""
Algae Box - Cloud-Connected Sensor System
Sends sensor data to Railway backend
Run this on your Raspberry Pi
"""
import time
import requests
from datetime import datetime
from modules.turbidity_sensor import TurbiditySensor
from modules.ph_sensor import PHSensor
from modules.temperature_sensor import TemperatureSensor
from modules.collection_system import CollectionSystem
import config

# ⚙️ CONFIGURATION - Change this to your Railway URL
RAILWAY_API_URL = "https://web-production-f856a8.up.railway.app"
TANK_ID = 1  # Change this to your tank ID from the mobile app

# Reading interval (seconds)
READING_INTERVAL = 10


class CloudConnectedAlgaeBox:
    """Raspberry Pi sensor system that sends data to cloud"""
    
    def __init__(self, tank_id: int):
        print("🌱 Initializing Cloud-Connected Algae Box...")
        print(f"   Mode: {'SIMULATION' if config.SIMULATION_MODE else 'REAL HARDWARE'}")
        print(f"   Tank ID: {tank_id}")
        print(f"   API: {RAILWAY_API_URL}\n")
        
        self.tank_id = tank_id
        self.species_params = None
        
        # Test connection and fetch tank info
        self._test_connection()
        self._fetch_tank_info()
        
        # Initialize sensors with species-specific parameters
        self.turbidity = TurbiditySensor(species_params=self.species_params)
        self.ph = PHSensor(species_params=self.species_params)
        self.temperature = TemperatureSensor(species_params=self.species_params)
        self.collector = CollectionSystem()
        
        print("✅ System initialized\n")
    
    def _test_connection(self):
        """Test connection to Railway backend"""
        try:
            response = requests.get(f"{RAILWAY_API_URL}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Connected to Railway backend")
            else:
                print(f"⚠️  Backend responded with status {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot connect to backend: {e}")
            print("   Check your WiFi connection and Railway URL")
    
    def _fetch_tank_info(self):
        """Fetch tank info and species parameters from API"""
        try:
            # Get tank info
            response = requests.get(f"{RAILWAY_API_URL}/api/tanks/{self.tank_id}", timeout=5)
            if response.status_code != 200:
                print(f"⚠️  Could not fetch tank info, using default parameters")
                return
            
            tank_data = response.json()['tank']
            algae_type = tank_data['algae_type']
            
            # Get species info
            response = requests.get(f"{RAILWAY_API_URL}/api/species", timeout=5)
            if response.status_code != 200:
                print(f"⚠️  Could not fetch species info, using default parameters")
                return
            
            species_list = response.json()['species']
            species = next((s for s in species_list if s['name'] == algae_type), None)
            
            if species:
                self.species_params = {
                    'name': species['name'],
                    'ph_optimal': species['ph_optimal'],
                    'temp_optimal': species['temp_optimal'],
                    'harvest_turbidity': species['harvest_turbidity']
                }
                print(f"📊 Tank Species: {species['name']}")
                print(f"   pH optimal: {species['ph_optimal']}")
                print(f"   Temp optimal: {species['temp_optimal']}°C")
                print(f"   Harvest at: {species['harvest_turbidity']} NTU\n")
            else:
                print(f"⚠️  Species '{algae_type}' not found, using defaults")
                
        except Exception as e:
            print(f"⚠️  Error fetching tank info: {e}")
            print("   Using default simulation parameters")
    
    def read_sensors(self) -> dict:
        """Read all sensor values"""
        try:
            readings = {
                'turbidity': self.turbidity.read_ntu(),
                'ph': self.ph.read_ph(),
                'temperature': self.temperature.read_celsius()
            }
            return readings
        except Exception as e:
            print(f"❌ Error reading sensors: {e}")
            return None
    
    def send_to_cloud(self, readings: dict) -> bool:
        """Send sensor readings to Railway backend"""
        if not readings:
            return False
        
        try:
            # Prepare data for API (match backend field names)
            data = {
                'tank_id': self.tank_id,
                'ph': readings['ph'],
                'temperature_c': readings['temperature'],
                'turbidity_ntu': readings['turbidity'],
                'ph_safe': True,  # These will be calculated by backend later
                'temperature_safe': True,
                'harvest_ready': False
            }
            
            # Send POST request to Railway
            response = requests.post(
                f"{RAILWAY_API_URL}/api/sensors/reading",
                json=data,
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"✅ Data sent: pH={readings['ph']:.2f}, "
                      f"Temp={readings['temperature']:.1f}°C, "
                      f"Turbidity={readings['turbidity']:.0f} NTU")
                return True
            else:
                print(f"⚠️  Server returned status {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Connection timeout - check your internet connection")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - is Railway backend running?")
            return False
        except Exception as e:
            print(f"❌ Error sending data: {e}")
            return False
    
    def check_recommendations(self):
        """Fetch recommendations from cloud"""
        try:
            response = requests.get(
                f"{RAILWAY_API_URL}/api/recommendations/{self.tank_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                recommendations = data.get('recommendations', [])
                
                if recommendations:
                    print("\n💡 Recommendations:")
                    for rec in recommendations:
                        priority = rec['priority']
                        emoji = "🔴" if priority == "critical" else "🟠" if priority == "action_required" else "🟡"
                        print(f"{emoji} [{rec['category'].upper()}] {rec['issue']}")
                        print(f"   → {rec['action']}")
                    print()
                    
        except Exception as e:
            print(f"⚠️  Could not fetch recommendations: {e}")
    
    def run(self):
        """Main loop - read sensors and send to cloud"""
        print("🔄 Starting sensor monitoring...")
        print(f"   Reading every {READING_INTERVAL} seconds")
        print("   Press Ctrl+C to stop\n")
        
        reading_count = 0
        last_recommendation_check = 0
        
        try:
            while True:
                reading_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"[{timestamp}] Reading #{reading_count}")
                
                # Read sensors
                readings = self.read_sensors()
                
                # Send to cloud
                if readings:
                    success = self.send_to_cloud(readings)
                    
                    # Check recommendations every 5 readings (50 seconds)
                    if success and reading_count % 5 == 0:
                        self.check_recommendations()
                
                # Wait before next reading
                time.sleep(READING_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping sensor monitoring...")
            print(f"   Total readings sent: {reading_count}")
            print("   Goodbye! 👋\n")


def main():
    """Entry point"""
    print("=" * 60)
    print("  🌊 ALGAE BOX - CLOUD-CONNECTED SENSOR SYSTEM 🌊")
    print("=" * 60)
    print()
    
    # Create and run system
    system = CloudConnectedAlgaeBox(tank_id=TANK_ID)
    system.run()


if __name__ == "__main__":
    main()
