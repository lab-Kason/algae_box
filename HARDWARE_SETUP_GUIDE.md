# Hardware Setup Guide - I2C Sensors

## 🎯 Quick Start

Your sensors are **digital I2C** - much easier than analog! All sensors share the same 2 data wires.

---

## 📦 What You'll Need

From HARDWARE_BOM.md:
- ✅ DFRobot SEN0554 Turbidity Sensor (I2C)
- ✅ Atlas Scientific EZO-pH Kit (I2C)
- ✅ DS18B20 Temperature Sensor (1-Wire)
- ✅ Raspberry Pi 4
- ✅ Jumper wires
- ✅ 4.7kΩ resistor (for DS18B20)

---

## 🔌 Wiring Connections

### Raspberry Pi GPIO Pinout (Pins 1-10)

```
  3.3V   5V
   ●     ●   Pin 1, 2
  SDA   5V
   ●     ●   Pin 3, 4
  SCL  GND
   ●     ●   Pin 5, 6
GPIO4 GPIO14
   ●     ●   Pin 7, 8
  GND  GPIO15
   ●     ●   Pin 9, 10
```

### 1. Turbidity Sensor (DFRobot SEN0554)

```
Sensor → Raspberry Pi
VCC    → Pin 1 (3.3V)
GND    → Pin 6 (GND)
SDA    → Pin 3 (SDA)
SCL    → Pin 5 (SCL)
```

**I2C Address:** 0x30

### 2. pH Sensor (Atlas Scientific EZO-pH)

```
Sensor → Raspberry Pi
VCC    → Pin 1 (3.3V)  ← Same as turbidity!
GND    → Pin 6 (GND)   ← Same as turbidity!
SDA    → Pin 3 (SDA)   ← Same as turbidity!
SCL    → Pin 5 (SCL)   ← Same as turbidity!
```

**I2C Address:** 0x63

**Important:** All I2C sensors share the SAME SDA/SCL wires!

### 3. Temperature Sensor (DS18B20)

```
DS18B20 Wire → Raspberry Pi
Red (VCC)    → Pin 1 (3.3V)
Black (GND)  → Pin 6 (GND)
Yellow (Data)→ Pin 7 (GPIO4)

ALSO: 4.7kΩ resistor between VCC and Data (pullup)
```

### Final Wiring Summary

```
All sensors connect to:
- Pin 1 (3.3V)  → All VCC wires (4 sensors)
- Pin 6 (GND)   → All GND wires (4 sensors)
- Pin 3 (SDA)   → Turbidity + pH (shared I2C)
- Pin 5 (SCL)   → Turbidity + pH (shared I2C)
- Pin 7 (GPIO4) → Temperature (1-Wire)
```

---

## ⚙️ Raspberry Pi Setup

### 1. Enable I2C Interface

```bash
# Open Raspberry Pi configuration
sudo raspi-config

# Navigate to:
# Interface Options → I2C → Enable

# Reboot
sudo reboot
```

### 2. Enable 1-Wire (for DS18B20)

```bash
# Open config again
sudo raspi-config

# Navigate to:
# Interface Options → 1-Wire → Enable

# Reboot
sudo reboot
```

### 3. Install I2C Tools

```bash
# Install utilities
sudo apt-get update
sudo apt-get install -y i2c-tools python3-smbus

# Test I2C bus
sudo i2cdetect -y 1
```

**Expected output:**
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: 30 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --  ← Turbidity
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- 63 -- -- -- -- -- -- -- -- -- -- -- --  ← pH
70: -- -- -- -- -- -- -- --
```

### 4. Install Python Libraries

```bash
# Install required packages
pip3 install smbus2
```

### 5. Test Sensors

```bash
cd /Users/kasonchiu/Documents/GitHub/algae_box

# Edit config.py - turn off simulation
nano config.py
# Change: SIMULATION_MODE = False

# Run sensor test
python3 main_cloud.py
```

---

## 🧪 Sensor Testing

### Test Turbidity (I2C)

```python
import smbus2

bus = smbus2.SMBus(1)
address = 0x30

# Read 2 bytes from register 0x00
data = bus.read_i2c_block_data(address, 0x00, 2)
ntu = ((data[0] << 8) | data[1]) / 10.0
print(f"Turbidity: {ntu} NTU")
```

### Test pH (I2C)

```python
import smbus2
import time

bus = smbus2.SMBus(1)
address = 0x63

# Send 'R' (read) command
bus.write_byte(address, ord('R'))
time.sleep(1.0)

# Read response
response = bus.read_i2c_block_data(address, 0, 31)
if response[0] == 1:
    ph_string = ''.join(chr(b) for b in response[1:] if b != 0)
    print(f"pH: {ph_string}")
```

### Test Temperature (1-Wire)

```python
import glob

# Find DS18B20 device
device = glob.glob('/sys/bus/w1/devices/28*')[0]
file = device + '/w1_slave'

# Read temperature
with open(file, 'r') as f:
    lines = f.readlines()
    temp_pos = lines[1].find('t=')
    temp_c = float(lines[1][temp_pos+2:]) / 1000.0
    print(f"Temperature: {temp_c}°C")
```

---

## 🔧 Troubleshooting

### I2C Sensors Not Detected

```bash
# Check I2C is enabled
sudo raspi-config
# → Interface Options → I2C → Enable

# Check devices on bus
sudo i2cdetect -y 1

# If nothing appears:
# - Check wiring (SDA, SCL, VCC, GND)
# - Make sure sensors are powered (3.3V)
# - Try different jumper wires
```

### DS18B20 Not Found

```bash
# Check 1-Wire is enabled
sudo raspi-config
# → Interface Options → 1-Wire → Enable

# List 1-Wire devices
ls /sys/bus/w1/devices/

# Should see: 28-xxxxxxxxxxxx

# If not:
# - Check 4.7kΩ pullup resistor between VCC and Data
# - Verify GPIO4 connection
# - Try different DS18B20 sensor
```

### Permission Denied

```bash
# Add user to I2C group
sudo usermod -a -G i2c $USER

# Logout and login again
```

### Sensors Work But Values Wrong

**Turbidity:**
- Sensor may need water to calibrate
- Try in clear water first (should read <5 NTU)
- Then test with algae sample

**pH:**
- Needs calibration with buffer solutions (pH 4, 7, 10)
- See Atlas Scientific documentation for calibration commands
- Calibration stored in sensor EEPROM

**Temperature:**
- Should be accurate out of box (±0.5°C)
- Test in ice water (0°C) or room temp

---

## 📊 System Integration

Once sensors work individually:

1. **Turn off simulation mode:**
   ```bash
   nano config.py
   # Set: SIMULATION_MODE = False
   ```

2. **Run cloud-connected system:**
   ```bash
   python3 main_cloud.py
   ```

3. **Sensors will:**
   - Auto-detect species from Railway API
   - Use species-specific optimal values
   - Send data to cloud every 10 seconds
   - Display in mobile app

4. **Monitor on mobile app:**
   - Real pH, temperature, turbidity
   - Species-aware recommendations
   - Harvest alerts

---

## ✅ Success Checklist

- [ ] I2C enabled in raspi-config
- [ ] 1-Wire enabled in raspi-config
- [ ] `sudo i2cdetect -y 1` shows 0x30 and 0x63
- [ ] `/sys/bus/w1/devices/28*` exists
- [ ] `pip3 install smbus2` successful
- [ ] Individual sensor tests pass
- [ ] `SIMULATION_MODE = False` in config.py
- [ ] `python3 main_cloud.py` runs without errors
- [ ] Mobile app shows real sensor data

---

## 🆘 Need Help?

**Check logs:**
```bash
python3 main_cloud.py 2>&1 | tee sensor_log.txt
```

**Common issues:**
1. "No module named 'smbus2'" → Run `pip3 install smbus2`
2. "Permission denied" → Add to i2c group, reboot
3. "Address not found" → Check wiring, run i2cdetect
4. "CRC failed" → Bad DS18B20 connection, check pullup resistor

**Resources:**
- DFRobot SEN0554: https://wiki.dfrobot.com/
- Atlas Scientific EZO-pH: https://atlas-scientific.com/
- DS18B20: https://www.maximintegrated.com/en/products/sensors/DS18B20.html
