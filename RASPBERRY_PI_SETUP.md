# 🔌 Connecting Raspberry Pi to Mobile App

## Architecture Overview

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│  Raspberry Pi   │─────▶│   Railway    │◀─────│  Mobile App │
│   (sensors)     │ POST │   Backend    │ GET  │   (user)    │
│                 │      │  + Database  │      │             │
└─────────────────┘      └──────────────┘      └─────────────┘
```

## Data Format: JSON over HTTP (NOT CSV/XLS)

Sensors send data as JSON via HTTP POST to Railway API:
```json
{
  "tank_id": 1,
  "ph": 7.2,
  "temperature": 25.5,
  "turbidity": 285
}
```

## Setup Steps

### 1. Mobile App (Already Done ✅)
- Create a tank with algae species and volume
- Note the tank ID from the app

### 2. Raspberry Pi Setup

**On your Raspberry Pi:**

```bash
# 1. Connect to WiFi
# Make sure Pi has internet access

# 2. Install Python dependencies
pip3 install requests

# 3. Clone your GitHub repo (when hardware arrives)
git clone https://github.com/lab-Kason/algae_box.git
cd algae_box

# 4. Edit configuration
nano main_cloud.py
# Change these lines:
#   RAILWAY_API_URL = "https://web-production-f856a8.up.railway.app"
#   TANK_ID = 1  # Use the tank ID from your mobile app

# 5. Run the sensor system
python3 main_cloud.py
```

### 3. How It Works

**Raspberry Pi (every 10 seconds):**
1. Reads sensors (pH, temperature, turbidity)
2. Sends HTTP POST to Railway API
3. Gets recommendations every 50 seconds

**Railway Backend:**
- Receives sensor data
- Stores in SQLite database
- Serves data to mobile app
- Generates recommendations

**Mobile App (auto-refresh every 10 seconds):**
- Fetches latest sensor readings
- Displays on dashboard
- Shows recommendations

## Testing Before Hardware Arrives

**Right now (simulation mode):**
```bash
# On your Mac (for testing)
python3 main_cloud.py
```

You'll see simulated sensor data being sent to Railway, and your mobile app will display it!

## Connection Requirements

- **Raspberry Pi**: WiFi connection to internet
- **No direct connection** between Pi and phone needed
- **Both connect** to Railway backend independently

## Troubleshooting

**If Pi can't connect:**
```bash
# Test Railway connection
curl https://web-production-f856a8.up.railway.app/api/health

# Check WiFi
ping google.com

# Check Python packages
pip3 list | grep requests
```

**If mobile app shows old data:**
- Pull down to refresh
- Check auto-refresh is enabled (every 10s)

## File Formats (What NOT to use)

❌ **CSV files** - No, sensors send to API directly
❌ **Excel files** - No, real-time data goes to database
❌ **Local database** - No, use Railway cloud database
✅ **HTTP POST to API** - Yes! This is the way
