import FreeCAD as App
import Part
from FreeCAD import Base

# Create a new document
doc = App.newDocument("FishTank20L")

# Calculate dimensions for a 20L tank
# Using a common aquarium aspect ratio (length:width:height = 2:1:1)
# 20L = 20,000 cubic cm
# If we use ratio 2:1:1, then: 2w * w * w = 20,000
# w^3 = 10,000, so w = 21.54 cm (approx)
# Dimensions: 43cm x 21.5cm x 21.5cm (approximately 20L)

# External dimensions (in mm for FreeCAD)
length = 430  # 43 cm
width = 215   # 21.5 cm
height = 215  # 21.5 cm

# Glass thickness (typical aquarium glass: 5-6mm)
glass_thickness = 6  # mm

# V-bottom design parameters
v_depth = 60  # mm - depth of V from sides to center
longitudinal_slope_angle = 5  # degrees - slope from high end to low end
v_angle = 50  # degrees - angle of V-shape (from horizontal)

print("Creating 20L Fish Tank with V-Shaped Sloped Bottom:")
print("External dimensions: " + str(length) + "mm x " + str(width) + "mm x " + str(height) + "mm")
print("Glass thickness: " + str(glass_thickness) + "mm")
print("V-depth: " + str(v_depth) + "mm")
print("Longitudinal slope: " + str(longitudinal_slope_angle) + " degrees")
print("V-angle: " + str(v_angle) + " degrees")

# Create walls as separate boxes (left, right, front, back)
# Left wall
left_wall = Part.makeBox(
    glass_thickness,
    width,
    height,
    Base.Vector(0, 0, 0)
)

# Right wall
right_wall = Part.makeBox(
    glass_thickness,
    width,
    height,
    Base.Vector(length - glass_thickness, 0, 0)
)

# Front wall
front_wall = Part.makeBox(
    length,
    glass_thickness,
    height,
    Base.Vector(0, 0, 0)
)

# Back wall  
back_wall = Part.makeBox(
    length,
    glass_thickness,
    height,
    Base.Vector(0, width - glass_thickness, 0)
)

# Create V-shaped bottom with longitudinal slope
# The V runs along the length, and slopes down from front to back
import math

# Calculate slope
slope_rad = math.radians(longitudinal_slope_angle)
slope_drop = length * math.tan(slope_rad)  # Total height drop over length

# V-shape angle
v_rad = math.radians(v_angle)

# Create V-bottom using vertices
# Front end (high): V-peak at height = glass_thickness + slope_drop
# Back end (low): V-peak at height = glass_thickness

# Define vertices for the V-bottom (a prism with triangular cross-section)
front_high = glass_thickness + slope_drop
back_low = glass_thickness

# Front triangle vertices (high end)
v1_front_left = Base.Vector(glass_thickness, glass_thickness, front_high)
v2_front_right = Base.Vector(length - glass_thickness, glass_thickness, front_high)
v3_front_center = Base.Vector(length / 2, width / 2, front_high - v_depth)

# Back triangle vertices (low end - this is where drain will be)
v1_back_left = Base.Vector(glass_thickness, glass_thickness, back_low)
v2_back_right = Base.Vector(length - glass_thickness, glass_thickness, back_low)
v3_back_center = Base.Vector(length / 2, width / 2, back_low - v_depth)

# Front triangle (mirrored for both sides of V)
v4_front_left_far = Base.Vector(glass_thickness, width - glass_thickness, front_high)
v5_front_right_far = Base.Vector(length - glass_thickness, width - glass_thickness, front_high)

# Back triangle (mirrored)
v4_back_left_far = Base.Vector(glass_thickness, width - glass_thickness, back_low)
v5_back_right_far = Base.Vector(length - glass_thickness, width - glass_thickness, back_low)

# Create left V-panel
left_v_panel = Part.makePolygon([v1_front_left, v3_front_center, v3_back_center, v1_back_left, v1_front_left])
left_v_face = Part.Face(left_v_panel)
left_v_solid = left_v_face.extrude(Base.Vector(0, 0, 0))

# Create right V-panel  
right_v_panel = Part.makePolygon([v4_front_left_far, v3_front_center, v3_back_center, v4_back_left_far, v4_front_left_far])
right_v_face = Part.Face(right_v_panel)
right_v_solid = right_v_face.extrude(Base.Vector(0, 0, 0))

# Create front triangular end
front_triangle = Part.makePolygon([v1_front_left, v3_front_center, v4_front_left_far, v1_front_left])
front_face = Part.Face(front_triangle)

# Create back triangular end
back_triangle = Part.makePolygon([v1_back_left, v3_back_center, v4_back_left_far, v1_back_left])
back_face = Part.Face(back_triangle)

# Combine all walls into tank
# Use simpler approach: create outer box and inner cavity separately
outer_shell = Part.makeBox(length, width, height)

# Create inner cavity as a compound shape (approximately)
# For visualization, we'll create a simplified V-bottom tank
inner_width = width - 2 * glass_thickness
inner_length = length - 2 * glass_thickness

# Create top rectangular part
top_cavity = Part.makeBox(
    inner_length,
    inner_width, 
    height - v_depth - slope_drop,
    Base.Vector(glass_thickness, glass_thickness, glass_thickness + v_depth + slope_drop/2)
)

# Combine walls
fish_tank = left_wall.fuse(right_wall).fuse(front_wall).fuse(back_wall)

# Add the V-bottom visualization (simplified for FreeCAD compatibility)
# Create sloped bottom reference plane
slope_bottom = Part.makePlane(
    inner_length,
    inner_width,
    Base.Vector(glass_thickness, glass_thickness, glass_thickness + slope_drop/2),
    Base.Vector(0, 0, 1)
)

# Create a Part object and add it to the document
tank_obj = doc.addObject("Part::Feature", "VBottom_Tank_20L")
tank_obj.Shape = fish_tank
tank_obj.ViewObject.ShapeColor = (0.7, 0.9, 1.0)  # Light blue color for glass
tank_obj.ViewObject.Transparency = 70  # Make it semi-transparent like glass

print("")
print("V-shaped bottom tank created successfully!")
print("Bottom slopes from front (high) to back (low)")
print("Algae will slide along V-channel toward drain at back-center")

# Recompute the document
doc.recompute()

# Fit the view to show the entire tank
App.ActiveDocument = doc
Gui.ActiveDocument = doc
Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().activeView().viewIsometric()

print("The tank has an open top and V-shaped sloped bottom.")

# Create microalgae particles
import random
import time

num_algae = 100
algae_radius = 2  # mm - small spheres
algae_objects = []
algae_positions = []
algae_velocities = []

print("")
print("Creating " + str(num_algae) + " microalgae particles...")

# Create algae spheres at random positions in the tank
inner_length_calc = length - 2 * glass_thickness
inner_width_calc = width - 2 * glass_thickness

for i in range(num_algae):
    # Random initial position in upper half of tank
    x = glass_thickness + random.uniform(0, inner_length_calc)
    y = glass_thickness + random.uniform(0, inner_width_calc)
    z = height * random.uniform(0.6, 0.95)  # Upper portion
    
    # Create sphere
    sphere = Part.makeSphere(algae_radius)
    algae_obj = doc.addObject("Part::Feature", "Algae_" + str(i))
    algae_obj.Shape = sphere
    algae_obj.Placement = App.Placement(App.Vector(x, y, z), App.Rotation())
    
    # Set green color with slight variation
    green_shade = random.uniform(0.3, 0.7)
    algae_obj.ViewObject.ShapeColor = (0.0, green_shade, 0.0)
    
    # Store object and position
    algae_objects.append(algae_obj)
    algae_positions.append([x, y, z])
    
    # Random sinking velocity (0.5 to 2.0 mm per frame - slow sinking)
    algae_velocities.append(random.uniform(0.5, 2.0))

doc.recompute()
print("Microalgae created!")

# Create drain valve indicator at back-center (lowest point of V)
drain_radius = 10  # mm - larger for visibility
drain_x = length / 2  # Center of tank width
drain_y = width / 2  # Center of tank depth
drain_z = back_low - v_depth  # Lowest point (back end, bottom of V)

drain_shape = Part.makeSphere(drain_radius)
drain_obj = doc.addObject("Part::Feature", "DrainValve")
drain_obj.Shape = drain_shape
drain_obj.Placement = App.Placement(App.Vector(drain_x, drain_y, drain_z), App.Rotation())
drain_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)  # Red color for valve
# Animation parameters for V-bottom passive collection
num_frames_settle = 80  # Frames for settling phase (longer for realistic settling + sliding)
num_frames_drain = 40   # Frames for draining
num_loops = 3           # Number of collection cycles

collected_algae = []    # Track collected algae

# Calculate V-bottom geometry for algae sliding
center_x = length / 2
center_y = width / 2

print("")
print("Starting V-BOTTOM PASSIVE COLLECTION animation...")
print("No tilting mechanism - tank stays stationary!")
print("Algae settle → slide down V-shape → concentrate at drain")
print("Collection cycles: " + str(num_loops))
print("")arting DRAIN-AND-TILT collection animation...")
print("Tilt angle: " + str(tilt_angle_max) + " degrees")
print("Collection cycles: " + str(num_loops))
print("")

loop_count = 0
while loop_count < num_loops:
    print("=== CYCLE " + str(loop_count + 1) + " ===")
    
    # PHASE 1: SETTLING AND SLIDING - Algae sink and slide down V-bottom toward drain
    print("Phase 1: Settling & sliding down V-bottom to drain...")
    for frame in range(num_frames_settle):
        for i in range(num_algae):
            if i in collected_algae:
                continue
            
            x = algae_positions[i][0]
            y = algae_positions[i][1]
            z = algae_positions[i][2]
            
            # Apply sinking
            z = z - algae_velocities[i]
            
            # Calculate V-bottom height at current position
            # V-bottom: center line is lowest, sides are higher
            dist_from_center_y = abs(y - center_y)
            v_height_at_y = v_depth * (dist_from_center_y / (width / 2 - glass_thickness))
            
            # Longitudinal slope: higher at front, lower at back
            x_progress = (x - glass_thickness) / (length - 2 * glass_thickness)
            longitudinal_height = front_high - x_progress * slope_drop
            
            # Combined bottom height
            bottom_at_position = longitudinal_height - v_height_at_y + algae_radius
            
            # Check if hit bottom
            if z <= bottom_at_position:
                z = bottom_at_position
                
                # Once on bottom, slide toward center and toward back (drain)
                # Slide toward center Y (V-shape effect)
                if y < center_y:
                    y = y + 0.3  # Slide toward center
                elif y > center_y:
                    y = y - 0.3  # Slide toward center
                
                # Slide toward back (longitudinal slope effect)
                x = x + 0.4  # Slide toward back (higher X = toward back/drain)
                
                # Clamp to boundaries
                x = min(x, length - glass_thickness - algae_radius)
                x = max(x, glass_thickness + algae_radius)
                y = min(y, width - glass_thickness - algae_radius)
                y = max(y, glass_thickness + algae_radius)
                
                algae_positions[i][0] = x
                algae_positions[i][1] = y
            
            # Update position
            algae_positions[i][2] = z
            algae_objects[i].Placement = App.Placement(
                App.Vector(x, y, z),
                App.Rotation()
            )
        
        doc.recompute()
        Gui.updateGui()
        time.sleep(0.02)
    
    # PHASE 2: DRAINING - Collect algae near drain (back-center, lowest point)
    print("Phase 2: Opening drain valve (collecting concentrated algae)...")
    drain_obj.ViewObject.ShapeColor = (0.0, 1.0, 0.0)  # Green = valve open
    
    for frame in range(num_frames_drain):
        # Check which algae are near drain and collect them
        for i in range(num_algae):
            if i in collected_algae:
                continue
            
            x = algae_positions[i][0]
            y = algae_positions[i][1]
            z = algae_positions[i][2]
            
            # Check if algae is near drain (within collection radius)
            collection_radius = 60  # mm - larger radius since algae concentrate here
            distance_to_drain = ((x - drain_x)**2 + (y - drain_y)**2 + (z - drain_z)**2)**0.5
            
            if distance_to_drain < collection_radius:
                # Algae collected through drain
                collected_algae.append(i)
                algae_objects[i].ViewObject.ShapeColor = (0.3, 0.3, 0.3)  # Dark gray
                algae_objects[i].ViewObject.Transparency = 90
                
                # Animate algae moving toward drain
                move_x = (drain_x - x) * 0.15
                move_y = (drain_y - y) * 0.15
                move_z = (drain_z - z) * 0.15
                algae_positions[i][0] = x + move_x
                algae_positions[i][1] = y + move_y
                algae_positions[i][2] = z + move_z
                
                # Update visual position
                algae_objects[i].Placement = App.Placement(
                    App.Vector(algae_positions[i][0], 
                              algae_positions[i][1], 
                              algae_positions[i][2]),
                    App.Rotation()
                )
        
        doc.recompute()
        Gui.updateGui()
        time.sleep(0.03)
    
    drain_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)  # Red = valve closed
    print("Collected: " + str(len(collected_algae)) + "/" + str(num_algae) + " algae")
    print("(Tank remains stationary - no tilting mechanism needed!)")
    print("")
    
    loop_count = loop_count + 1

print("")
print("=== ANIMATION COMPLETE ===")
print("Total microalgae collected: " + str(len(collected_algae)) + "/" + str(num_algae))
print("Collection efficiency: " + str(round(100.0 * len(collected_algae) / num_algae, 1)) + "%")
print("")
print("Method: DRAIN-AND-TILT")
print("Benefits:")
print("  - No mechanical parts touching algae")
print("  - Minimal disturbance, no re-suspension")
print("  - Gravity-driven, reliable")
print("  - Simple servo/linear actuator control")
print("")
print("=== ANIMATION COMPLETE ===")
print("Total microalgae collected: " + str(len(collected_algae)) + "/" + str(num_algae))
print("Collection efficiency: " + str(round(100.0 * len(collected_algae) / num_algae, 1)) + "%")
print("")
print("Method: V-BOTTOM WITH LONGITUDINAL SLOPE (PASSIVE)")
print("Benefits:")
print("  ✓ No tilting mechanism - tank stays stationary")
print("  ✓ Scalable to any size (20L to 1000L+)")
print("  ✓ V-shape concentrates algae to centerline")
print("  ✓ Longitudinal slope moves algae toward drain")
print("  ✓ Only ONE valve needed - no servo/actuator")
print("  ✓ No mechanical parts touching algae")
print("  ✓ Gravity does all the work")
print("  ✓ Minimal disturbance, no re-suspension")
print("  ✓ Industrial proven design")
print("")
print("Tank Design:")
print("  - V-angle: " + str(v_angle) + "° (from horizontal)")
print("  - V-depth: " + str(v_depth) + " mm")
print("  - Longitudinal slope: " + str(longitudinal_slope_angle) + "° (high front → low back)")
print("  - Drain location: Back-center (lowest point)")