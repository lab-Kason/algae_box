/*
 * Algae Box ESP32-S3 with OLED Display + QR Code
 * Shows tank QR code for easy mobile access
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "qrcode.h"

// ============== CONFIGURATION ==============
// WiFi credentials
const char* WIFI_SSID = "Wokwi-GUEST";  // Change for real hardware
const char* WIFI_PASSWORD = "";

// Backend API
const char* API_URL = "https://labkason.pythonanywhere.com/api/sensors/reading";
const int TANK_ID = 1;

// Streamlit URL (where users will be directed)
// Change TANK_ID above and this URL for each tank's ESP32
const char* STREAMLIT_URL = "https://algaebox-rdmdjyaytxgplld4gkgxcl.streamlit.app/?tank=1";

// OLED Display (SSD1306 128x64)
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_I2C_ADDR 0x3C

// I2C Pins for ESP32-S3
#define I2C_SDA 8
#define I2C_SCL 9

// Sensor Pins (potentiometers for simulation)
const int TURBIDITY_PIN = 4;
const int PH_PIN = 5;
const int TEMP_PIN = 6;

// Timing
const unsigned long SEND_INTERVAL = 10000;  // 10 seconds
const unsigned long DISPLAY_SWITCH = 5000;  // Switch display every 5s
unsigned long lastSendTime = 0;
unsigned long lastDisplaySwitch = 0;
bool showQR = true;

// ============== OBJECTS ==============
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
QRCode qrcode;

// ============== SETUP ==============
void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("============================================");
  Serial.println("  🌿 ALGAE BOX - ESP32-S3 + OLED + QR 🌿");
  Serial.println("============================================");

  // Initialize I2C
  Wire.begin(I2C_SDA, I2C_SCL);

  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    Serial.println("❌ OLED initialization failed!");
    while (1) delay(100);
  }
  Serial.println("✅ OLED initialized");

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Algae Box");
  display.println("Connecting WiFi...");
  display.display();

  // Connect WiFi
  connectWiFi();

  // Show QR code initially
  displayQRCode();

  Serial.println("🔄 Starting sensor monitoring...");
}

// ============== MAIN LOOP ==============
void loop() {
  unsigned long now = millis();

  // Send sensor data every SEND_INTERVAL
  if (now - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = now;
    sendSensorData();
  }

  // Switch between QR code and sensor display
  if (now - lastDisplaySwitch >= DISPLAY_SWITCH) {
    lastDisplaySwitch = now;
    showQR = !showQR;

    if (showQR) {
      displayQRCode();
    } else {
      displaySensorData();
    }
  }

  delay(100);
}

// ============== WIFI ==============
void connectWiFi() {
  Serial.print("📡 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected");
    Serial.print("   IP: ");
    Serial.println(WiFi.localIP());

    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("WiFi Connected!");
    display.print("IP: ");
    display.println(WiFi.localIP());
    display.display();
    delay(1500);
  } else {
    Serial.println();
    Serial.println("❌ WiFi failed!");
    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("WiFi Failed!");
    display.println("Check credentials");
    display.display();
  }
}

// ============== SENSOR READING ==============
float readTurbidity() {
  int raw = analogRead(TURBIDITY_PIN);
  return (raw / 4095.0) * 400.0;  // 0-400 NTU
}

float readPH() {
  int raw = analogRead(PH_PIN);
  return 6.0 + (raw / 4095.0) * 3.0;  // pH 6-9
}

float readTemperature() {
  int raw = analogRead(TEMP_PIN);
  return 20.0 + (raw / 4095.0) * 12.0;  // 20-32°C
}

// ============== SEND DATA ==============
void sendSensorData() {
  float turbidity = readTurbidity();
  float ph = readPH();
  float temperature = readTemperature();

  Serial.printf("📊 Sensors: Turb=%.1f NTU, pH=%.2f, Temp=%.1f°C\n",
                turbidity, ph, temperature);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️  WiFi disconnected, reconnecting...");
    connectWiFi();
    return;
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;
  doc["tank_id"] = TANK_ID;
  doc["turbidity"] = turbidity;
  doc["ph"] = ph;
  doc["temperature"] = temperature;

  String jsonString;
  serializeJson(doc, jsonString);

  int httpCode = http.POST(jsonString);

  if (httpCode > 0) {
    Serial.printf("✅ Data sent (HTTP %d)\n", httpCode);
  } else {
    Serial.printf("❌ HTTP error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

// ============== DISPLAY QR CODE ==============
void displayQRCode() {
  display.clearDisplay();

  // Create QR code
  uint8_t qrcodeData[qrcode_getBufferSize(3)];
  qrcode_initText(&qrcode, qrcodeData, 3, ECC_LOW, STREAMLIT_URL);

  // Calculate position to center QR code
  int scale = 2;
  int qrSize = qrcode.size * scale;
  int offsetX = (SCREEN_WIDTH - qrSize) / 2;
  int offsetY = (SCREEN_HEIGHT - qrSize) / 2;

  // Draw QR code
  for (uint8_t y = 0; y < qrcode.size; y++) {
    for (uint8_t x = 0; x < qrcode.size; x++) {
      if (qrcode_getModule(&qrcode, x, y)) {
        display.fillRect(offsetX + x * scale, offsetY + y * scale, scale, scale, SSD1306_WHITE);
      }
    }
  }

  // Add label at bottom
  display.setTextSize(1);
  display.setCursor(20, 56);
  display.print("Scan to monitor");

  display.display();
  Serial.println("📱 QR code displayed");
}

// ============== DISPLAY SENSOR DATA ==============
void displaySensorData() {
  float turbidity = readTurbidity();
  float ph = readPH();
  float temperature = readTemperature();

  display.clearDisplay();

  // Title
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("Tank #");
  display.println(TANK_ID);
  display.drawLine(0, 10, 128, 10, SSD1306_WHITE);

  // Sensor values
  display.setTextSize(1);

  display.setCursor(0, 16);
  display.print("Turbidity: ");
  display.print(turbidity, 0);
  display.println(" NTU");

  display.setCursor(0, 28);
  display.print("pH: ");
  display.println(ph, 2);

  display.setCursor(0, 40);
  display.print("Temp: ");
  display.print(temperature, 1);
  display.println(" C");

  // Status bar
  display.drawLine(0, 52, 128, 52, SSD1306_WHITE);
  display.setCursor(0, 56);
  if (WiFi.status() == WL_CONNECTED) {
    display.print("WiFi OK | Sending...");
  } else {
    display.print("WiFi Disconnected");
  }

  display.display();
}
