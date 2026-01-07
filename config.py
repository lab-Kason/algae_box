"""
Configuration file for Algae Box automation system
"""

# ==================== SIMULATION MODE ====================
SIMULATION_MODE = True  # Set to False when real sensors connected

# ==================== SENSOR THRESHOLDS ====================
# Turbidity settings
TURBIDITY_HARVEST_THRESHOLD = 35  # NTU - trigger collection above this
TURBIDITY_MIN = 0                  # NTU
TURBIDITY_MAX = 200               # NTU

# pH settings
PH_MIN_SAFE = 6.5
PH_MAX_SAFE = 8.5
PH_OPTIMAL = 7.5

# Temperature settings (Celsius)
TEMP_MIN_SAFE = 20
TEMP_MAX_SAFE = 30
TEMP_OPTIMAL = 25

# ==================== COLLECTION SYSTEM ====================
# U-bottom passive collection (gravity-based, no moving parts)
SETTLING_TIME = 5  # seconds (fast for demo, use 300-600 for real)
DRAIN_OPEN_TIME = 10  # seconds - how long drain valve stays open
COLLECTION_COOLDOWN = 30  # seconds (fast for demo, use 3600 for real)

# Multi-cycle collection for thorough harvesting
COLLECTION_CYCLES = 3  # Number of settle-drain cycles per harvest
CYCLE_INTERVAL = 10  # seconds between cycles (lets disturbed algae re-settle)
TURBIDITY_REDUCTION_PER_CYCLE = 0.6  # 60% reduction per collection cycle

# Tank geometry (U-bottom with longitudinal slope)
U_DEPTH = 80  # mm - depth from sides to center (parabolic curve)
LONGITUDINAL_SLOPE_ANGLE = 12  # degrees - front high to back low

# Valve control
DRAIN_VALVE_PIN = 17  # GPIO pin for drain valve at back-center (lowest point)

# ==================== SIMULATION PARAMETERS ====================
# How simulated sensors behave
SIM_ALGAE_GROWTH_RATE = 5.0  # NTU increase per minute (fast for demo)
SIM_TURBIDITY_NOISE = 2.0    # Random fluctuation in readings
SIM_PH_DRIFT = 0.01          # pH change per minute
SIM_TEMP_VARIATION = 0.5     # Temperature fluctuation

# ==================== MONITORING ====================
SENSOR_READ_INTERVAL = 10    # seconds - how often to read sensors
LOG_FILE = "data/algae_log.csv"
ALERT_EMAIL = None           # Set email for alerts (future feature)

# ==================== GPIO PINS (for real hardware) ====================
# Will be used when SIMULATION_MODE = False
TURBIDITY_ADC_CHANNEL = 0    # MCP3008 channel
PH_ADC_CHANNEL = 1
TEMP_SENSOR_PIN = 4          # DS18B20 1-wire pin
