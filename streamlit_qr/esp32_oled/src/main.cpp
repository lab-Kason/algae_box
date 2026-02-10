#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// DS18B20 Temperature Sensor
#define ONE_WIRE_BUS 4
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature tempSensor(&oneWire);

// TDS/EC Sensor (simulated with potentiometer) & Resume button
#define TDS_SENSOR_PIN 34
#define RESUME_BTN_PIN 15

// Simulation parameters
float turbidity = 36.0;      // NTU - starts low, matches initial algae
float ph = 7.0;              // Neutral pH
float temperature = 25.0;    // From DS18B20
float algaePopulation = 10.0; // Arbitrary units

// Growth factors
float lightIntensity = 1.0;  // 0-1 scale (day/night cycle)
float nutrientLevel = 100.0; // Percentage - controlled by potentiometer

// Time tracking
unsigned long simTime = 0;   // Simulated hours
unsigned long lastUpdate = 0;
const unsigned long UPDATE_INTERVAL = 100; // 100ms = 1 simulated hour (FAST MODE)

// Harvest state machine
enum HarvestState {
  GROWING,       // Pump ON, algae growing
  SETTLING,      // Pump OFF, waiting for algae to sink (60 min)
  HARVEST_READY, // Paused, waiting for user to press button
  HARVESTING,    // Valve open, draining (30 sec)
  RESTART        // Refilling, restarting cycle
};

HarvestState harvestState = GROWING;
unsigned long settlingStartTime = 0;
unsigned long harvestStartTime = 0;
const unsigned long SETTLING_DURATION = 3600; // 60 min in simulated hours (36 sec in fast mode)
const unsigned long HARVEST_DURATION = 300;   // 5 min drain time (30 sec in fast mode)

// Harvest state
const float HARVEST_TURBIDITY = 350.0;

// Day/night cycle (24 hours)
bool isDaytime() {
  int hour = simTime % 24;
  return (hour >= 6 && hour < 20); // 6 AM to 8 PM
}

float getLightIntensity() {
  int hour = simTime % 24;
  if (hour >= 6 && hour < 12) {
    return 0.3 + (hour - 6) * 0.1;
  } else if (hour >= 12 && hour < 15) {
    return 1.0;
  } else if (hour >= 15 && hour < 20) {
    return 1.0 - (hour - 15) * 0.15;
  } else {
    return 0.05;
  }
}

void readSensors() {
  // Read DS18B20 temperature
  tempSensor.requestTemperatures();
  float tempReading = tempSensor.getTempCByIndex(0);
  if (tempReading != DEVICE_DISCONNECTED_C && tempReading > -50) {
    temperature = tempReading;
  }
  
  // Read TDS/EC sensor (0-2000 ppm)
  // In real life: TDS sensor measures dissolved solids = nutrient concentration
  int tdsRaw = analogRead(TDS_SENSOR_PIN);
  float tdsPPM = map(tdsRaw, 0, 4095, 0, 2000); // 0-2000 ppm range
  
  // Convert TDS ppm to nutrient percentage (500 ppm = 100% ideal)
  float newNutrient = (tdsPPM / 500.0) * 100.0;
  newNutrient = constrain(newNutrient, 0, 200); // Allow over-fertilization
  
  // Only add nutrients if TDS increases (simulates adding fertilizer)
  if (newNutrient > nutrientLevel + 5) {
    nutrientLevel = newNutrient;
    Serial.print(">>> NUTRIENTS ADDED! TDS: ");
    Serial.print(tdsPPM, 0);
    Serial.println(" ppm <<<");
  }
}

void simulateAlgaeGrowth() {
  // Only grow if in GROWING state
  if (harvestState != GROWING) return;
  
  lightIntensity = getLightIntensity();
  
  // Algae growth model
  float optimalTemp = 25.0;
  float tempFactor = 1.0 - abs(temperature - optimalTemp) / 20.0;
  tempFactor = max(0.1f, tempFactor);
  
  float growthRate = 0.15 * lightIntensity * tempFactor * (nutrientLevel / 100.0);
  
  // Logistic growth (carrying capacity)
  float carryingCapacity = 500.0;
  float populationFactor = 1.0 - (algaePopulation / carryingCapacity);
  populationFactor = max(0.0f, populationFactor);
  
  // Update algae population
  algaePopulation += algaePopulation * growthRate * populationFactor;
  algaePopulation = constrain(algaePopulation, 1.0, carryingCapacity);
  
  // Consume nutrients (slower consumption)
  nutrientLevel -= algaePopulation * 0.0005;
  nutrientLevel = max(5.0f, nutrientLevel);
  
  // Turbidity increases with algae population (monotonically increasing)
  float newTurbidity = 20.0 + (algaePopulation / carryingCapacity) * 800.0;
  newTurbidity += random(0, 5); // Only positive noise
  
  // RULE: Turbidity can only increase (or stay same), never decrease
  if (newTurbidity > turbidity) {
    turbidity = newTurbidity;
  }
  turbidity = constrain(turbidity, 0, 1000);
  
  // pH changes based on photosynthesis
  if (isDaytime()) {
    ph += 0.02 * lightIntensity * (algaePopulation / 100.0);
  } else {
    ph -= 0.03 * (algaePopulation / 100.0);
  }
  ph = constrain(ph, 6.0, 9.5);
  
  // Check harvest threshold
  if (turbidity >= HARVEST_TURBIDITY && harvestState == GROWING) {
    harvestState = SETTLING;
    settlingStartTime = simTime;
    Serial.println("");
    Serial.println("!!! HARVEST THRESHOLD REACHED !!!");
    Serial.println(">>> PUMP OFF - Starting settling phase <<<");
    Serial.println("Algae will sink for 60 simulated minutes...");
    Serial.println("");
  }
}

void displayHarvestScreen() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  
  if (harvestState == SETTLING) {
    unsigned long elapsed = simTime - settlingStartTime;
    unsigned long remaining = SETTLING_DURATION - elapsed;
    int minutes = remaining / 60;
    int seconds = remaining % 60;
    
    display.setTextSize(1);
    display.println("== SETTLING ==");
    display.println("Pump: OFF");
    display.println("Algae sinking...");
    display.println("");
    display.print("Time left: ");
    display.print(minutes);
    display.print(":");
    if (seconds < 10) display.print("0");
    display.println(seconds);
    display.println("");
    display.print("Turb: ");
    display.print(turbidity, 0);
    display.println(" NTU");
    
  } else if (harvestState == HARVEST_READY) {
    display.setTextSize(2);
    display.setCursor(10, 5);
    display.println("HARVEST");
    display.setCursor(20, 25);
    display.println("READY!");
    
    display.setTextSize(1);
    display.setCursor(0, 48);
    display.println("Place bucket below");
    display.println("Press GREEN button");
    
  } else if (harvestState == HARVESTING) {
    unsigned long elapsed = simTime - harvestStartTime;
    unsigned long remaining = HARVEST_DURATION - elapsed;
    int seconds = remaining / 60;
    
    display.setTextSize(1);
    display.println("== HARVESTING ==");
    display.println("Valve: OPEN");
    display.println("Draining algae...");
    display.println("");
    display.setTextSize(2);
    display.print("  ");
    display.print(seconds);
    display.println(" sec");
    display.setTextSize(1);
    display.println("");
    display.println("Collecting...");
    
  } else if (harvestState == RESTART) {
    display.setTextSize(1);
    display.println("== RESTARTING ==");
    display.println("");
    display.println("Refilling water...");
    display.println("Resetting system...");
    display.println("");
    display.println("Pump will restart");
    display.println("in 5 seconds...");
  }
  
  display.print("Turb: ");
  display.print(turbidity, 0);
  display.println(" NTU");
  display.println("Press btn to resume");
  display.display();
}

void displayNormalScreen() {
  int day = simTime / 24;
  int hour = simTime % 24;
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);
  
  display.print("Day ");
  display.print(day);
  display.print(" ");
  display.print(hour);
  display.print(":00 ");
  display.println(isDaytime() ? "[DAY]" : "[NIGHT]");
  
  display.println("----------------");
  
  display.print("Algae: ");
  display.print(algaePopulation, 0);
  display.println(" units");
  
  display.print("Turb: ");
  display.print(turbidity, 0);
  display.print("/");
  display.print(HARVEST_TURBIDITY, 0);
  display.println(" NTU");
  
  display.print("pH: ");
  display.print(ph, 2);
  display.print(" T:");
  display.print(temperature, 1);
  display.println("C");
  
  display.print("Nutrients: ");
  display.print(nutrientLevel, 0);
  display.println("%");
  
  // Progress bar for harvest
  int progress = (turbidity / HARVEST_TURBIDITY) * 100;
  progress = constrain(progress, 0, 100);
  display.print("Harvest: [");
  int barWidth = progress / 10;
  for (int i = 0; i < 10; i++) {
    display.print(i < barWidth ? "=" : " ");
  }
  display.print("] ");
  display.print(progress);
  display.println("%");
  
  display.display();
}

void setup() {
  Serial.begin(9600);
  while(!Serial) { delay(10); }
  delay(500);
  
  Serial.println("");
  Serial.println("=== ALGAE GROWTH SIMULATOR v3 ===");
  Serial.println("Features:");
  Serial.println("  - DS18B20 temperature sensor");
  Serial.println("  - TDS/EC nutrient sensor (0-2000 ppm)");
  Serial.println("  - Auto settling at 350 NTU");
  Serial.println("  - Semi-auto harvest (press button when ready)");
  Serial.println("  - Gravity settling cone design");
  Serial.println("");
  
  // Initialize resume button
  pinMode(RESUME_BTN_PIN, INPUT_PULLUP);
  
  // Initialize DS18B20
  tempSensor.begin();
  Serial.print("Found ");
  Serial.print(tempSensor.getDeviceCount());
  Serial.println(" DS18B20 sensor(s)");
  
  Wire.begin(21, 22);
  
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED failed!");
    while(true);
  }
  
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Algae Simulator v3");
  display.println("Semi-Auto Harvest");
  display.println("");
  display.println("Settling Cone");
  display.println("Design");
  display.display();
  delay(2000);
  
  randomSeed(analogRead(0));
}

void loop() {
  unsigned long currentTime = millis();
  
  // Always read sensors
  readSensors();
  
  // State machine for harvest process
  switch (harvestState) {
    case GROWING:
      // Normal growth mode - check button does nothing
      break;
      
    case SETTLING:
      // Check if settling time is complete
      if (simTime - settlingStartTime >= SETTLING_DURATION) {
        harvestState = HARVEST_READY;
        Serial.println("");
        Serial.println("!!! SETTLING COMPLETE !!!");
        Serial.println(">>> Algae concentrated at bottom <<<");
        Serial.println("Place collection bucket and press GREEN button to harvest");
        Serial.println("");
      }
      break;
      
    case HARVEST_READY:
      // Wait for user to press harvest button
      if (digitalRead(RESUME_BTN_PIN) == LOW) {
        harvestState = HARVESTING;
        harvestStartTime = simTime;
        Serial.println(">>> HARVEST BUTTON PRESSED <<<");
        Serial.println("Opening drain valve...");
        delay(300); // Debounce
      }
      break;
      
    case HARVESTING:
      // Drain for specified duration
      if (simTime - harvestStartTime >= HARVEST_DURATION) {
        harvestState = RESTART;
        Serial.println(">>> HARVEST COMPLETE <<<");
        Serial.println("Closing valve, restarting system...");
      }
      break;
      
    case RESTART:
      // Reset for next cycle
      turbidity = 36.0;
      algaePopulation = 10.0;
      ph = 7.0;
      nutrientLevel = 100.0;
      harvestState = GROWING;
      Serial.println("");
      Serial.println("=== NEW CYCLE STARTED ===");
      Serial.println("Pump ON - Growing phase");
      Serial.println("");
      break;
  }
  
  // Display appropriate screen
  if (harvestState != GROWING) {
    displayHarvestScreen();
    delay(500);
    return;
  }
  
  // Normal simulation update (GROWING state only)
  // Normal simulation update
  if (currentTime - lastUpdate >= UPDATE_INTERVAL) {
    lastUpdate = currentTime;
    simTime++;
    
    simulateAlgaeGrowth();
    
    // Serial output
    int day = simTime / 24;
    int hour = simTime % 24;
    
    Serial.print("Day ");
    Serial.print(day);
    Serial.print(" ");
    Serial.print(hour < 10 ? "0" : "");
    Serial.print(hour);
    Serial.print(":00 | ");
    Serial.print(isDaytime() ? "DAY  " : "NIGHT");
    Serial.print(" | Algae: ");
    Serial.print(algaePopulation, 1);
    Serial.print(" | Turb: ");
    Serial.print(turbidity, 0);
    Serial.print("/350");
    Serial.print(" | pH: ");
    Serial.print(ph, 2);
    Serial.print(" | Temp: ");
    Serial.print(temperature, 1);
    Serial.print("C | Nutr: ");
    Serial.print(nutrientLevel, 0);
    Serial.println("%");
    
    displayNormalScreen();
  }
}

