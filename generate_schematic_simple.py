"""
Ultra-clean schematic with manual positioning
No overlapping, clear layout
"""

from graphviz import Digraph

print("Generating clean schematic...")

# Create schematic
dot = Digraph(comment='Algae Box Schematic', format='png')
dot.attr(rankdir='LR', splines='line', sep='3', nodesep='2', ranksep='3')
dot.attr(bgcolor='white', dpi='300')
dot.attr('node', shape='box', style='filled', fontname='Arial', fontsize='12', fillcolor='white', color='black', penwidth='2', margin='0.4,0.2')
dot.attr('edge', fontname='Arial', fontsize='11', penwidth='2')

# Title
dot.node('title', 'Algae Box - Raspberry Pi GPIO Wiring Schematic', shape='plaintext', fontsize='16', fontname='Arial Bold')

# Raspberry Pi GPIO - show as pin list
rpi_pins = '''RASPBERRY PI 4B GPIO
━━━━━━━━━━━━━━━━━━━━━
Pin 1:  3.3V Power
Pin 2:  5V Power
Pin 6:  GND
Pin 7:  GPIO4 (1-Wire)
Pin 11: GPIO17 (Relay CH1)
Pin 12: GPIO18 (Relay CH2)
Pin 19: MOSI (SPI)
Pin 21: MISO (SPI)
Pin 23: SCLK (SPI)
Pin 24: CE0 (SPI)'''

dot.node('rpi', rpi_pins, fillcolor='lightgreen', fontname='Courier New', fontsize='11', width='3', height='4')

# DS18B20 Temperature Sensor
dot.node('ds18b20', 'DS18B20\nTemperature Sensor\n\nPin 1: VCC → Pi 3.3V\nPin 2: DATA → Pi GPIO4\nPin 3: GND → Pi GND\n\n+ 4.7kΩ pull-up\n  (DATA to 3.3V)', 
         fillcolor='lightyellow', width='2.5', height='2.5')

# MCP3008 ADC
dot.node('mcp3008', 'MCP3008 ADC\n10-bit 8-channel\n\nCH0 ← Turbidity Sensor\nVDD ← Pi 3.3V\nVREF ← Pi 3.3V\nDGND ← Pi GND\nCS ← Pi CE0\nMOSI ← Pi MOSI\nMISO → Pi MISO\nSCLK ← Pi SCLK', 
         fillcolor='lightblue', width='2.5', height='3')

# Turbidity Sensor
dot.node('turbidity', 'Turbidity Sensor\n\nVCC → Pi 5V\nAOUT → MCP3008 CH0\nGND → Pi GND', 
         fillcolor='palegreen', width='2', height='1.5')

# Relay Module
dot.node('relay', '2-Channel Relay Module\n5V Coil, 12V Switch\n\nVCC ← Pi 5V\nIN1 ← Pi GPIO17\nIN2 ← Pi GPIO18\nGND ← Pi GND\n\nCOM1,COM2 ← 12V Supply\nNO1 → Valve +\nNO2 → Pump +', 
         fillcolor='lightcoral', width='3', height='3')

# Solenoid Valve
dot.node('valve', 'Solenoid Valve\n12V DC\n\n+ ← Relay NO1\n- → GND', 
         fillcolor='pink', width='2', height='1.5')

# Water Pump
dot.node('pump', 'Water Pump\n12V DC\n\n+ ← Relay NO2\n- → GND', 
         fillcolor='lightblue', width='2', height='1.5')

# Power supplies
dot.node('psu5v', '5V Power Supply\n3A\n\nFor Raspberry Pi\nUSB-C', 
         fillcolor='gold', width='2', height='1.5')

dot.node('psu12v', '12V Power Supply\n2A\n\nFor Pump and Valve\nvia Relay', 
         fillcolor='orange', width='2', height='1.5')

# Connections (simplified - just grouping)
dot.edge('title', 'rpi', style='invis')  # Force title at top

dot.edge('rpi', 'ds18b20', label='  Pin 7: GPIO4\n  Pin 1: 3.3V\n  Pin 6: GND  ', color='orange', fontcolor='orange')
dot.edge('rpi', 'mcp3008', label='  SPI Bus\n  Pins 19,21,23,24\n  + 3.3V, GND  ', color='purple', fontcolor='purple')
dot.edge('turbidity', 'mcp3008', label='  Analog Signal  ', color='green', fontcolor='green')
dot.edge('rpi', 'relay', label='  Pin 11: GPIO17\n  Pin 12: GPIO18\n  + 5V, GND  ', color='blue', fontcolor='blue')
dot.edge('relay', 'valve', label='  12V Switched  ', color='brown', fontcolor='brown', penwidth='3')
dot.edge('relay', 'pump', label='  12V Switched  ', color='teal', fontcolor='teal', penwidth='3')
dot.edge('psu5v', 'rpi', label='  5V @ 3A  ', color='red', fontcolor='red', penwidth='4')
dot.edge('psu12v', 'relay', label='  12V @ 2A  ', color='red', fontcolor='red', penwidth='4')

# Important note
dot.node('note', 'CRITICAL:\n• All GND must be connected together\n• MCP3008 VDD and VREF both to 3.3V\n• DS18B20 DATA needs 4.7kΩ pull-up to 3.3V\n• Total power: 5V@3A + 12V@2A', 
         shape='note', style='filled', fillcolor='lightyellow', fontsize='11')

# Save
dot.render('diagrams/wiring_schematic_clean', cleanup=True)
print("Clean schematic saved: diagrams/wiring_schematic_clean.png")

print("\nSchematic shows:")
print("  - Raspberry Pi GPIO with pin numbers")
print("  - All sensor connections clearly labeled")
print("  - Power requirements for each component")
print("  - Signal flow direction with arrows")
print("  - Color-coded wiring (orange=1-Wire, purple=SPI, blue=GPIO, red=Power)")
