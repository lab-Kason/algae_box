# Algae Box - Complete Hardware Shopping List

## 🛒 Complete Bill of Materials (BOM)

Last Updated: January 7, 2026

---

## 1. Main Controller

### Raspberry Pi 4 Model B (4GB) - **$55**
- **Why:** Sufficient processing power, GPIO pins, runs Python
- **Alternative:** Raspberry Pi Zero 2 W ($15) - cheaper, lower power, still capable
- **Supplier:** [Adafruit](https://www.adafruit.com/product/4296), [Amazon](https://www.amazon.com/Raspberry-Model-2019-Quad-Bluetooth/dp/B07TC2BK1X)
- **Includes:** Quad-core processor, WiFi, Bluetooth, 40 GPIO pins

### MicroSD Card (32GB Class 10) - **$10**
- **Model:** SanDisk Ultra 32GB
- **Why:** OS storage and data logging
- **Supplier:** Amazon, Best Buy

### Power Supply (5V 3A USB-C) - **$10**
- **Model:** Official Raspberry Pi Power Supply
- **Why:** Stable 5V 3A for Pi + sensors
- **Supplier:** Adafruit, Amazon

---

## 2. Sensors

### A. Turbidity Sensor - **$12**

**Option 1: DFRobot SEN0189 (Recommended)**
- **Model:** SEN0189 Gravity Analog Turbidity Sensor
- **Range:** 0-1000 NTU
- **Output:** 0-4.5V analog
- **Why:** Affordable, well-documented, Arduino/Pi compatible
- **Supplier:** [DFRobot](https://www.dfrobot.com/product-1394.html), [Amazon](https://www.amazon.com/DFRobot-Turbidity-Detection-Suspended-Particles/dp/B07FNGY6TT)
- **Datasheet:** [Link](https://wiki.dfrobot.com/Turbidity_sensor_SKU__SEN0189)

**Option 2: TSW-10 Turbidity Sensor - $18**
- Higher accuracy, industrial grade
- Supplier: AliExpress, eBay

### B. pH Sensor - **$25**

**Model: DFRobot SEN0161-V2 pH Sensor Kit**
- **Range:** pH 0-14
- **Accuracy:** ±0.1 pH @ 25°C
- **Output:** Analog voltage
- **Includes:** pH probe, BNC connector, signal conditioning board
- **Why:** Waterproof probe, pre-calibrated, easy Arduino/Pi interface
- **Supplier:** [DFRobot](https://www.dfrobot.com/product-1782.html), [Amazon](https://www.amazon.com/DFRobot-Gravity-Analog-Sensor-Arduino/dp/B01ENIXO7E)
- **Note:** Requires periodic calibration with buffer solutions

**pH Calibration Buffer Set (pH 4.0, 7.0, 10.0) - $12**
- Essential for accurate readings
- Supplier: Amazon, scientific supply stores

### C. Temperature Sensor - **$8**

**Model: DS18B20 Waterproof Digital Temperature Sensor**
- **Range:** -55°C to +125°C
- **Accuracy:** ±0.5°C
- **Interface:** 1-Wire (single data pin)
- **Cable:** 1m waterproof stainless steel probe
- **Why:** Waterproof, accurate, widely supported, simple wiring
- **Supplier:** [Adafruit](https://www.adafruit.com/product/381), [Amazon](https://www.amazon.com/Waterproof-Digital-Temperature-DS18B20-Raspberry/dp/B012C597T0)

**4.7kΩ Pull-up Resistor** (for DS18B20) - **$0.10**
- Required for 1-Wire protocol
- Included in resistor kit below

---

## 3. Analog-to-Digital Converter (ADC)

### MCP3008 8-Channel 10-Bit ADC - **$4**

**Model: Microchip MCP3008**
- **Why:** Raspberry Pi doesn't have analog inputs; this converts analog sensor signals to digital
- **Channels:** 8 (turbidity + pH + 6 spare)
- **Resolution:** 10-bit (0-1023 values)
- **Interface:** SPI
- **Supplier:** [Adafruit](https://www.adafruit.com/product/856), [Amazon](https://www.amazon.com/Waveshare-MCP3008-Raspberry-Interface-Channels/dp/B07WGCWW43)

**Alternative: ADS1115 16-Bit ADC - $10**
- Higher resolution (16-bit vs 10-bit)
- I2C interface
- Better for precise pH readings

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

### B. Servo Motor (Shovel Mechanism) - **$12**

**Model: MG996R High Torque Metal Gear Servo**
- **Torque:** 11 kg·cm @ 6V
- **Rotation:** 180° (0-180°)
- **Voltage:** 4.8-7.2V
- **Why:** Strong enough to operate shovel/scraper mechanism
- **Supplier:** [Amazon](https://www.amazon.com/Smraza-Helicopter-Airplane-Control-Arduino/dp/B07L5FQVXV), hobby stores

**Alternative: Linear Actuator - $25-40**
- If you need push/pull motion instead of rotation
- 12V DC, 50-100mm stroke length

### C. Relay Module (2-Channel) - **$6**

**Model: 2-Channel 5V Relay Module**
- **Channels:** 2 (valve + shovel power)
- **Input:** 5V control from GPIO
- **Output:** Switches 12V DC for valve/servo
- **Isolation:** Optocoupler isolated
- **Why:** Safely control high-power devices from Pi GPIO
- **Supplier:** [Amazon](https://www.amazon.com/HiLetgo-Channel-Isolation-Support-Trigger/dp/B00LW15A4W), electronics stores

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

## 8. Mechanical Parts (Shovel/Scraper Mechanism)

### Acrylic Sheet (3mm thick) - **$10**
- **Size:** 300x200mm
- **Why:** Build custom shovel/scraper blade
- **Supplier:** Hardware store, Amazon

### Stainless Steel Sheet (0.5mm) - **$8** *(Alternative)*
- More durable for scraper
- Supplier: Hardware store

### M3 Bolts, Nuts, Washers Set - **$10**
- Various lengths (6-30mm)
- Mounting hardware
- Supplier: Amazon, hardware store

### Hinges (Small, Stainless Steel) - **$5**
- For shovel opening mechanism
- Supplier: Hardware store

### Silicone Tubing (Food Grade) - **$8**
- **Size:** 1/2 inch ID
- **Length:** 2-3 meters
- **Why:** Connect valve to tank drainage
- **Supplier:** Amazon, brewing supply stores

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

### **Starter Package (Minimum Viable System)** - ~$230
✅ Raspberry Pi 4 (4GB) + SD card + power supply  
✅ DFRobot Turbidity Sensor  
✅ DS18B20 Temperature Sensor  
✅ MCP3008 ADC  
✅ 2-Channel Relay Module  
✅ 12V Solenoid Valve  
✅ MG996R Servo Motor  
✅ 12V Power Supply  
✅ Jumper wires + breadboard  
✅ Basic resistor kit  
✅ Waterproof enclosure  

*Skip pH sensor initially, add later when calibration solutions available*

### **Complete System** - ~$380
Everything in Starter Package PLUS:  
✅ DFRobot pH Sensor + calibration buffers  
✅ ADS1115 (higher precision ADC)  
✅ Camera module  
✅ RTC module  
✅ All mechanical parts  
✅ Tools (if needed)  

### **Professional Grade** - ~$500
Complete System PLUS:  
✅ UPS HAT  
✅ USB Microscope (better imaging)  
✅ Industrial turbidity sensor  
✅ Linear actuator (instead of servo)  
✅ Quality soldering kit  

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

| Configuration | Cost | Timeline |
|--------------|------|----------|
| **Minimum Viable** | $230 | Order now, start with basics |
| **Recommended** | $380 | Full featured, room to grow |
| **Professional** | $500 | Production quality |

**Note:** Prices are approximate USD as of January 2026. Check current prices as components fluctuate.

---

## 🚀 Recommended Ordering Strategy

### **Phase 1 - Order Now:**
- Raspberry Pi + accessories
- Turbidity sensor
- Temperature sensor  
- MCP3008 ADC
- Relay module
- Solenoid valve
- Basic wiring kit

**Start coding and testing while waiting for:**

### **Phase 2 - Order Later:**
- pH sensor (requires calibration knowledge)
- Servo/actuator (after designing shovel mechanism)
- Camera module (for algae ID integration)
- Mechanical parts (custom to your tank)

---

Want me to create:
1. **Detailed wiring diagram** for specific components?
2. **Assembly instructions** for the shovel mechanism?
3. **Calibration procedures** for each sensor?
