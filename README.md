# Algae Box - Automated Cultivation System

Automated system for cultivating and collecting microalgae using Raspberry Pi.

## Features

- 🌊 **Turbidity monitoring** - Track algae density in real-time
- 🧪 **pH monitoring** - Ensure optimal water chemistry  
- 🌡️ **Temperature monitoring** - Maintain ideal growth conditions
- 🤖 **Auto-collection** - Gravity-based shovel mechanism
- 📊 **Data logging** - CSV logs for analysis
- 🔬 **Simulation mode** - Develop without hardware

## System Architecture

### Auto-Shovel Collection Mechanism
1. **Close valve** → Stop water flow
2. **Settle** → Gravity pulls algae to bottom (5 min)
3. **Open shovel** → Collect settled algae
4. **Close shovel** → Secure collection
5. **Open valve** → Resume normal flow

### Hardware (Future)
- Raspberry Pi 4 / Zero 2 W
- Turbidity sensor (TSW-10 or DFRobot SEN0189)
- pH probe with BNC connector
- DS18B20 waterproof temperature sensor
- Solenoid valve (flow control)
- Servo or linear actuator (shovel)
- MCP3008 ADC (analog sensors)

## Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/lab-Kason/algae_box.git
cd algae_box

# Install dependencies (when using real hardware)
pip install RPi.GPIO adafruit-circuitpython-mcp3xxx
```

### Run Simulation
```bash
python main.py
```

The system will:
- Initialize all sensors in simulation mode
- Start monitoring loop (reads every 60 seconds)
- Automatically trigger collection when turbidity > 100 NTU
- Log all data to `data/algae_log.csv`

### Test Individual Components
```bash
# Test turbidity sensor
python modules/turbidity_sensor.py

# Test pH sensor
python modules/ph_sensor.py

# Test collection system
python modules/collection_system.py
```

## Configuration

Edit `config.py` to adjust:

```python
# Switch to real hardware
SIMULATION_MODE = False

# Adjust thresholds
TURBIDITY_HARVEST_THRESHOLD = 100  # NTU
PH_MIN_SAFE = 6.5
PH_MAX_SAFE = 8.5

# Collection timing
SETTLING_TIME = 300  # 5 minutes for algae to settle
COLLECTION_COOLDOWN = 3600  # 1 hour between collections

# GPIO pins (for real hardware)
VALVE_PIN = 17
SHOVEL_PIN = 27
```

## Project Structure

```
algae_box/
├── main.py                      # Main control system
├── config.py                    # All configuration
├── modules/
│   ├── turbidity_sensor.py     # Turbidity monitoring
│   ├── ph_sensor.py             # pH monitoring
│   ├── temperature_sensor.py   # Temperature monitoring
│   └── collection_system.py    # Auto-shovel control
├── data/
│   └── algae_log.csv           # Sensor data logs
├── simulations/                # CFD/flow demo scripts & generated files
├── PROJECT_PLAN.md             # Detailed project plan
└── README.md                   # This file
```

## Development Roadmap

- [x] Simulation mode for all sensors
- [x] Auto-shovel collection logic
- [x] Data logging system
- [ ] Real sensor integration
- [ ] Algae identification module integration
- [ ] Web dashboard for monitoring
- [ ] Email/SMS alerts
- [ ] Mobile app control

## Switching to Real Hardware

When you get physical sensors:

1. **Set `SIMULATION_MODE = False` in `config.py`**
2. **Install libraries:**
   ```bash
   pip install RPi.GPIO adafruit-circuitpython-mcp3xxx
   ```
3. **Wire sensors to GPIO pins** (see config.py for pin assignments)
4. **Calibrate sensors** using known standards
5. **Run system:** `python main.py`

The code automatically detects hardware and falls back to simulation if sensors aren't connected.

## Safety Features

- pH/temperature range checks before collection
- Cooldown timer between collections
- Emergency stop function
- Automatic valve restoration on error

## Data Analysis

View logged data:
```bash
cat data/algae_log.csv
```

Import into Python/Excel for analysis:
- Track growth rates
- Optimize collection timing
- Correlate pH/temp with growth

## Contributing

This is a personal project, but suggestions welcome!

## License

MIT

---

**Current Status:** ✅ Simulation mode complete, ready for hardware integration
