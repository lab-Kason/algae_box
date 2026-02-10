"""
FreeCAD Algae Settling Tank Model
Toilet-inspired cone design for gravity-based algae harvesting

To use:
1. Open FreeCAD
2. Open this file: File -> Open -> algae_settling_tank.py
3. Or paste into FreeCAD Python console
"""

import FreeCAD as App
import Part
import Sketcher

# Create document
doc = App.newDocument("AlgaeSettlingTank")

# Parameters (all in mm)
TANK_HEIGHT = 400  # 40cm tall
TANK_DIAMETER = 300  # 30cm diameter
CONE_HEIGHT = 150  # 15cm cone at bottom
CONE_OUTLET = 25  # 25mm (1 inch) drain
WALL_THICKNESS = 3  # 3mm walls
OVERFLOW_HEIGHT = 350  # Overflow at 35cm

# ==================== MAIN TANK CYLINDER ====================
cylinder_outer = Part.makeCylinder(
    TANK_DIAMETER/2, 
    TANK_HEIGHT - CONE_HEIGHT,
    App.Vector(0, 0, CONE_HEIGHT),
    App.Vector(0, 0, 1)
)

cylinder_inner = Part.makeCylinder(
    TANK_DIAMETER/2 - WALL_THICKNESS,
    TANK_HEIGHT - CONE_HEIGHT + 10,
    App.Vector(0, 0, CONE_HEIGHT),
    App.Vector(0, 0, 1)
)

tank_cylinder = cylinder_outer.cut(cylinder_inner)

# ==================== SETTLING CONE (BOTTOM) ====================
# Outer cone
cone_outer = Part.makeCone(
    CONE_OUTLET/2,  # bottom radius (drain)
    TANK_DIAMETER/2,  # top radius (matches cylinder)
    CONE_HEIGHT,
    App.Vector(0, 0, 0),
    App.Vector(0, 0, 1)
)

# Inner cone (for hollow)
cone_inner = Part.makeCone(
    CONE_OUTLET/2 + WALL_THICKNESS,
    TANK_DIAMETER/2 - WALL_THICKNESS,
    CONE_HEIGHT - 5,
    App.Vector(0, 0, 5),
    App.Vector(0, 0, 1)
)

tank_cone = cone_outer.cut(cone_inner)

# ==================== DRAIN PIPE ====================
drain_pipe = Part.makeCylinder(
    CONE_OUTLET/2,
    30,  # 3cm extension
    App.Vector(0, 0, -30),
    App.Vector(0, 0, 1)
)

# ==================== BOTTOM CAP ====================
bottom_cap = Part.makeCylinder(
    CONE_OUTLET/2 + WALL_THICKNESS,
    5,
    App.Vector(0, 0, -5),
    App.Vector(0, 0, 1)
)

# ==================== OVERFLOW PIPE ====================
overflow_pipe_outer = Part.makeCylinder(
    15,  # 30mm diameter
    40,  # extends 4cm
    App.Vector(TANK_DIAMETER/2 - 20, 0, OVERFLOW_HEIGHT),
    App.Vector(1, 0, 0)
)

overflow_pipe_inner = Part.makeCylinder(
    12,
    50,
    App.Vector(TANK_DIAMETER/2 - 25, 0, OVERFLOW_HEIGHT),
    App.Vector(1, 0, 0)
)

overflow_pipe = overflow_pipe_outer.cut(overflow_pipe_inner)

# ==================== COMBINE ALL PARTS ====================
tank = tank_cylinder.fuse(tank_cone)
tank = tank.fuse(drain_pipe)
tank = tank.fuse(bottom_cap)
tank = tank.fuse(overflow_pipe)

# ==================== CREATE PART OBJECTS ====================
# Main tank
tank_obj = doc.addObject("Part::Feature", "SettlingTank")
tank_obj.Shape = tank
tank_obj.ViewObject.ShapeColor = (0.8, 0.9, 1.0, 0.3)  # Light blue, transparent

# ==================== ADD ANNOTATIONS ====================
# Water level indicator
water_level = Part.makeCylinder(
    TANK_DIAMETER/2 - WALL_THICKNESS - 2,
    1,
    App.Vector(0, 0, OVERFLOW_HEIGHT - 20),
    App.Vector(0, 0, 1)
)
water_obj = doc.addObject("Part::Feature", "WaterLevel")
water_obj.Shape = water_level
water_obj.ViewObject.ShapeColor = (0.0, 0.5, 1.0, 0.5)  # Blue water

# Algae settlement zone
algae_zone = Part.makeCone(
    CONE_OUTLET/2 + 5,
    TANK_DIAMETER/2 - WALL_THICKNESS - 5,
    CONE_HEIGHT - 20,
    App.Vector(0, 0, 10),
    App.Vector(0, 0, 1)
)
algae_obj = doc.addObject("Part::Feature", "AlgaeZone")
algae_obj.Shape = algae_zone
algae_obj.ViewObject.ShapeColor = (0.0, 0.6, 0.0, 0.6)  # Green algae

# ==================== ADD DIMENSIONS AS TEXT ====================
print("\n=== ALGAE SETTLING TANK DIMENSIONS ===")
print(f"Total Height: {TANK_HEIGHT}mm ({TANK_HEIGHT/10}cm)")
print(f"Tank Diameter: {TANK_DIAMETER}mm ({TANK_DIAMETER/10}cm)")
print(f"Cone Height: {CONE_HEIGHT}mm ({CONE_HEIGHT/10}cm)")
print(f"Drain Diameter: {CONE_OUTLET}mm")
print(f"Overflow Height: {OVERFLOW_HEIGHT}mm ({OVERFLOW_HEIGHT/10}cm)")
print(f"\nVolume (approx): {(3.14159 * (TANK_DIAMETER/2)**2 * TANK_HEIGHT) / 1000000:.2f} Liters")
print(f"Algae Collection Zone: {(3.14159 * (TANK_DIAMETER/2)**2 * CONE_HEIGHT) / 1000000:.2f} Liters")
print("\n=== HOW IT WORKS ===")
print("1. Algae grows in main cylinder (pump circulates)")
print("2. At 350 NTU: Pump stops")
print("3. 60 min: Algae settles into cone")
print("4. User presses button: Drain valve opens")
print("5. Concentrated algae drains from bottom")
print("6. Clean water stays on top")
print("7. System refills and restarts\n")

# Recompute and fit view
doc.recompute()
App.ActiveDocument = doc

# Save the file
import os
save_path = os.path.join(os.path.dirname(__file__), "algae_settling_tank.FCStd")
doc.saveAs(save_path)
print(f"Model saved to: {save_path}")
print("Open in FreeCAD to view and modify!")

# Optional: If running in FreeCAD GUI, adjust view
try:
    import FreeCADGui
    FreeCADGui.ActiveDocument.activeView().viewIsometric()
    FreeCADGui.SendMsgToActiveView("ViewFit")
except:
    pass
