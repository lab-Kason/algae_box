# Arduino ESP32 Setup Guide
# ESP32设置指南

## 📦 Required Software 所需软件

### 1. Install Arduino IDE
**Download:** https://www.arduino.cc/en/software

**Supported:**
- Windows 7+
- macOS 10.14+
- Linux

---

## 🔧 Configure Arduino IDE for ESP32

### Step 1: Add ESP32 Board Support
1. Open Arduino IDE
2. Go to **File → Preferences** (文件 → 首选项)
3. In **"Additional Boards Manager URLs"** field, add:
   ```
   https://dl.espressif.com/dl/package_esp32_index.json
   ```
4. Click **OK**

### Step 2: Install ESP32 Board
1. Go to **Tools → Board → Boards Manager** (工具 → 开发板 → 开发板管理器)
2. Search for **"esp32"**
3. Install **"esp32 by Espressif Systems"**
4. Wait for download and installation (~300MB)

### Step 3: Select ESP32 Board
1. Go to **Tools → Board → ESP32 Arduino**
2. Select **"ESP32 Dev Module"** or **"NodeMCU-32S"**

---

## 📚 Install Required Libraries

### Via Library Manager (Recommended)

1. Go to **Sketch → Include Library → Manage Libraries** (项目 → 加载库 → 管理库)
2. Search and install each:

```
✅ OneWire by Paul Stoffregen
✅ DallasTemperature by Miles Burton
✅ ArduinoJson by Benoit Blanchon (version 6.x)
```

**Built-in libraries (no install needed):**
- WiFi.h (ESP32 built-in)
- HTTPClient.h (ESP32 built-in)
- Wire.h (Arduino built-in)

---

## 🔌 Hardware Setup

### ESP32 DevKit V1 Pinout
```
                     ESP32
     ┌─────────────────────────────┐
     │                             │
     │  3V3 ●●  VIN(5V)            │
     │  GND ●●  GND                │
     │  D21 ●●  D22    (I2C)       │  GPIO21=SDA, GPIO22=SCL
     │  D4  ●●  D17    (Sensors)   │  GPIO4=Temp, GPIO17=Pump
     │  D16 ●●  D18                │  GPIO16=Valve
     │  ...                        │
     └─────────────────────────────┘
```

### Wiring Connections 接线图

**浊度传感器 Turbidity Sensor (I2C 0x30):**
```
Sensor → ESP32
VCC    → 3V3
GND    → GND
SDA    → GPIO21
SCL    → GPIO22
```

**pH传感器 pH Sensor (I2C 0x63):**
```
Sensor → ESP32
VCC    → 3V3
GND    → GND
SDA    → GPIO21 (same as turbidity)
SCL    → GPIO22 (same as turbidity)
```

**温度传感器 Temperature DS18B20 (1-Wire):**
```
DS18B20 → ESP32
Red     → 3V3
Black   → GND
Yellow  → GPIO4
```
⚠️ **Important:** Add 4.7kΩ resistor between 3V3 and GPIO4 (Data line)

**继电器模块 Relay Module:**
```
Relay   → ESP32
VCC     → VIN (5V)
GND     → GND
IN1     → GPIO17 (Pump control)
IN2     → GPIO16 (Valve control)
```

---

## 📝 Upload Code to ESP32

### Step 1: Configure Code
Open `algae_box_esp32.ino` and edit:

```cpp
// Line 17-18: WiFi credentials
const char* WIFI_SSID = "Your_WiFi_Name";
const char* WIFI_PASSWORD = "Your_WiFi_Password";

// Line 21: API endpoint
const char* API_URL = "https://your-backend.railway.app/api/sensors/reading";

// Line 22: Tank ID
const int TANK_ID = 1;

// Line 34: Simulation mode
bool SIMULATION_MODE = true; // Change to false when real sensors connected
```

### Step 2: Connect ESP32
1. Connect ESP32 to computer via USB cable
2. **Tools → Port** → Select correct COM port (Windows) or `/dev/cu.usbserial` (Mac)

### Step 3: Upload
1. Click **Upload** button (→) or **Sketch → Upload**
2. Wait for compilation and upload (~30 seconds)
3. Should see: **"Hard resetting via RTS pin..."** = Success

### Step 4: Open Serial Monitor
1. **Tools → Serial Monitor** (工具 → 串口监视器)
2. Set baud rate to **115200**
3. You should see:
```
============================================================
  🌊 ALGAE BOX - ESP32 SENSOR SYSTEM 🌊
============================================================
✅ I2C initialized
✅ DS18B20 initialized
📡 Connecting to WiFi: Your_WiFi_Name
...
✅ WiFi connected
   IP address: 192.168.1.xxx
🔬 Running in SIMULATION mode
🔄 Starting sensor monitoring...
[Reading #1]
  Turbidity: 90.23 NTU
  pH: 6.78
  Temp: 25.3°C
✅ Sent to cloud (HTTP 200)
```

---

## 🔍 Troubleshooting 故障排除

### ❌ ESP32 not detected
**Solution:**
- Install CH340/CP2102 USB driver
- Try different USB cable (must be data cable, not charge-only)
- Press and hold BOOT button while uploading

### ❌ Compilation error: "WiFi.h not found"
**Solution:**
- Make sure ESP32 board is selected in Tools → Board
- Reinstall ESP32 board support

### ❌ Upload failed: "Serial port not found"
**Solution:**
- Check correct port selected
- Close other programs using serial port (Arduino IDE, serial monitor)

### ❌ WiFi connection failed
**Solution:**
- Check SSID and password (case-sensitive)
- ESP32 only supports 2.4GHz WiFi (not 5GHz)
- Move closer to router

### ❌ HTTP error: Connection refused
**Solution:**
- Check API_URL is correct
- Test URL in browser first
- Make sure backend is running

### ❌ Sensor not found (0x30 or 0x63)
**Solution:**
- Check I2C wiring (SDA, SCL, VCC, GND)
- Verify sensor power (3.3V for most sensors)
- Use I2C scanner code to find address

---

## 🧪 Test Individual Sensors

### I2C Scanner Code
```cpp
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22); // SDA=21, SCL=22
  Serial.println("I2C Scanner");
}

void loop() {
  for(byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if(Wire.endTransmission() == 0) {
      Serial.printf("Device found at 0x%02X\n", addr);
    }
  }
  delay(5000);
}
```

Expected output:
```
Device found at 0x30  (Turbidity)
Device found at 0x63  (pH)
```

---

## 🔄 Switch from Simulation to Real Sensors

When hardware arrives:

### Step 1: Connect all sensors (see wiring above)

### Step 2: Test sensors individually
- Use I2C scanner to verify addresses
- Check DS18B20 with example code

### Step 3: Change code
```cpp
bool SIMULATION_MODE = false; // Line 34
```

### Step 4: Re-upload and monitor Serial output
Should see real sensor values:
```
✅ Turbidity sensor found at 0x30
✅ pH sensor found at 0x63
✅ Temperature sensor found
[Reading #1]
  Turbidity: 125.4 NTU  (real value)
  pH: 7.23              (real value)
  Temp: 24.8°C          (real value)
```

---

## 📊 Monitor on Mobile App

1. Make sure ESP32 is sending data (check Serial Monitor)
2. Open mobile app
3. Navigate to your tank dashboard
4. Should see live updates every 10 seconds

---

## 💡 Power Options

### Option 1: USB Power (Development)
- Connect ESP32 to computer via USB
- Good for testing and debugging
- Computer must stay on

### Option 2: USB Charger (Portable)
- 5V 2A USB charger + USB cable
- ESP32 powered independently
- Good for deployment

### Option 3: Battery (Mobile)
- 18650 lithium battery + holder
- Add voltage regulator (7-12V → 5V)
- Longest runtime

**Estimated power consumption:**
- ESP32 + sensors: ~150mA
- With WiFi active: ~200-250mA
- 2000mAh battery = ~8-10 hours

---

## 🎯 Next Steps

1. ✅ Install Arduino IDE
2. ✅ Add ESP32 board support
3. ✅ Install libraries
4. ✅ Upload test code
5. ✅ Verify WiFi connection
6. ✅ Check data on mobile app
7. ⏳ Wait for real sensors
8. ⏳ Switch to real mode
