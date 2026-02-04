# Algae Box - Streamlit + QR Code Version

A simpler alternative to the Flutter APK approach. Uses an OLED display on the ESP32 to show a QR code that users scan to access the monitoring dashboard in their browser.

## Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│  ESP32 + OLED   │ ── WiFi POST ───► │  PythonAnywhere │
│  Display QR     │                    │  Flask Backend  │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
    User scans QR                         Streamlit reads
         │                                      │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│  Phone Browser  │ ◄───────────────── │  Streamlit App  │
│  (No app needed)│                    │  (Web Frontend) │
└─────────────────┘                    └─────────────────┘
```

## Components

### 1. ESP32 + OLED Display (`esp32_oled/`)
- ESP32-S3 with SSD1306 OLED display
- Shows QR code linking to Streamlit dashboard
- Alternates between QR code and sensor readings
- Sends sensor data to backend every 10 seconds

### 2. Streamlit Web App (`app.py`)
- Real-time sensor dashboard
- Works on any phone browser (no app install needed)
- Auto-refresh every 10 seconds
- Shows pH, temperature, turbidity, recommendations, history charts

### 3. Backend (existing PythonAnywhere)
- Same Flask backend as before
- No changes needed

## Hardware Required

| Component | Model | Purpose | ~Cost |
|-----------|-------|---------|-------|
| ESP32-S3 | ESP32-S3-DevKitC-1 | Main controller | $8 |
| OLED Display | SSD1306 128x64 I2C | QR code + sensor display | $5 |
| Sensors | (same as before) | pH, temp, turbidity | varies |

## Setup

### 1. Deploy Streamlit App

**Option A: Streamlit Cloud (Free)**
1. Push this folder to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Deploy `streamlit_qr/app.py`
5. Get your URL (e.g., `https://algae-box.streamlit.app`)

**Option B: Local Testing**
```bash
cd streamlit_qr
pip install -r requirements.txt
streamlit run app.py
```

### 2. Update ESP32 Code
Edit `esp32_oled/sketch.ino`:
- Change `STREAMLIT_URL` to your deployed Streamlit URL
- Change `WIFI_SSID` and `WIFI_PASSWORD` for real hardware
- Change `TANK_ID` if using multiple tanks

### 3. Wokwi Simulation
1. Go to [wokwi.com](https://wokwi.com)
2. Create new ESP32-S3 project
3. Copy `esp32_oled/sketch.ino` to the editor
4. Copy `esp32_oled/diagram.json` to the diagram tab
5. Add libraries: ArduinoJson, Adafruit GFX, Adafruit SSD1306, QRCode
6. Run simulation

### 4. Real Hardware
1. Connect OLED to ESP32-S3:
   - VCC → 3.3V
   - GND → GND
   - SDA → GPIO 8
   - SCL → GPIO 9
2. Upload code via Arduino IDE
3. Connect sensors as before

## Usage

1. **Power on** the ESP32
2. **Wait** for WiFi connection
3. **Scan QR code** on the OLED display
4. **View dashboard** in your phone browser
5. **Adjust potentiometers** (simulation) or real sensors
6. **Watch data update** every 10 seconds

## Advantages over APK

- ✅ No app installation required
- ✅ Works on any phone (iOS, Android)
- ✅ Instant updates (just redeploy Streamlit)
- ✅ Easier development (Python only)
- ✅ QR code makes tank identification seamless
- ✅ Desktop browser access too

## Files

```
streamlit_qr/
├── app.py              # Streamlit web dashboard
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── esp32_oled/
    ├── sketch.ino     # ESP32 code with OLED + QR
    ├── diagram.json   # Wokwi circuit diagram
    └── libraries.txt  # Required Arduino libraries
```
