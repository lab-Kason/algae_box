# Algae Box - Automated Cultivation & Collection System

## Project Overview
Automated system for cultivating microalgae in a fish tank with:
- Turbidity-based auto-collection
- pH/Temperature monitoring
- Algae type identification
- Physical collection mechanism control

## Hardware Platform
**Raspberry Pi** (Recommended: Pi 4 or Pi Zero 2 W)
- Python support ✓
- GPIO pins for sensors/actuators ✓
- Good I2C/SPI support ✓
- Can run 24/7 ✓

## System Architecture (Modular Design)

### Phase 1: Foundation - Turbidity Sensing ⭐ START HERE
**Why first?** 
- Simplest to implement
- Core metric for harvest decision
- Tests your hardware setup
- No moving parts risk

**Hardware needed:**
- Turbidity sensor (Options):
  * TSW-10 Analog Turbidity Sensor (~$15)
  * DFRobot SEN0189 (~$10)
  * DIY: IR LED + photodiode setup
- ADC converter (if analog sensor): MCP3008 or ADS1115

**Implementation:**
```python
# modules/turbidity_sensor.py
class TurbiditySensor:
    def __init__(self, pin):
        # Setup sensor
        pass
    
    def read_ntu(self):
        # Return turbidity in NTU units
        pass
    
    def is_harvest_ready(self, threshold=100):
        # Decision logic
        return self.read_ntu() > threshold
```

### Phase 2: Environmental Monitoring
**pH Sensor:**
- Analog pH probe + BNC connector
- Requires calibration routine

**Temperature Sensor:**
- DS18B20 (waterproof, 1-wire, very reliable)
- DHT22 for air temperature (optional)

### Phase 3: Auto-Collection Logic
Combine sensors to make harvest decisions:
```python
# Core decision engine
if turbidity > threshold and pH in safe_range:
    trigger_collection()
```

### Phase 4: Physical Collection Mechanism
**Options:**
1. **Pump-based** (Simplest): Peristaltic pump controlled by relay
2. **Filtration**: Valve + filter system
3. **Overflow**: Controlled drain valve
4. **Hydrocyclone**: Based on Plitt model (complex)

### Phase 5: Algae Type Identification Integration
- Import your existing program as module
- Trigger on collection events or schedule
- Possibly needs camera/microscope interface

## Recommended Starting Order

### ✅ Step 1: Turbidity Sensing (THIS WEEK)
1. Wire up turbidity sensor to Pi
2. Write basic reading script
3. Test calibration with water samples
4. Log data to CSV for 24-48 hours

### Step 2: Add pH + Temperature (WEEK 2)
1. Add sensors to existing code
2. Create unified monitoring dashboard
3. Set up alerts for out-of-range values

### Step 3: Collection Trigger Logic (WEEK 3)
1. Define harvest criteria
2. Implement decision algorithm
3. Add logging and notifications

### Step 4: Physical Collection (WEEK 4)
1. Choose mechanism (start with pump)
2. Wire relay/motor control
3. Test dry, then with water
4. Integrate with trigger logic

### Step 5: Algae ID Integration (WEEK 5)
1. Review existing code
2. Adapt for modular integration
3. Schedule or event-trigger runs

## Project Structure
```
algae_box/
├── main.py                 # Main control loop
├── config.py              # All settings/thresholds
├── modules/
│   ├── turbidity_sensor.py
│   ├── ph_sensor.py
│   ├── temperature_sensor.py
│   ├── collection_system.py
│   └── algae_identifier.py
├── utils/
│   ├── logger.py
│   └── notifications.py
├── data/                  # Sensor logs
└── tests/                 # Unit tests
```

## Why Start with Turbidity?

✅ **Least complex** - Just read analog value  
✅ **No moving parts** - Lower risk of mistakes  
✅ **Immediate feedback** - See values change in real-time  
✅ **Foundation for decisions** - Everything else builds on this  
✅ **Safe to test** - Can't damage tank/algae  

## Next Steps
1. Order turbidity sensor
2. Set up Raspberry Pi with Raspbian OS
3. Install Python libraries: RPi.GPIO, adafruit-circuitpython-ads1x15
4. Create basic sensor reading script
5. Start logging data to understand algae growth pattern

---
*Note: Plitt model documented in Untitled-1.txt for future hydrocyclone consideration*
