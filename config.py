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
# Pump-based flow manifold system (slot-cut water knife)
SETTLING_TIME = 5  # seconds (fast for demo, use 100-300 for real)
FLUSH_PASSES = 3   # Number of repeated sweep passes per cycle
FLUSH_TIME_PER_PASS = 10  # seconds per pass (fast for demo, use 200-600 for real)
COLLECTION_WAIT_TIME = 3  # seconds - pump OFF, algae settle at drain
DRAIN_OPEN_TIME = 10  # seconds - how long drain valve stays open
COLLECTION_COOLDOWN = 30  # seconds (fast for demo, use 3600 for real)

# Multi-cycle collection for thorough harvesting
COLLECTION_CYCLES = 1  # Number of complete collection cycles per harvest
CYCLE_INTERVAL = 10  # seconds between cycles (optional rest period)
TURBIDITY_REDUCTION_PER_CYCLE = 0.7  # 70% reduction per collection cycle

# Manifold specifications (from CAD design)
MANIFOLD_DIAMETER = 25  # mm - PVC pipe diameter
SLOT_WIDTH = 8  # mm - horizontal slot cut width
SLOT_LENGTH = 185  # mm - slot length (almost full tank width)
MANIFOLD_HEIGHT = 10  # mm - height above bottom
FLOW_RATE = 1.0  # L/min - target pump flow rate (adjustable via PWM)

# Flow physics (with water resistance)
FLOW_VELOCITY_BULK = 0.25  # mm/frame equivalent (~15 mm/s)
BOUNDARY_LAYER_THICKNESS = 3.0  # mm - reduces velocity near bottom
DRAG_REDUCTION_FACTOR = 0.6  # Water viscosity effect

# Valve and pump control
DRAIN_VALVE_PIN = 17  # GPIO pin for drain valve at back wall
PUMP_PIN = 18  # GPIO pin for pump relay (12V DC pump)

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
