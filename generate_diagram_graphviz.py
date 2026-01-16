"""
Algae Box Wiring Diagram using Graphviz
Cleaner layout with strategic component positioning
"""

from graphviz import Digraph

print("Generating Algae Box Wiring Diagram (Circuit Style)...")

# Create directed graph with cleaner styling
dot = Digraph(comment='Algae Box System Wiring', format='png')
dot.attr(rankdir='TB', splines='line', nodesep='2.0', ranksep='1.5')
dot.attr(bgcolor='white', dpi='300')
dot.attr('node', shape='box', style='filled,rounded', fontname='Arial', fontsize='13', fillcolor='white', color='black', penwidth='2', margin='0.3')
dot.attr('edge', fontname='Arial', fontsize='11', penwidth='2.5')

# Title
dot.node('title', 'Algae Box - Raspberry Pi Wiring Schematic', 
         shape='plaintext', fontsize='20', fontname='Arial Bold')

# Use subgraphs to control layout
with dot.subgraph(name='cluster_power') as c:
    c.attr(label='Power Supplies', fontsize='14', style='dashed', color='gray')
    c.node('psu5v', '5V Power Supply\n3A\nfor Raspberry Pi', fillcolor='gold', penwidth='3')
    c.node('psu12v', '12V Power Supply\n2A\nfor Pump & Valve', fillcolor='orange', penwidth='3')

with dot.subgraph(name='cluster_sensors') as c:
    c.attr(label='Sensors', fontsize='14', style='dashed', color='gray')
    c.node('temp', 'DS18B20\nTemperature Sensor\n\nVCC  DATA  GND', fillcolor='lightyellow')
    c.node('turb', 'Turbidity Sensor\nAnalog Output\n\nVCC  AOUT  GND', fillcolor='palegreen')
    c.node('r1', '4.7k Ohm\nPull-up Resistor', fillcolor='wheat', width='2')

# Raspberry Pi - center with actual GPIO pinout
rpi_gpio = '''Raspberry Pi 4B - GPIO Header
========================================
Pin 1: 3.3V          Pin 2: 5V
Pin 3: SDA           Pin 4: 5V
Pin 5: SCL           Pin 6: GND
Pin 7: GPIO4 [TEMP]  Pin 8: TX
Pin 9: GND           Pin 10: RX
Pin 11: GPIO17 [RLY] Pin 12: GPIO18 [RLY]
...
Pin 19: MOSI [SPI]   Pin 20: GND
Pin 21: MISO [SPI]   Pin 22: GPIO25
Pin 23: SCLK [SPI]   Pin 24: CE0 [SPI]
Pin 25: GND          Pin 26: CE1
...
[TEMP] = Temperature Sensor (1-Wire)
[RLY] = Relay Control Signals
[SPI] = MCP3008 ADC Connection'''

dot.node('rpi', rpi_gpio, 
         fillcolor='lightgreen', penwidth='3', width='5', fontname='Courier New', fontsize='10')

# MCP3008 ADC
dot.node('adc', 'MCP3008 ADC\n8-Channel 10-bit\n\nCH0 CH1-7\nVDD VREF DGND\nCE MOSI MISO SCLK', 
         fillcolor='lightblue', width='2.5')

with dot.subgraph(name='cluster_actuators') as c:
    c.attr(label='Control & Actuators', fontsize='14', style='dashed', color='gray')
    c.node('relay', '2-Channel Relay\n5V Coil / 12V Switch\n\nIN1  IN2  VCC  GND\nNO1  COM1  NO2  COM2', 
           fillcolor='lightcoral', width='2.8')
    c.node('valve', 'Solenoid Valve\n12V DC', fillcolor='pink', width='1.8')
    c.node('pump', 'Water Pump\n12V DC', fillcolor='lightblue', width='1.8')

# Connections - grouped by function
# Power connections
dot.edge('psu5v', 'rpi', label='  5V + GND  ', color='red', fontcolor='red', penwidth='4')

# Temperature sensor
dot.edge('rpi', 'temp', label='  GPIO4 (1-Wire)\n  3.3V, GND  ', color='orange', fontcolor='orange')
dot.edge('rpi', 'r1', label='  3.3V  ', color='red', fontcolor='red', style='dashed')
dot.edge('r1', 'temp', label='  Pull-up to DATA  ', color='orange', fontcolor='orange', style='dashed')

# SPI to ADC
dot.edge('rpi', 'adc', label='  SPI Bus:\n  CE0, MOSI, MISO, SCLK\n  3.3V, GND  ', color='purple', fontcolor='purple')

# Turbidity to ADC
dot.edge('turb', 'adc', label='  Analog to CH0  ', color='green', fontcolor='green')
dot.edge('rpi', 'turb', label='  5V, GND  ', color='red', fontcolor='red', style='dashed')

# Relay control
dot.edge('rpi', 'relay', label='  GPIO17 -> IN1\n  GPIO18 -> IN2\n  5V, GND  ', color='blue', fontcolor='blue')

# High power - relay to devices
dot.edge('psu12v', 'relay', label='  12V -> COM1, COM2  ', color='red', fontcolor='red', penwidth='4')
dot.edge('relay', 'valve', label='  NO1 -> Valve (+)\n  GND to Valve (-)  ', color='brown', fontcolor='brown', penwidth='3')
dot.edge('relay', 'pump', label='  NO2 -> Pump (+)\n  GND to Pump (-)  ', color='teal', fontcolor='teal', penwidth='3')

# Important notes
dot.node('note', 'IMPORTANT NOTES:\n• All GND pins must be connected together (common ground)\n• MCP3008 VDD and VREF both connect to 3.3V from Pi\n• Relay coil uses 5V, but switches 12V loads\n• Total power: 5V @ 3A + 12V @ 2A', 
         shape='note', style='filled', fillcolor='lightyellow', fontsize='12', fontname='Arial', margin='0.4')

# Render and save
output_path = 'diagrams/wiring_diagram'
dot.render(output_path, cleanup=True)
print(f"Clean diagram saved: {output_path}.png")

print("\\nPin Connections Summary:")
print("="*60)
print("SENSORS:")
print("  - Turbidity -> MCP3008 CH0 -> Pi SPI (CE0, MOSI, MISO, SCLK)")
print("  - Temperature DS18B20 -> Pi GPIO4 (with 4.7kohm pull-up)")
print("")
print("ACTUATORS:")
print("  - Drain Valve -> Relay CH1 -> Pi GPIO17")
print("  - Water Pump -> Relay CH2 -> Pi GPIO18")
print("")
print("POWER:")
print("  - Raspberry Pi: 5V 3A (USB-C)")
print("  - MCP3008 ADC: 3.3V from Pi")
print("  - Relay Module: 5V from Pi")
print("  - Pump + Valve: 12V 2A external supply")
print("")
print("Ready for hardware assembly!")
print("   Open diagrams/wiring_diagram.png in VS Code to view")
