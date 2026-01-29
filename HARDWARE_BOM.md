# Algae Box - Complete Hardware Shopping List

## 🛒 Complete Bill of Materials (BOM)
## Pump-Based Flow Manifold System

Last Updated: January 21, 2026

**Key Changes:**
- ✅ Updated to **digital I2C sensors** (no ADC needed!)
- ✅ Easier wiring - all sensors use I2C/1-Wire
- ✅ Better accuracy for algae cultivation
- ✅ Plug-and-play compatibility

---

## 1. Main Controller

### Raspberry Pi 4 Model B (4GB) - **$55**
- **Why:** Sufficient processing power, I2C/SPI/GPIO pins, runs Python
- **Alternative:** Raspberry Pi Zero 2 W ($15) - cheaper, lower power, still capable
- **Supplier:** [Adafruit](https://www.adafruit.com/product/4296), [Amazon](https://www.amazon.com/Raspberry-Model-2019-Quad-Bluetooth/dp/B07TC2BK1X)
- **Includes:** Quad-core processor, WiFi, Bluetooth, 40 GPIO pins, **I2C interface built-in**

### MicroSD Card (32GB Class 10) - **$10**
- **Model:** SanDisk Ultra 32GB
- **Why:** OS storage and data logging
- **Supplier:** Amazon, Best Buy

### Power Supply (5V 3A USB-C) - **$10**
- **Model:** Official Raspberry Pi Power Supply
- **Why:** Stable 5V 3A for Pi + sensors
- **Supplier:** Adafruit, Amazon

---

## 2. Sensors (All Digital - No ADC Needed! ✨)

### A. Turbidity Sensor - **$35**

**Model: DFRobot SEN0554 Gravity I2C Turbidity Sensor** ⭐ RECOMMENDED
- **Interface:** I2C (direct to Raspberry Pi, no ADC!)
- **Range:** 0-1000 NTU (perfect for algae: 0-500 NTU)
- **Accuracy:** ±5% FSD
- **Output:** Digital (0.001 NTU resolution)
- **Why:** 
  - Plug-and-play I2C
  - No calibration curve needed
  - Direct digital output
  - Much better precision than analog sensors
- **Supplier:** [DFRobot](https://www.dfrobot.com/product-2623.html), [Amazon](https://www.amazon.com/DFRobot-Turbidity-Sensor-Gravity-Compatible/dp/B0BXXX)
- **Wiring:** Only 4 wires (VCC, GND, SDA, SCL)
- **Python Library:** Included, very easy to use

**Alternative: Analog Version (if budget tight) - $12**
- DFRobot SEN0189 (requires MCP3008 ADC)
- More complex wiring, less accurate

### B. pH Sensor - **$60**

**Model: Atlas Scientific EZO-pH Kit (I2C)** ⭐ RECOMMENDED
- **Interface:** I2C (direct to Raspberry Pi)
- **Range:** pH 0.001-14.000
- **Accuracy:** ±0.002 pH
- **Features:**
  - Digital I2C communication
  - Auto-calibration storage
  - Temperature compensation
  - No external ADC needed
- **Includes:** EZO-pH circuit + probe
- **Why:** Industrial-grade, lab-quality, drift-resistant, easy Python library
- **Supplier:** [Atlas Scientific](https://atlas-scientific.com/kits/ph-kit/), [Amazon](https://www.amazon.com/Atlas-Scientific-ENV-SDS-KIT-Gravity-Sensor/dp/)
- **Wiring:** 4 wires (VCC, GND, SDA, SCL)
- **Calibration:** Digital via Python (stores in EEPROM)

**pH Calibration Buffer Set (pH 4.0, 7.0, 10.0) - $12**
- Essential for accurate readings
- One-time setup, stores calibration

**Budget Alternative: DFRobot SEN0161-V2 - $25**
- Analog output (requires MCP3008 ADC)
- Less accurate, requires more calibration

### C. Temperature Sensor - **$8** ✅ SAME (Already Perfect)

**Model: DS18B20 Waterproof Digital Temperature Sensor**
- **Interface:** 1-Wire (single GPIO pin, no ADC!)
- **Range:** -55°C to +125°C
- **Accuracy:** ±0.5°C
- **Cable:** 1m waterproof stainless steel probe
- **Why:** Waterproof, accurate, widely supported, simple wiring
- **Supplier:** [Adafruit](https://www.adafruit.com/product/381), [Amazon](https://www.amazon.com/Waterproof-Digital-Temperature-DS18B20-Raspberry/dp/B012C597T0)
- **Wiring:** 3 wires (VCC, GND, DATA)

**4.7kΩ Pull-up Resistor** (for DS18B20) - **$0.10**
- Required for 1-Wire protocol

---

## 3. Analog-to-Digital Converter (ADC)

### ~~MCP3008 - NOT NEEDED ANYMORE! ✨~~

**Why removed:**
- All sensors now use digital I2C or 1-Wire
- Direct connection to Raspberry Pi
- No analog conversion needed
- Simpler wiring, fewer components

**If using budget analog sensors:**
- MCP3008 8-Channel 10-Bit ADC - $4
- ADS1115 16-Bit ADC - $10 (better for pH)

---

## 4. Actuators & Collection System

### A. Solenoid Valve (Flow Control) - **$15**

**Model: 12V DC 1/2" Electric Solenoid Valve**
- **Size:** 1/2 inch (DN15) or match your tank plumbing
- **Voltage:** 12V DC
- **Type:** Normally Closed (NC) - closes when power off (safe default)
- **Material:** Plastic or brass body
- **Why:** Stops water flow for settling phase
- **Supplier:** [Amazon](https://www.amazon.com/Solenoid-Valve-Electric-Normally-Closed/dp/B01N8Y0HQK), AliExpress
- **Options:**
  - 1/4" for smaller tanks
  - 3/4" for larger systems

### B. Water Pump (Flow Manifold System) - **$18**

**Model: 12V DC Submersible Water Pump**
- **Flow Rate:** 0.5-1.5 L/min (adjustable via PWM)
- **Voltage:** 12V DC
- **Head Height:** 1-2m (sufficient for tank)
- **Type:** Brushless DC pump (quiet, long life)
- **Why:** Creates gentle laminar flow through slot cut manifold for algae sweeping
- **Supplier:** [Amazon](https://www.amazon.com/KEDSUM-Submersible-Fountain-Aquarium-Hydroponics/dp/B013J4P87A), AliExpress
- **Features:**
  - Low noise operation
  - Food-safe materials
  - Easy flow rate control
  - Can run continuously

**Alternative: Peristaltic Pump - $25-35**
- More precise flow control
- Self-priming
- Better for gentle algae handling

### C. Relay Module (2-Channel) - **$6**

**Model: 2-Channel 5V Relay Module**
- **Channels:** 2 (drain valve + pump power)
- **Input:** 5V control from GPIO
- **Output:** Switches 12V DC for valve/pump
- **Isolation:** Optocoupler isolated
- **Why:** Safely control high-power devices from Pi GPIO
- **Supplier:** [Amazon](https://www.amazon.com/HiLetgo-Channel-Isolation-Support-Trigger/dp/B00LW15A4W), electronics stores

### D. PWM Motor Speed Controller (Optional) - **$8**

**Model: 12V PWM DC Motor Speed Controller**
- **Why:** Fine-tune pump flow rate for optimal sweeping
- **Features:** Adjustable duty cycle 0-100%
- **Supplier:** Amazon, electronics stores

---

## 5. Power Supply & Distribution

### 12V DC Power Supply (2A minimum) - **$12**
- **Model:** 12V 2A wall adapter
- **Why:** Powers solenoid valve and servo
- **Supplier:** Amazon
- **Note:** Get one with barrel jack connector

### DC-DC Buck Converter (12V to 5V) - **$5** *(Optional)*
- If you want to power Pi from same 12V supply
- Step-down converter 12V → 5V 3A
- Supplier: Amazon, Adafruit

### Breadboard Power Supply Module - **$3**
- Converts 12V/9V to 5V and 3.3V rails
- Supplier: Amazon

---

## 6. Wiring & Connectors

### Jumper Wires (Male-to-Male, Male-to-Female, Female-to-Female) - **$8**
- **Quantity:** 120 pieces assorted
- **Length:** 10-30cm
- **Why:** Connect sensors to Pi GPIO and breadboard
- **Supplier:** [Amazon](https://www.amazon.com/EDGELEC-Breadboard-Optional-Assorted-Multicolored/dp/B07GD2BWPY)

### Breadboard (830 tie-points) - **$5**
- **Why:** Prototype circuits before soldering
- **Supplier:** Amazon, Adafruit

### Dupont Connector Kit - **$10**
- Male/female pins and housings
- For making custom cable lengths
- Crimping tool included

### Screw Terminal Blocks - **$6**
- **Type:** 2.54mm pitch, 2-3 position
- **Quantity:** 10-20 pieces
- **Why:** Secure sensor wire connections
- **Supplier:** Amazon

### Heat Shrink Tubing Set - **$8**
- Various sizes for protecting connections
- Supplier: Amazon

### Waterproof Cable Glands - **$8**
- **Size:** PG7 or PG9
- **Quantity:** 5-10 pieces
- **Why:** Seal sensor cables entering tank
- **Supplier:** Amazon

---

## 7. Electronic Components

### Resistor Kit (1/4W, 1Ω to 1MΩ) - **$10**
- **Quantity:** 600 pieces, 30 values
- **Includes:** 4.7kΩ for DS18B20, others for circuits
- **Supplier:** Amazon

### Capacitor Kit (Ceramic & Electrolytic) - **$12**
- For noise filtering and power stability
- Supplier: Amazon

### Diodes (1N4007) - **$3**
- **Quantity:** 20 pieces
- **Why:** Flyback protection for relay/motor
- **Supplier:** Amazon

---

## 8. Flow Manifold System Parts

### PVC Pipe (25mm diameter) - **$8**
- **Size:** 25mm (1 inch) diameter
- **Length:** 1 meter (cut to tank width ~215mm)
- **Why:** Main manifold body for water distribution
- **Supplier:** Hardware store (plumbing section), Home Depot

### PVC End Caps (25mm) - **$3**
- **Quantity:** 2 pieces
- **Why:** Seal both ends of manifold pipe
- **Supplier:** Hardware store

### PVC Cement/Glue - **$6**
- For permanent waterproof joints
- Supplier: Hardware store

### Barbed Hose Fitting (25mm to 12mm) - **$5**
- **Why:** Connect pump hose to manifold inlet
- **Supplier:** Hardware store, aquarium stores

### Silicone Tubing (Food Grade) - **$8**
- **Size:** 12mm (1/2 inch) ID
- **Length:** 2-3 meters
- **Why:** Connect pump to manifold and drain valve
- **Supplier:** Amazon, brewing supply stores

### Mounting Brackets (Stainless Steel) - **$6**
- **Type:** L-brackets or pipe clamps
- **Why:** Secure manifold to tank front wall
- **Supplier:** Hardware store

### Suction Cups (Heavy Duty) - **$8**
- **Size:** 40-50mm diameter
- **Quantity:** 3-4 pieces
- **Why:** Mount manifold inside tank without drilling glass
- **Supplier:** Aquarium stores, Amazon

### Rotary Tool or Dremel - **$30** *(if you don't have)*
- **Why:** Cut horizontal slot (8mm wide × 185mm long) in PVC pipe
- **Includes:** Cutting wheels, grinding bits
- **Supplier:** Harbor Freight, Amazon, Home Depot

### Waterproof Epoxy Resin - **$10**
- **Why:** Seal around manifold inlet, smooth edges of slot cut
- **Type:** Marine epoxy or aquarium-safe silicone
- **Supplier:** Hardware store, aquarium stores

---

## 9. Enclosure & Protection

### Waterproof Project Box (IP65) - **$15**
- **Size:** 200x120x75mm
- **Why:** Protect Raspberry Pi and electronics from humidity
- **Features:** Clear lid, cable entry ports
- **Supplier:** [Amazon](https://www.amazon.com/LeMotech-Dustproof-Waterproof-Electrical-200mmx120mmx75mm/dp/B075DJHP15)

### Silica Gel Desiccant Packets - **$6**
- Keep moisture out of electronics box
- Supplier: Amazon

---

## 10. Optional Upgrades

### Camera Module (Algae Identification) - **$25**
- **Model:** Raspberry Pi Camera Module V2 (8MP)
- **Why:** For your algae identification program
- **Supplier:** [Adafruit](https://www.adafruit.com/product/3099), Amazon

### USB Microscope - **$30-50**
- Better for detailed algae imaging
- 1000x magnification
- Supplier: Amazon

### Real-Time Clock (RTC) Module - **$6**
- **Model:** DS3231 RTC
- **Why:** Keep accurate time when Pi offline
- **Supplier:** Amazon

### UPS HAT for Raspberry Pi - **$25**
- **Model:** Geekworm X728 UPS
- **Why:** Backup power, safe shutdown during power loss
- **Supplier:** Amazon

### WiFi Range Extender - **$20** *(if needed)*
- If tank is far from router
- For remote monitoring

---

## 11. Tools (If you don't have)

### Soldering Iron Kit - **$25**
- For permanent connections
- Includes solder, stand, tips
- Supplier: Amazon

### Multimeter - **$15**
- **Essential** for troubleshooting
- Measure voltage, continuity, resistance
- Supplier: Amazon, Harbor Freight

### Wire Stripper/Crimper - **$12**
- For preparing wires
- Supplier: Amazon

### Precision Screwdriver Set - **$10**
- For Pi and electronics assembly
- Supplier: Amazon

---

## 📦 Package Recommendations

### **Starter Package (Minimum Viable System)** - ~$245
✅ Raspberry Pi 4 (4GB) + SD card + power supply  
✅ DFRobot Turbidity Sensor  
✅ DS18B20 Temperature Sensor  
✅ MCP3008 ADC  
✅ 2-Channel Relay Module  
✅ 12V Solenoid Valve  
✅ 12V DC Water Pump  
✅ PVC Pipe (25mm) + end caps + fittings  
✅ Silicone tubing  
✅ 12V Power Supply  
✅ Jumper wires + breadboard  
✅ Basic resistor kit  
✅ Waterproof enclosure  

*Skip pH sensor initially, add later when calibration solutions available*

**Key Advantage:** No mechanical scraper = fewer moving parts, lower maintenance

### **Complete System** - ~$395
Everything in Starter Package PLUS:  
✅ DFRobot pH Sensor + calibration buffers  
✅ ADS1115 (higher precision ADC)  
✅ Camera module  
✅ RTC module  
✅ PWM speed controller (fine flow control)  
✅ Mounting hardware (brackets, suction cups)  
✅ Waterproof epoxy  
✅ Tools (rotary tool for slot cutting, if needed)  

### **Professional Grade** - ~$520
Complete System PLUS:  
✅ UPS HAT  
✅ USB Microscope (better imaging)  
✅ Industrial turbidity sensor  
✅ Peristaltic pump (precision flow control)  
✅ Quality soldering kit  
✅ Flow rate sensor (measure actual pump performance)  

---

## 🌐 Recommended Suppliers

### **Primary (US):**
- **Adafruit** - High quality, excellent documentation
- **Amazon** - Fast shipping, variety
- **DFRobot** - Direct from manufacturer

### **Budget Options:**
- **AliExpress** - Cheap, but 2-4 week shipping
- **eBay** - Used/surplus components

### **Specialty:**
- **Digi-Key** / **Mouser** - Electronic components, professional
- **McMaster-Carr** - Mechanical parts, industrial quality

---

## 📋 Shopping Links by Category

### **All-in-One Kits to Consider:**

**Raspberry Pi Starter Kit - $100**
- Includes Pi, case, power supply, SD card, heatsinks
- Example: [CanaKit Raspberry Pi 4 Starter Kit](https://www.amazon.com/CanaKit-Raspberry-Starter-Premium-Black/dp/B07BCC8PK7)

**Sensor Bundle - $80**
- Turbidity + pH + Temperature all together
- Search: "Arduino water quality sensor kit"

---

## ⚡ Wiring Diagram Coming

When you're ready to order, I can provide:
1. **Complete wiring diagram** showing all connections
2. **Pin assignments** for each component
3. **Assembly instructions** step-by-step
4. **Updated code** with your specific sensor models

---

## 💰 **Total Cost Estimate:**

| Configuration | Cost | Timeline | Features |
|--------------|------|----------|----------|
| **Minimum Viable** | $245 | Order now, start with basics | Pump + slot cut manifold |
| **Recommended** | $395 | Full featured, room to grow | + pH sensor + camera |
| **Professional** | $520 | Production quality | + precision pump + flow sensor |

**Note:** Prices are approximate USD as of January 2026. Check current prices as components fluctuate.

---

## 🚀 Recommended Ordering Strategy

### **Phase 1 - Order Now (Core System):**
- Raspberry Pi 4 + accessories ($75 total)
- **DS18B20 Temperature sensor** ($8) ✅ Easy - 1-Wire
- **DFRobot SEN0554 Turbidity sensor** ($35) ✅ Easy - I2C
- **Atlas Scientific pH sensor** ($60) ✅ Easy - I2C
- Relay module ($6)
- 12V solenoid valve ($15)
- 12V DC water pump ($18)
- PVC pipe + fittings ($15)
- Silicone tubing ($8)
- Basic wiring kit ($12)

**Total Phase 1: ~$252**

**Why this order:**
- All digital sensors - no ADC needed!
- Simple I2C wiring - just 4 wires per sensor
- Can start coding immediately with simulation
- Proven reliable for algae cultivation

### **Phase 2 - Order Later (Optional Upgrades):**
- PWM speed controller ($8) - fine-tune flow after testing
- Camera module ($30) - for algae ID integration
- Mounting hardware ($10) - after testing manifold positioning
- Backup sensors ($40) - spare turbidity/pH sensors

---

## 🔌 **Wiring Guide (I2C Sensors)**

### **Super Simple Wiring - All I2C Sensors Share Same Bus!**

```
Raspberry Pi GPIO Header:
┌─────────────────────┐
│ 3.3V  ●●  5V        │  Pin 1 (3.3V) → All sensor VCC
│ SDA   ●●  5V        │  Pin 3 (SDA)  → All sensor SDA
│ SCL   ●●  GND       │  Pin 5 (SCL)  → All sensor SCL
│ GPIO4 ●●  GND       │  Pin 6 (GND)  → All sensor GND
│  ...                │  Pin 7 (GPIO4) → DS18B20 Data
└─────────────────────┘
```

### **Sensor Connections:**

**Turbidity Sensor (DFRobot SEN0554):**
- VCC → Pi Pin 1 (3.3V)
- GND → Pi Pin 6 (GND)
- SDA → Pi Pin 3 (SDA)
- SCL → Pi Pin 5 (SCL)

**pH Sensor (Atlas Scientific EZO-pH):**
- VCC → Pi Pin 1 (3.3V)
- GND → Pi Pin 6 (GND)
- SDA → Pi Pin 3 (SDA)
- SCL → Pi Pin 5 (SCL)

**Temperature Sensor (DS18B20):**
- Red (VCC) → Pi Pin 1 (3.3V)
- Black (GND) → Pi Pin 6 (GND)
- Yellow (Data) → Pi Pin 7 (GPIO4)
- **4.7kΩ resistor** between VCC and Data

**Relay Module (for Pump/Valve):**
- VCC → Pi Pin 2 (5V)
- GND → Pi Pin 6 (GND)
- IN1 → Pi Pin 11 (GPIO17) - Pump control
- IN2 → Pi Pin 12 (GPIO18) - Valve control

### **I2C Address Summary:**
- Turbidity: 0x30 (default)
- pH: 0x63 (default)
- No address conflicts - just works!

### **Advantages of I2C Sensors:**
✅ Only 4 wires per sensor (VCC, GND, SDA, SCL)
✅ All sensors share same SDA/SCL bus
✅ No ADC needed - direct digital reading
✅ Better accuracy than analog
✅ Auto-calibration storage in sensor EEPROM
✅ Python libraries included
✅ Plug-and-play - less soldering

---

## 🔧 **System Design Notes**

### Flow Manifold Construction:
1. Cut PVC pipe to tank width (~215mm)
2. Mark slot position: 8mm wide × 185mm long on bottom of pipe
3. Use rotary tool to cut horizontal slot (creates "water knife" effect)
4. Smooth edges with file/sandpaper
5. Glue end caps with PVC cement
6. Install barbed fitting at one end for pump hose
7. Mount 10mm above bottom using suction cups or brackets

### System Advantages:
✅ No moving parts in tank (higher reliability)
✅ Gentle flow prevents algae cell damage
✅ Continuous operation possible
✅ Easy to adjust flow rate (PWM control)
✅ Scalable to larger tanks
✅ Lower maintenance
✅ Slot cut creates uniform water curtain (better than holes)
✅ Works with standard rectangular tanks (no modifications needed)

---

Want me to create:
1. **Detailed wiring diagram** for pump + valve + sensors?
2. **Step-by-step manifold construction guide** with photos/diagrams?
3. **Calibration procedures** for turbidity and pH sensors?
4. **Flow rate calculation** for optimal algae collection?
