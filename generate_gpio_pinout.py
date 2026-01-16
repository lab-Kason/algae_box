"""
Simple GPIO Pinout Diagram for Raspberry Pi 4 Model B
Showing connections for algae box project
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 22)
ax.axis('off')

# Title
ax.text(7, 21, 'Raspberry Pi 4 Model B - GPIO Pinout', 
        fontsize=18, weight='bold', ha='center')
ax.text(7, 20.2, 'Algae Box Project Connections', 
        fontsize=12, ha='center', color='gray')

# Draw GPIO header (2x20 pins)
pin_size = 0.4
start_x = 5
start_y = 18

# Pin data: (physical_pin, left_label, right_label, left_color, right_color)
pins = [
    (1, '3.3V', '5V', 'orange', 'red'),
    (2, 'GPIO2 (SDA)', '5V', 'green', 'red'),
    (3, 'GPIO3 (SCL)', 'GND', 'green', 'black'),
    (4, 'GPIO4 (1-WIRE)', 'GPIO14 (TXD)', 'blue', 'green'),
    (5, 'GND', 'GPIO15 (RXD)', 'black', 'green'),
    (6, 'GPIO17 (RELAY CH1)', 'GPIO18 (RELAY CH2)', 'purple', 'purple'),
    (7, 'GPIO27', 'GND', 'gray', 'black'),
    (8, 'GPIO22', 'GPIO23', 'gray', 'purple'),
    (9, '3.3V', 'GPIO24 (SPI CE0)', 'orange', 'cyan'),
    (10, 'GPIO10 (SPI MOSI)', 'GND', 'cyan', 'black'),
    (11, 'GPIO9 (SPI MISO)', 'GPIO25', 'cyan', 'gray'),
    (12, 'GPIO11 (SPI SCLK)', 'GPIO8 (SPI CE1)', 'cyan', 'gray'),
    (13, 'GND', 'GPIO7', 'black', 'gray'),
    (14, 'GPIO0 (ID_SD)', 'GPIO1 (ID_SC)', 'gray', 'gray'),
    (15, 'GPIO5', 'GND', 'gray', 'black'),
    (16, 'GPIO6', 'GPIO12', 'gray', 'gray'),
    (17, 'GPIO13', 'GND', 'gray', 'black'),
    (18, 'GPIO19 (SPI MOSI)', 'GPIO16', 'cyan', 'gray'),
    (19, 'GPIO26', 'GPIO20 (SPI MISO)', 'gray', 'cyan'),
    (20, 'GND', 'GPIO21 (SPI SCLK)', 'black', 'cyan'),
]

# Draw pins
for i, (pin_num, left_label, right_label, left_color, right_color) in enumerate(pins):
    y_pos = start_y - i * 0.8
    
    # Left pin (odd numbers)
    left_rect = patches.Rectangle((start_x - 0.5, y_pos - pin_size/2), 
                                  pin_size, pin_size, 
                                  facecolor=left_color, edgecolor='black', linewidth=1)
    ax.add_patch(left_rect)
    
    # Pin number and label (left)
    ax.text(start_x - 0.8, y_pos, f'{i*2+1}', fontsize=8, ha='right', va='center', weight='bold')
    ax.text(start_x - 1.2, y_pos, left_label, fontsize=9, ha='right', va='center')
    
    # Right pin (even numbers)
    right_rect = patches.Rectangle((start_x + 0.1, y_pos - pin_size/2), 
                                   pin_size, pin_size, 
                                   facecolor=right_color, edgecolor='black', linewidth=1)
    ax.add_patch(right_rect)
    
    # Pin number and label (right)
    ax.text(start_x + 0.8, y_pos, f'{i*2+2}', fontsize=8, ha='left', va='center', weight='bold')
    ax.text(start_x + 1.2, y_pos, right_label, fontsize=9, ha='left', va='center')

# Add connection legend
legend_y = 2.5
ax.text(7, legend_y + 1.5, 'Project Connections:', fontsize=12, weight='bold', ha='center')

connections = [
    ('GPIO4 (Pin 7)', 'DS18B20 Temperature Sensor', 'blue'),
    ('GPIO17 (Pin 11)', 'Relay Channel 1 (Drain Valve)', 'purple'),
    ('GPIO18 (Pin 12)', 'Relay Channel 2 (Water Pump)', 'purple'),
    ('SPI Bus (19,21,23,24)', 'MCP3008 ADC (Turbidity Sensor)', 'cyan'),
]

for i, (pin, device, color) in enumerate(connections):
    y = legend_y - i * 0.6
    # Color indicator
    circle = patches.Circle((2, y), 0.15, facecolor=color, edgecolor='black')
    ax.add_patch(circle)
    # Connection text
    ax.text(2.5, y, f'{pin} → {device}', fontsize=10, va='center')

# Add color key
key_y = legend_y - 4
ax.text(7, key_y, 'Pin Color Key:', fontsize=11, weight='bold', ha='center')

colors_key = [
    ('Power (5V)', 'red'),
    ('Power (3.3V)', 'orange'),
    ('Ground', 'black'),
    ('SPI Interface', 'cyan'),
    ('GPIO Control', 'purple'),
    ('1-Wire Bus', 'blue'),
    ('I2C', 'green'),
    ('Unused', 'gray'),
]

for i, (label, color) in enumerate(colors_key):
    x = 2 if i < 4 else 9
    y = key_y - 0.6 - (i % 4) * 0.5
    circle = patches.Circle((x, y), 0.12, facecolor=color, edgecolor='black')
    ax.add_patch(circle)
    ax.text(x + 0.4, y, label, fontsize=9, va='center')

plt.tight_layout()
plt.savefig('diagrams/gpio_pinout.png', dpi=300, bbox_inches='tight', facecolor='white')
print("GPIO pinout diagram saved: diagrams/gpio_pinout.png")
