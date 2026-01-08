# Algae Box Project - TODO List

**Project:** Automated Algae Cultivation & Collection System  
**Status:** Design Phase Complete ✅ | Ready for Hardware Procurement  
**Current Design:** Pump-Based Flow Manifold System with Slot Cut  
**Last Updated:** January 8, 2026

---

## 🎯 Current Status Summary

✅ **COMPLETED:**
- Core system architecture and modular design
- Turbidity sensor simulation
- pH sensor simulation  
- Temperature sensor simulation
- Data logging to CSV
- Safety checks (pH/temp validation)
- Post-collection wait period
- Plitt model documentation
- Complete hardware BOM with Taobao sources
- **CAD simulation (FreeCAD Python)**
  - Standard 20L rectangular tank (430×215×215mm)
  - Pump-based flow manifold with 8mm slot cut
  - 100 algae particles with realistic physics
  - Water resistance modeling (boundary layer + drag)
  - 7-phase collection cycle animation
  - Multiple flush passes (3× 600 frames = 1800 frames)
- **Pump-based collection system design**
  - Flow manifold at FRONT wall with slot cut "water knife"
  - Unidirectional flow: FRONT → BACK
  - Multi-pass flushing (3 passes per cycle)
  - Separate phases: settle → flush → wait → drain
  - No mechanical scrapers (gentle laminar flow)
- **Updated control code**
  - collection_system.py rewritten for pump control
  - config.py updated with pump parameters
  - HARDWARE_BOM.md updated with pump + PVC manifold parts

---

## 🚀 Design Evolution History

1. ~~**Mechanical Shovel** → Rejected (algae re-suspension issue)~~
2. ~~**Drain-and-Tilt** → Rejected (scalability issues for larger tanks)~~
3. ~~**V-Bottom Passive** → Rejected (boss: don't modify tank)~~
4. ~~**U-Bottom Passive** → Rejected (boss: prefer pump-based)~~
5. ✅ **Pump-Based Flow Manifold** ← **CURRENT DESIGN**

---

## 📋 TODO List

### Phase 1: Pre-Hardware (Current Phase) ✅ MOSTLY COMPLETE
- [x] **Create hardware BOM** with pump-based system components
- [x] **Design CAD simulation** for proposal demonstration
- [x] **Design flow manifold system** (25mm PVC with 8mm slot cut)
- [x] **Update control code** for pump-based collection
- [x] **Add water resistance physics** to simulation
- [ ] **Create wiring diagram** showing all component connections
- [ ] **Create GPIO pin assignment document** (pump, valve, sensors)
- [ ] **Write sensor calibration procedures** (especially pH and turbidity)
- [ ] **Document manifold construction instructions** (slot cutting, assembly)
- [ ] **Add realistic growth simulation** option (change growth rate to 0.005 NTU/min)
- [ ] **Test data analysis scripts** - read and plot logged CSV data
- [ ] **Create backup/restore system** for configuration and data

### Phase 2: Hardware Procurement (READY TO ORDER)
- [ ] **Order Phase 1 components** (Pi, basic sensors, wiring)
  - [ ] Raspberry Pi 4B + SD card + power supply
  - [ ] Turbidity sensor (DFRobot SEN0189 or equivalent)
  - [ ] DS18B20 temperature sensor
  - [ ] MCP3008 ADC
  - [ ] Jumper wires and breadboard
  - [ ] Basic resistor/component kit
- [ ] **Order Phase 2 components** (actuators and pump system)
  - [ ] pH sensor + calibration buffers
  - [ ] Solenoid valve (12V)
  - [ ] **12V DC Water Pump (0.5-1.5 L/min)**
  - [ ] Relay module (2-channel)
  - [ ] PWM speed controller (optional)
  - [ ] 12V power supply
  - [ ] Waterproof enclosure
- [ ] **Order flow manifold parts**
  - [ ] 25mm PVC pipe (1 meter)
  - [ ] PVC end caps (2 pieces)
  - [ ] PVC cement/glue
  - [ ] Barbed hose fittings (25mm to 12mm)
  - [ ] Silicone tubing (12mm, 2-3 meters)
  - [ ] Suction cups or mounting brackets
  - [ ] Waterproof epoxy
  - [ ] Rotary tool or Dremel (for slot cutting)

### Phase 3: Hardware Setup & Testing
- [ ] **Set up Raspberry Pi**
  - [ ] Install Raspbian OS
  - [ ] Configure WiFi and SSH
  - [ ] Install Python libraries (RPi.GPIO, Adafruit libraries)
  - [ ] Clone GitHub repository to Pi
- [ ] **Test individual sensors (simulation → real)**
  - [ ] Turbidity sensor: Test readings with clean/cloudy water
  - [ ] Temperature sensor: Verify accuracy with thermometer
  - [ ] pH sensor: Calibrate with buffer solutions (pH 4, 7, 10)
  - [ ] MCP3008 ADC: Test analog to digital conversion
- [ ] **Test actuators**
  - [ ] Relay module: Test switching with GPIO
  - [ ] Solenoid valve: Test open/close operation
  - [ ] **Water pump: Test flow rate and PWM control**
- [ ] **Update code with real hardware**
  - [ ] Uncomment TODO sections in turbidity_sensor.py
  - [ ] Uncomment TODO sections in ph_sensor.py
  - [ ] Uncomment TODO sections in temperature_sensor.py
  - [ ] Uncomment TODO sections in collection_system.py (pump control)
  - [ ] Test each sensor module independently
  - [ ] Add voltage-to-NTU calibration curve for turbidity
  - [ ] Add voltage-to-pH calibration curve
- [ ] **Build and test flow manifold system**
  - [ ] Cut PVC pipe to tank width (~215mm)
  - [ ] Mark and cut 8mm × 185mm horizontal slot
  - [ ] Smooth edges with file/sandpaper
  - [ ] Glue end caps with PVC cement
  - [ ] Install barbed fitting for pump hose
  - [ ] Mount manifold 10mm above bottom (suction cups or brackets)
  - [ ] Connect pump to manifold with silicone tubing
  - [ ] Test flow pattern (should create uniform water curtain)
  - [ ] Adjust flow rate for optimal sweeping (PWM control)

### Phase 4: Integration & Calibration
- [ ] **Integrate all sensors on breadboard**
  - [ ] Wire everything according to wiring diagram
  - [ ] Test all sensors reading simultaneously
  - [ ] Check for electrical interference/noise
- [ ] **Calibrate sensors with real algae culture**
  - [ ] Grow test algae batch
  - [ ] Correlate turbidity readings with algae density
  - [ ] Adjust harvest threshold for your algae species
  - [ ] Monitor pH changes during growth cycle
  - [ ] Verify temperature stability
- [ ] **Test collection system with real algae**
  - [ ] Verify settling time is adequate (adjust from 5s to 100-300s)
  - [ ] Check collection efficiency (how much algae collected)
  - [ ] Measure turbidity reduction after collection
  - [ ] Test multiple flush passes (currently 3× per cycle)
  - [ ] Verify flow velocity doesn't cause re-suspension
  - [ ] Optimize pump flow rate (0.5-1.5 L/min range)
  - [ ] Adjust flush time per pass (currently 10s, real: 200-600s)
- [ ] **Fine-tune parameters in config.py**
  - [ ] Set realistic settling time (100-300s)
  - [ ] Set realistic flush time per pass (200-600s)
  - [ ] Adjust number of flush passes if needed
  - [ ] Set realistic collection cooldown (3600s)
  - [ ] Set realistic growth rate for simulation (0.005 NTU/min)
  - [ ] Adjust turbidity threshold based on species
  - [ ] Set safe pH/temp ranges for your algae
  - [ ] Fine-tune pump flow rate (FLOW_RATE in config)

### Phase 5: Algae Identification Integration
- [ ] **Locate existing algae identification program**
  - [ ] Review code structure
  - [ ] Understand input/output format
  - [ ] Check camera/microscope requirements
- [ ] **Create algae_identifier.py module**
  - [ ] Adapt existing code for modular use
  - [ ] Add interface to work with main system
  - [ ] Test with sample images
- [ ] **Integrate camera module**
  - [ ] Install Raspberry Pi Camera or USB microscope
  - [ ] Test image capture
  - [ ] Implement automatic image capture on collection
- [ ] **Schedule identification runs**
  - [ ] Trigger on collection events
  - [ ] Or run on time schedule (e.g., daily)
  - [ ] Log algae types to CSV

### Phase 6: Monitoring & Automation
- [ ] **Add web dashboard** (optional)
  - [ ] Flask/Django web interface
  - [ ] Real-time sensor graphs
  - [ ] Manual collection trigger button
  - [ ] View historical data
- [ ] **Add notifications**
  - [ ] Email alerts for out-of-range conditions
  - [ ] SMS/WeChat alerts for collection events
  - [ ] Daily summary reports
- [ ] **Implement remote access**
  - [ ] Set up VPN or port forwarding
  - [ ] Mobile app control (optional)
  - [ ] Cloud data backup
- [ ] **Add advanced features**
  - [ ] Predictive harvesting (ML model)
  - [ ] Automatic light control (if growing indoors)
  - [ ] Nutrient dosing automation
  - [ ] Multiple tank support

### Phase 7: Documentation & Sharing
- [ ] **Document complete build**
  - [ ] Take photos of assembly process
  - [ ] Create step-by-step build guide
  - [ ] Record video demonstration
- [ ] **Write research paper/blog post**
  - [ ] Document algae growth results
  - [ ] Compare different collection strategies
  - [ ] Share efficiency data
- [ ] **Publish to GitHub**
  - [ ] Clean up code comments
  - [ ] Add comprehensive README
  - [ ] Include example data and plots
  - [ ] Add license
- [ ] **Share with community**
  - [ ] Post on Hackaday/Instructables
  - [ ] Share on Reddit (r/raspberry_pi, r/aquaponics)
  - [ ] Submit to maker forums

---

## 🔧 Technical Debt / Future Improvements

- [ ] Add unit tests for each module
- [ ] Implement proper logging (Python logging module)
- [ ] Add configuration validation (check for invalid values)
- [ ] Create installer script for dependencies
- [ ] Add graceful shutdown handling
- [ ] Implement data backup/recovery system
- [ ] Add sensor health monitoring (detect failures)
- [ ] Optimize power consumption for 24/7 operation
- [ ] Add watchdog timer for automatic recovery
- [ ] Create GUI for non-technical users

---

## 🐛 Known Issues / Questions

- [x] ~~Growth rate realism: Current 5 NTU/min is ~7200x too fast~~ (demo only, documented)
- [x] ~~Collection method: Shovel vs passive vs pump~~ → **Pump-based selected**
- [x] ~~Tank modifications needed?~~ → **No, standard rectangular tank**
- [ ] **Settling time:** Need to verify 5min is sufficient in real tank (currently fast for demo)
- [ ] **Flush time:** Need to verify 10s per pass is sufficient (currently fast for demo, should be 200-600s)
- [ ] **Collection efficiency:** Unknown until physical testing (CAD shows ~36% with short flush)
- [ ] **Flow rate optimization:** What pump flow rate gives best collection? (0.5-1.5 L/min)
- [ ] **Water resistance impact:** Does real-world drag match simulation? (boundary layer effects)
- [ ] **Algae species:** Which microalgae will be cultivated?
- [ ] **Power backup:** Should we add UPS for power outages?
- [ ] **Winter operation:** Heating requirements in cold climates?

---

## 💡 Key Design Insights from CAD Simulation

✅ **Water resistance matters!** 
- Algae at bottom experience only ~30-40% of bulk flow velocity
- Boundary layer + viscous drag significantly reduce effective sweeping force
- 3× longer flush time justified by physics

✅ **Multiple passes work!**
- Pass 1: Breaks weak adhesion (adhesion strength 0.3-0.6)
- Pass 2: Moves partially-freed algae
- Pass 3: Sweeps remaining stubborn algae (0.7-1.0 adhesion)
- Total exposure time > individual particle adhesion resistance

✅ **Slot cut > holes**
- Continuous water curtain (no gaps)
- Uniform flow distribution across full width
- Lower pressure = gentler flow (preserves algae cells)
- Easier fabrication (one cut vs. drilling 10 holes)

✅ **Extended flush time critical**
- 36% collection with 600 frames (old setting)
- Predicted >85% collection with 1800 frames (3× longer)
- Adhesion weakens exponentially with flow exposure time

---

## 📅 Milestones

### Milestone 1: Simulation Complete ✅ (Jan 7, 2026)
- All sensors simulated
- Multi-cycle collection working
- Data logging functional

### Milestone 1.5: Design Complete ✅ (Jan 8, 2026)
- **CAD simulation complete** (FreeCAD Python, 638 lines)
- **Pump-based flow manifold designed**
- **Water resistance physics added**
- **HARDWARE_BOM updated** for pump system
- **Control code updated** (collection_system.py, config.py)
- **Ready for hardware procurement**

### Milestone 2: Hardware Ordered (Target: Jan 2026)
- All components purchased
- PVC manifold parts ordered
- Waiting for delivery

### Milestone 3: Manifold Built (Target: Feb 2026)
- PVC pipe cut and slot created
- Pump connected and tested
- Flow pattern verified

### Milestone 4: Basic Sensors Working (Target: Feb 2026)
- Turbidity + temperature reading real values
- Logging real data

### Milestone 5: Full System Operational (Target: Mar 2026)
- All sensors + actuators working
- Collection system tested with real algae
- Flow rate optimized

### Milestone 6: Autonomous Operation (Target: Apr 2026)
- System runs 24/7 unsupervised
- Algae ID integrated
- Production ready

---

## 📝 Notes & Ideas

- Consider adding **light sensor** to monitor photoperiod
- Could add **dissolved oxygen sensor** for growth optimization
- **Stirring mechanism** to keep algae suspended before collection?
- **Multiple collection containers** for different algae species?
- **Computer vision** to measure algae density visually?
- Integration with **home automation** (Home Assistant)?

---

## 🤔 Decisions Made

- [x] **Tank:** Standard 20L rectangular (430×215×215mm) - no modifications
- [x] **Collection method:** Pump-based flow manifold with slot cut
- [x] **Manifold design:** 25mm PVC pipe, 8mm × 185mm horizontal slot
- [x] **Flow direction:** Unidirectional FRONT → BACK (simple, effective)
- [x] **Flush strategy:** Multiple passes (3×) with extended time
- [x] **Pump type:** 12V DC submersible (0.5-1.5 L/min adjustable)

## 🤔 Decisions Still Needed

- [ ] **Algae species:** Chlorella? Spirulina? Mixed culture?
- [ ] **Location:** Indoor lab? Outdoor? Greenhouse?
- [ ] **Power source:** Wall outlet? Solar? Battery backup?
- [ ] **Collection container:** Size? Material? Automatic emptying?
- [ ] **Mounting method:** Suction cups vs. brackets for manifold?

---

## 📞 Support & Resources

- **GitHub Repository:** https://github.com/lab-Kason/algae_box
- **Raspberry Pi Forums:** https://forums.raspberrypi.com/
- **DFRobot Wiki:** https://wiki.dfrobot.com/
- **Adafruit Learn:** https://learn.adafruit.com/

---

**Remember:** Check off items as completed and add new tasks as they come up!

**Priority:** Focus on Phase 1 & 2 (pre-hardware and procurement) before moving to testing.
