# Algae Box Project - TODO List

**Project:** Automated Algae Cultivation & Collection System  
**Status:** Simulation Phase Complete ✅  
**Next Phase:** Hardware Integration  
**Last Updated:** January 7, 2026

---

## 🎯 Current Status Summary

✅ **COMPLETED:**
- Core system architecture and modular design
- Turbidity sensor simulation
- pH sensor simulation  
- Temperature sensor simulation
- Multi-cycle collection logic (3 cycles)
- Auto-shovel gravity-based collection system
- Data logging to CSV
- Safety checks (pH/temp validation)
- Post-collection wait period
- Plitt model documentation
- Complete hardware BOM with Taobao sources

---

## 📋 TODO List

### Phase 1: Pre-Hardware (Current Phase)
- [ ] **Create Taobao shopping checklist** with optimized Chinese search terms
- [ ] **Design wiring diagram** showing all component connections
- [ ] **Create GPIO pin assignment document** (which sensor goes to which pin)
- [ ] **Write sensor calibration procedures** (especially pH and turbidity)
- [ ] **Document assembly instructions** for shovel mechanism
- [ ] **Add realistic growth simulation** option (change growth rate to 0.005 NTU/min)
- [ ] **Test data analysis scripts** - read and plot logged CSV data
- [ ] **Create backup/restore system** for configuration and data

### Phase 2: Hardware Procurement
- [ ] **Order Phase 1 components** (Pi, basic sensors, wiring)
  - [ ] Raspberry Pi 4B + SD card + power supply
  - [ ] Turbidity sensor (DFRobot SEN0189 or equivalent)
  - [ ] DS18B20 temperature sensor
  - [ ] MCP3008 ADC
  - [ ] Jumper wires and breadboard
  - [ ] Basic resistor/component kit
- [ ] **Order Phase 2 components** (after Phase 1 arrives)
  - [ ] pH sensor + calibration buffers
  - [ ] Solenoid valve (12V)
  - [ ] Servo motor (MG996R)
  - [ ] Relay module (2-channel)
  - [ ] 12V power supply
  - [ ] Waterproof enclosure
- [ ] **Order mechanical parts** (after designing shovel)
  - [ ] Acrylic/stainless steel sheet
  - [ ] Hinges, bolts, nuts
  - [ ] Silicone tubing
  - [ ] Cable glands

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
  - [ ] Servo motor: Test rotation range and holding torque
- [ ] **Update code with real hardware**
  - [ ] Uncomment TODO sections in turbidity_sensor.py
  - [ ] Uncomment TODO sections in ph_sensor.py
  - [ ] Uncomment TODO sections in temperature_sensor.py
  - [ ] Uncomment TODO sections in collection_system.py
  - [ ] Test each sensor module independently
  - [ ] Add voltage-to-NTU calibration curve for turbidity
  - [ ] Add voltage-to-pH calibration curve
- [ ] **Build and test collection mechanism**
  - [ ] Design shovel/scraper mechanism
  - [ ] Mount servo motor
  - [ ] Test opening/closing motion
  - [ ] Install in tank bottom
  - [ ] Test settling and collection cycle

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
  - [ ] Verify settling time is adequate (adjust from 5s to 300s)
  - [ ] Check collection efficiency (how much algae collected)
  - [ ] Measure turbidity reduction after collection
  - [ ] Optimize number of cycles (currently 3)
  - [ ] Adjust cycle interval timing
- [ ] **Fine-tune parameters in config.py**
  - [ ] Set realistic settling time (300s)
  - [ ] Set realistic collection cooldown (3600s)
  - [ ] Set realistic growth rate for simulation (0.005 NTU/min)
  - [ ] Adjust turbidity threshold based on species
  - [ ] Set safe pH/temp ranges for your algae

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

- [ ] **Growth rate realism:** Current 5 NTU/min is ~7200x too fast (demo only)
- [ ] **Settling time:** Need to verify 5min is sufficient in real tank
- [ ] **Collection efficiency:** Unknown until physical testing
- [ ] **Tank size:** Need to specify tank dimensions for shovel design
- [ ] **Algae species:** Which microalgae will be cultivated?
- [ ] **Power backup:** Should we add UPS for power outages?
- [ ] **Winter operation:** Heating requirements in cold climates?

---

## 📅 Milestones

### Milestone 1: Simulation Complete ✅ (Jan 7, 2026)
- All sensors simulated
- Multi-cycle collection working
- Data logging functional

### Milestone 2: Hardware Ordered (Target: Jan 2026)
- All components purchased
- Waiting for delivery

### Milestone 3: Basic Sensors Working (Target: Feb 2026)
- Turbidity + temperature reading real values
- Logging real data

### Milestone 4: Full System Operational (Target: Mar 2026)
- All sensors + actuators working
- Collection system tested with real algae

### Milestone 5: Autonomous Operation (Target: Apr 2026)
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

## 🤔 Decisions Needed

- [ ] **Tank size/shape:** What are the dimensions?
- [ ] **Algae species:** Chlorella? Spirulina? Mixed culture?
- [ ] **Location:** Indoor lab? Outdoor? Greenhouse?
- [ ] **Power source:** Wall outlet? Solar? Battery backup?
- [ ] **Shovel design:** Hinged door? Sliding gate? Rotating scraper?
- [ ] **Collection container:** Size? Material? Automatic emptying?

---

## 📞 Support & Resources

- **GitHub Repository:** https://github.com/lab-Kason/algae_box
- **Raspberry Pi Forums:** https://forums.raspberrypi.com/
- **DFRobot Wiki:** https://wiki.dfrobot.com/
- **Adafruit Learn:** https://learn.adafruit.com/

---

**Remember:** Check off items as completed and add new tasks as they come up!

**Priority:** Focus on Phase 1 & 2 (pre-hardware and procurement) before moving to testing.
