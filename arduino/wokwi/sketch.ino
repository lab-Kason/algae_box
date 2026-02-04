/*
 * Wokwi Simulation - Algae Box ESP32-S3
 * Simulated sensors via potentiometers (no real I2C devices in Wokwi)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// WiFi (Wokwi default)
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// API endpoint (replace with your backend URL)
const char* API_URL = "https://labKason.pythonanywhere.com/api/sensors/reading";
const int TANK_ID = 1;

// Analog pins (simulated sensors)
const int TURBIDITY_PIN = 4;   // Potentiometer 1
const int PH_PIN = 5;          // Potentiometer 2
const int TEMP_PIN = 6;        // Potentiometer 3

const unsigned long READ_INTERVAL = 10000;
unsigned long lastReadTime = 0;
int readingCount = 0;

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("============================================================");
  Serial.println("  🌊 ALGAE BOX - WOKWI SIMULATION 🌊");
  Serial.println("============================================================");

  connectWiFi();

  Serial.println("🔄 Starting sensor monitoring...");
  Serial.println("   Reading every 10 seconds");
}

void loop() {
  unsigned long now = millis();
  if (now - lastReadTime >= READ_INTERVAL) {
    lastReadTime = now;
    readingCount++;

    float turbidity = readTurbidity();
    float ph = readPH();
    float temperature = readTemperature();

    Serial.printf("[Reading #%d]\n", readingCount);
    Serial.printf("  Turbidity: %.2f NTU\n", turbidity);
    Serial.printf("  pH: %.2f\n", ph);
    Serial.printf("  Temp: %.2f°C\n", temperature);

    sendToCloud(turbidity, ph, temperature);

    Serial.println();
  }

  delay(100);
}

void connectWiFi() {
  Serial.print("📡 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("✅ WiFi connected");
    Serial.print("   IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("❌ WiFi connection failed!");
  }
}

float readTurbidity() {
  int raw = analogRead(TURBIDITY_PIN);
  // Map 0-4095 to 0-400 NTU
  return (raw / 4095.0) * 400.0;
}

float readPH() {
  int raw = analogRead(PH_PIN);
  // Map 0-4095 to pH 6.0 - 9.0
  return 6.0 + (raw / 4095.0) * 3.0;
}

float readTemperature() {
  int raw = analogRead(TEMP_PIN);
  // Map 0-4095 to 20-32°C
  return 20.0 + (raw / 4095.0) * 12.0;
}

void sendToCloud(float turbidity, float ph, float temperature) {
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
    String response = http.getString();
    Serial.printf("✅ Sent to cloud (HTTP %d)\n", httpCode);
    Serial.printf("   Response: %s\n", response.c_str());
  } else {
    Serial.printf("❌ HTTP error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}
