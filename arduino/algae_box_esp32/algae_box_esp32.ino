/*
 * Algae Box - ESP32-S3 Main Controller
 * Cloud-connected sensor system for Arduino
 * 
 * Hardware: ESP32-S3-DevKitC-1 (compatible with ESP32 DevKit V1)
 * Sensors: I2C Turbidity, I2C pH, 1-Wire Temperature
 * Cloud: PythonAnywhere/Self-hosted backend
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// ==================== CONFIGURATION ====================
// WiFi credentials
const char* WIFI_SSID = "YOUR_WIFI_NAME";        // 改成你的WiFi名称
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"; // 改成你的WiFi密码

// API endpoint (CHANGE THIS when backend is ready)
const char* API_URL = "https://labKason.pythonanywhere.com/api/sensors/reading";
const int TANK_ID = 1;  // Your tank ID

// Sensor pins (ESP32-S3 compatible)
#define I2C_SDA 8   // ESP32-S3 default SDA (or use 21 for compatibility)
#define I2C_SCL 9   // ESP32-S3 default SCL (or use 22 for compatibility)
#define TEMP_PIN 4  // Any GPIO for 1-Wire
#define PUMP_PIN 17 // Relay control
#define VALVE_PIN 16 // Relay control

// I2C addresses
#define TURBIDITY_ADDR 0x30
#define PH_ADDR 0x63

// Reading interval
const unsigned long READ_INTERVAL = 10000; // 10 seconds

// Simulation mode
bool SIMULATION_MODE = true; // Set false when real sensors connected

// ==================== SENSOR OBJECTS ====================
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

// ==================== GLOBAL VARIABLES ====================
unsigned long lastReadTime = 0;
int readingCount = 0;

// Simulation variables
float simTurbidity = 90.0;
float simPH = 6.8;
float simTemp = 25.0;

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("============================================================");
  Serial.println("  🌊 ALGAE BOX - ESP32-S3 SENSOR SYSTEM 🌊");
  Serial.println("============================================================");
  Serial.println();
  
  // Initialize GPIO
  pinMode(PUMP_PIN, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);
  digitalWrite(VALVE_PIN, LOW);
  
  // Initialize I2C
  Wire.begin(I2C_SDA, I2C_SCL);
  Serial.println("✅ I2C initialized");
  
  // Initialize temperature sensor
  tempSensor.begin();
  Serial.println("✅ DS18B20 initialized");
  
  // Connect to WiFi
  connectWiFi();
  
  // Check sensors
  if (SIMULATION_MODE) {
    Serial.println("🔬 Running in SIMULATION mode");
  } else {
    checkSensors();
  }
  
  Serial.println();
  Serial.println("🔄 Starting sensor monitoring...");
  Serial.println("   Reading every 10 seconds");
  Serial.println();
}

// ==================== MAIN LOOP ====================
void loop() {
  unsigned long currentTime = millis();
  
  // Read sensors at interval
  if (currentTime - lastReadTime >= READ_INTERVAL) {
    lastReadTime = currentTime;
    readingCount++;
    
    // Read sensor values
    float turbidity = readTurbidity();
    float ph = readPH();
    float temperature = readTemperature();
    
    // Print to serial
    Serial.printf("[Reading #%d]\n", readingCount);
    Serial.printf("  Turbidity: %.2f NTU\n", turbidity);
    Serial.printf("  pH: %.2f\n", ph);
    Serial.printf("  Temp: %.2f°C\n", temperature);
    
    // Send to cloud
    sendToCloud(turbidity, ph, temperature);
    
    Serial.println();
  }
  
  delay(100);
}

// ==================== WiFi CONNECTION ====================
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

// ==================== SENSOR READING ====================
float readTurbidity() {
  if (SIMULATION_MODE) {
    // Simulate algae growth
    simTurbidity += random(-20, 50) / 10.0;
    if (simTurbidity < 0) simTurbidity = 0;
    if (simTurbidity > 400) simTurbidity = 90; // Reset after harvest
    return simTurbidity;
  }
  
  // Real sensor: DFRobot SEN0554
  Wire.beginTransmission(TURBIDITY_ADDR);
  Wire.write(0x00); // Register address
  if (Wire.endTransmission() != 0) {
    Serial.println("⚠️  Turbidity sensor not responding");
    return -1;
  }
  
  Wire.requestFrom(TURBIDITY_ADDR, 2);
  if (Wire.available() == 2) {
    uint8_t highByte = Wire.read();
    uint8_t lowByte = Wire.read();
    uint16_t value = (highByte << 8) | lowByte;
    return value / 10.0; // Convert to NTU
  }
  
  return -1;
}

float readPH() {
  if (SIMULATION_MODE) {
    // Simulate pH drift
    simPH += random(-10, 10) / 100.0;
    if (simPH < 6.0) simPH = 6.0;
    if (simPH > 8.0) simPH = 8.0;
    return simPH;
  }
  
  // Real sensor: Atlas Scientific EZO-pH
  Wire.beginTransmission(PH_ADDR);
  Wire.write('R'); // Read command
  if (Wire.endTransmission() != 0) {
    Serial.println("⚠️  pH sensor not responding");
    return -1;
  }
  
  delay(1000); // Wait for reading
  
  Wire.requestFrom(PH_ADDR, 31);
  if (Wire.available() > 0) {
    byte responseCode = Wire.read();
    
    if (responseCode == 1) { // Success
      String response = "";
      while (Wire.available()) {
        char c = Wire.read();
        if (c != 0) response += c;
      }
      return response.toFloat();
    }
  }
  
  return -1;
}

float readTemperature() {
  if (SIMULATION_MODE) {
    // Simulate temperature variation
    simTemp += random(-5, 5) / 10.0;
    if (simTemp < 20) simTemp = 20;
    if (simTemp > 30) simTemp = 30;
    return simTemp;
  }
  
  // Real sensor: DS18B20
  tempSensor.requestTemperatures();
  float temp = tempSensor.getTempCByIndex(0);
  
  if (temp == DEVICE_DISCONNECTED_C) {
    Serial.println("⚠️  Temperature sensor not responding");
    return -1;
  }
  
  return temp;
}

// ==================== CLOUD COMMUNICATION ====================
void sendToCloud(float turbidity, float ph, float temperature) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️  WiFi disconnected, reconnecting...");
    connectWiFi();
    return;
  }
  
  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["tank_id"] = TANK_ID;
  doc["turbidity"] = turbidity;
  doc["ph"] = ph;
  doc["temperature"] = temperature;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send POST request
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

// ==================== SENSOR CHECK ====================
void checkSensors() {
  Serial.println("🔍 Checking sensors...");
  
  // Check turbidity
  Wire.beginTransmission(TURBIDITY_ADDR);
  if (Wire.endTransmission() == 0) {
    Serial.println("✅ Turbidity sensor found at 0x30");
  } else {
    Serial.println("⚠️  Turbidity sensor not found");
  }
  
  // Check pH
  Wire.beginTransmission(PH_ADDR);
  if (Wire.endTransmission() == 0) {
    Serial.println("✅ pH sensor found at 0x63");
  } else {
    Serial.println("⚠️  pH sensor not found");
  }
  
  // Check temperature
  tempSensor.requestTemperatures();
  if (tempSensor.getTempCByIndex(0) != DEVICE_DISCONNECTED_C) {
    Serial.println("✅ Temperature sensor found");
  } else {
    Serial.println("⚠️  Temperature sensor not found");
  }
}

// ==================== PUMP CONTROL ====================
void pumpOn() {
  digitalWrite(PUMP_PIN, HIGH);
  Serial.println("💧 Pump ON");
}

void pumpOff() {
  digitalWrite(PUMP_PIN, LOW);
  Serial.println("💧 Pump OFF");
}

void valveOpen() {
  digitalWrite(VALVE_PIN, HIGH);
  Serial.println("🚰 Valve OPEN");
}

void valveClose() {
  digitalWrite(VALVE_PIN, LOW);
  Serial.println("🚰 Valve CLOSED");
}
