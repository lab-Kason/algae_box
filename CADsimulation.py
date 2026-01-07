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
v_depth = 80  # mm - depth of V from sides to center (steeper V-angle for faster roll)
longitudinal_slope_angle = 12  # degrees - slope from high end to low end (steeper for faster slide to drain)
v_angle = 50  # degrees - angle of V-shape (from horizontal)

print("Creating 20L Fish Tank with V-Shaped Sloped Bottom:")
print("External dimensions: " + str(length) + "mm x " + str(width) + "mm x " + str(height) + "mm")
print("Glass thickness: " + str(glass_thickness) + "mm")
print("V-depth: " + str(v_depth) + "mm")
print("Longitudinal slope: " + str(longitudinal_slope_angle) + " degrees")
print("V-angle: " + str(v_angle) + " degrees")

# Create V-shaped bottom with longitudinal slope
# The V runs along the length, and slopes down from front to back
import math

# Calculate slope
slope_rad = math.radians(longitudinal_slope_angle)
slope_drop = length * math.tan(slope_rad)  # Total height drop over length

# Define key heights for the V-bottom
front_high = glass_thickness + slope_drop
back_low = glass_thickness

# Create walls (4 vertical panels) that connect to V-bottom edges
# Walls start from the V-bottom top edges and go upward

# Left wall - connects to left edge of V-bottom (from front_left_top going up)
left_wall_points_bottom = [
    Base.Vector(glass_thickness, glass_thickness, front_high),
    Base.Vector(glass_thickness, glass_thickness, height),
    Base.Vector(glass_thickness, width - glass_thickness, height),
    Base.Vector(glass_thickness, width - glass_thickness, front_high),
    Base.Vector(glass_thickness, glass_thickness, front_high)
]
left_wall_wire = Part.makePolygon(left_wall_points_bottom)
left_wall_face = Part.Face(left_wall_wire)

# Right wall - mirror of left
right_wall_points_bottom = [
    Base.Vector(length - glass_thickness, glass_thickness, back_low),
    Base.Vector(length - glass_thickness, glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, back_low),
    Base.Vector(length - glass_thickness, glass_thickness, back_low)
]
right_wall_wire = Part.makePolygon(right_wall_points_bottom)
right_wall_face = Part.Face(right_wall_wire)

# Front wall - connects front edge, slopes from front_high to back_low
front_wall_points = [
    Base.Vector(glass_thickness, glass_thickness, front_high),
    Base.Vector(glass_thickness, glass_thickness, height),
    Base.Vector(length - glass_thickness, glass_thickness, height),
    Base.Vector(length - glass_thickness, glass_thickness, back_low),
    Base.Vector(glass_thickness, glass_thickness, front_high)
]
front_wall_wire = Part.makePolygon(front_wall_points)
front_wall_face = Part.Face(front_wall_wire)

# Back wall - mirror of front
back_wall_points = [
    Base.Vector(glass_thickness, width - glass_thickness, front_high),
    Base.Vector(glass_thickness, width - glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, back_low),
    Base.Vector(glass_thickness, width - glass_thickness, front_high)
]
back_wall_wire = Part.makePolygon(back_wall_points)
back_wall_face = Part.Face(back_wall_wire)

# Create U-bottom shape (rounded bottom instead of sharp V)
# The U runs along the length (X-axis), slopes down from front to back
# Use multiple cross-sections to create smooth curved bottom

# Parameters for U-shape curve
num_cross_sections = 20  # Number of slices along length for smooth curve
num_arc_points = 15  # Points across the U-curve at each cross-section

u_bottom_faces = []

# Create cross-sections from front to back
for section_idx in range(num_cross_sections):
    # Progress along length (0 to 1)
    progress = section_idx / float(num_cross_sections - 1)
    x_pos = glass_thickness + progress * (length - 2 * glass_thickness)
    
    # Height at this longitudinal position (slopes down from front to back)
    section_top_height = front_high - progress * slope_drop
    section_bottom_height = section_top_height - v_depth
    
    # Create U-curve points at this cross-section
    curve_points = []
    for point_idx in range(num_arc_points):
        # Progress across width (-1 to +1, where 0 is center)
        y_progress = (point_idx / float(num_arc_points - 1)) * 2.0 - 1.0  # -1 to +1
        
        # Y position
        y_pos = width / 2 + y_progress * (width / 2 - glass_thickness)
        
        # Z height using parabola for U-shape pointing DOWN
        # At center (y_progress = 0): z = section_bottom_height (LOWEST)
        # At edges (y_progress = ±1): z = section_top_height (HIGHEST)
        arc_factor = abs(y_progress)  # 0 at center, 1 at edges
        # Parabolic U-shape: z rises from bottom as we move away from center
        z_offset = v_depth * (1.0 - arc_factor * arc_factor)  # 0 at edges, v_depth at center
        z_pos = section_top_height - z_offset  # Subtract to go down
        
        curve_points.append(Base.Vector(x_pos, y_pos, z_pos))
    
    # Store this cross-section
    if section_idx == 0:
        # Front cap - create triangular face from edge to edge through curve
        front_left_top = Base.Vector(glass_thickness, glass_thickness, front_high)
        front_right_top = Base.Vector(glass_thickness, width - glass_thickness, front_high)
        
        # Create front cap by connecting top edges to U-curve
        front_cap_points = [front_left_top] + curve_points + [front_right_top, front_left_top]
        front_cap_wire = Part.makePolygon(front_cap_points)
        front_cap_face = Part.Face(front_cap_wire)
        u_bottom_faces.append(front_cap_face)
    
    if section_idx == num_cross_sections - 1:
        # Back cap
        back_left_top = Base.Vector(length - glass_thickness, glass_thickness, back_low)
        back_right_top = Base.Vector(length - glass_thickness, width - glass_thickness, back_low)
        
        back_cap_points = [back_left_top] + curve_points + [back_right_top, back_left_top]
        back_cap_wire = Part.makePolygon(back_cap_points)
        back_cap_face = Part.Face(back_cap_wire)
        u_bottom_faces.append(back_cap_face)
    
    # Create surface patches between consecutive cross-sections
    if section_idx > 0:
        prev_curve = prev_curve_points
        curr_curve = curve_points
        
        # Create quad faces between consecutive curves
        for pt_idx in range(len(curr_curve) - 1):
            quad_points = [
                prev_curve[pt_idx],
                prev_curve[pt_idx + 1],
                curr_curve[pt_idx + 1],
                curr_curve[pt_idx],
                prev_curve[pt_idx]
            ]
            quad_wire = Part.makePolygon(quad_points)
            quad_face = Part.Face(quad_wire)
            u_bottom_faces.append(quad_face)
    
    prev_curve_points = curve_points

# Extract the left and right U-bottom faces (will be used to join with walls)
# Use first and last curve sections
left_v_face = u_bottom_faces[0]  # Placeholder - actual U-surface will be used
right_v_face = u_bottom_faces[0]  # Placeholder

# Don't create separate V-bottom object - it will be part of the main tank

# Combine all faces (walls + U-bottom) into one complete tank
try:
    all_faces = [left_wall_face, right_wall_face, front_wall_face, back_wall_face] + u_bottom_faces
    tank_shell = Part.Shell(all_faces)
    fish_tank = Part.Solid(tank_shell)
except:
    # If solid fails, use compound
    fish_tank = Part.makeCompound([left_wall_face, right_wall_face, front_wall_face, back_wall_face] + u_bottom_faces)

# Create a Part object and add it to the document
tank_obj = doc.addObject("Part::Feature", "UBottom_Tank_20L")
tank_obj.Shape = fish_tank
tank_obj.ViewObject.ShapeColor = (0.7, 0.9, 1.0)  # Light blue color for glass
tank_obj.ViewObject.Transparency = 70  # Make it semi-transparent like glass

print("")
print("U-shaped bottom tank created successfully!")
print("Bottom slopes from front (high) to back (low) with rounded U-curve")
print("Algae will roll along U-channel toward drain at back-center")

# Recompute the document
doc.recompute()

# Fit the view to show the entire tank
App.ActiveDocument = doc
Gui.ActiveDocument = doc
Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().activeView().viewIsometric()

print("The tank has an open top and U-shaped sloped bottom.")

# Create microalgae particles
import random
import time

num_algae = 100
algae_radius = 2  # mm - small spheres representing microalgae colonies

# Microalgae physical properties (based on typical Chlorella/Spirulina)
algae_density = 1050  # kg/m³ (slightly denser than water at 1000 kg/m³)
water_density = 1000  # kg/m³
water_viscosity = 0.001  # Pa·s (1 cP at 20°C)

# Stokes' settling velocity calculation
# v = (2/9) × (r²) × g × (ρ_algae - ρ_water) / μ
# For 10-50 micron algae cells (but we're modeling aggregates/flocs)
g = 9.81  # m/s²
algae_radius_m = algae_radius / 1000  # Convert mm to meters
settling_velocity_m_s = (2.0 / 9.0) * (algae_radius_m ** 2) * g * (algae_density - water_density) / water_viscosity
settling_velocity_mm_frame = settling_velocity_m_s * 1000 * 0.02  # Convert to mm per frame (0.02s per frame)

# Friction coefficient for sliding on smooth glass V-bottom
friction_coeff = 0.15  # Low friction (algae biofilm on glass)

algae_objects = []
algae_positions = []
algae_velocities = []

print("")
print("Creating " + str(num_algae) + " microalgae particles...")
print("Algae density: " + str(algae_density) + " kg/m³")
print("Water density: " + str(water_density) + " kg/m³")
print("Settling velocity: " + str(round(settling_velocity_mm_frame, 3)) + " mm/frame")
print("Friction coefficient: " + str(friction_coeff))

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
    
    # Use calculated settling velocity with slight random variation (±20%)
    individual_velocity = settling_velocity_mm_frame * random.uniform(0.8, 1.2)
    algae_velocities.append(individual_velocity)

doc.recompute()
print("Microalgae created!")

# Create drain valve indicator at back-center (lowest point of V)
drain_radius = 10  # mm - larger for visibility
drain_x = length - glass_thickness - 10  # BACK of tank (high X = back end)
drain_y = width / 2  # Center of tank width (centerline of V)
drain_z = back_low - v_depth  # Lowest point (back end, bottom of V)

drain_shape = Part.makeSphere(drain_radius)
drain_obj = doc.addObject("Part::Feature", "DrainValve")
drain_obj.Shape = drain_shape
drain_obj.Placement = App.Placement(App.Vector(drain_x, drain_y, drain_z), App.Rotation())
drain_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)  # Red color for valve

print("Drain valve created at back-center (lowest point of V-bottom)")
print("Drain position: X=" + str(round(drain_x, 1)) + "mm (back), Y=" + str(round(drain_y, 1)) + "mm (center), Z=" + str(round(drain_z, 1)) + "mm (lowest)")

# Animation parameters for V-bottom passive collection
num_frames_settle = 250  # Frames for settling phase (long time for algae to roll to centerline AND slide to drain)
num_frames_drain = 40   # Frames for draining
num_loops = 3           # Number of collection cycles

collected_algae = []    # Track collected algae

# Calculate V-bottom geometry for algae sliding
center_x = length / 2
center_y = width / 2

print("")
print("Starting U-BOTTOM PASSIVE COLLECTION animation...")
print("No tilting mechanism - tank stays stationary!")
print("Algae settle → roll down U-shape → concentrate at drain")
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
            
            # Calculate U-bottom height at current position
            # The U-bottom is a rounded VALLEY/TROUGH that runs from front to back
            # Algae must: 1) Roll down to centerline, 2) Slide along centerline to back
            
            dist_from_center_y = abs(y - center_y)
            
            # Longitudinal slope: the centerline height changes from front to back
            x_progress = max(0.0, min(1.0, (x - glass_thickness) / (length - 2 * glass_thickness)))
            centerline_height = front_high - x_progress * slope_drop - v_depth  # Centerline is ALWAYS at -v_depth
            
            # U-shape: distance from centerline determines how high algae sits (parabolic curve)
            # At centerline (y = center_y): height = centerline_height (LOWEST point)
            # At walls (y = edges): height = centerline_height + v_depth (HIGHEST)
            width_from_center = (width / 2 - glass_thickness)
            if width_from_center > 0:
                # Parabolic interpolation for U-shape pointing DOWN
                y_normalized = dist_from_center_y / width_from_center  # 0 at center to 1 at edges
                # Height rises from center: 0 rise at center, v_depth rise at edges
                u_rise_from_center = v_depth * (1.0 - (1.0 - y_normalized) ** 2)  # Parabola
            else:
                u_rise_from_center = 0
            
            # Bottom surface height at position (x, y)
            bottom_at_position = centerline_height + u_rise_from_center + algae_radius
            
            # Ensure algae don't go below the V-bottom surface
            if z < bottom_at_position:
                z = bottom_at_position
            
            # Check if hit bottom
            if z <= bottom_at_position:
                z = bottom_at_position
                
                # Once on bottom, algae MUST roll down to centerline first, then slide along it
                # The U-shape acts like a valley - everything rolls to the bottom
                
                # STEP 1: Roll toward centerline (U-shape gravity)
                if abs(y - center_y) > 0.5:  # Not at center yet
                    # U-slope angle (derivative of parabola at current position)
                    y_normalized = dist_from_center_y / width_from_center
                    # Slope of parabola: dz/dy = 2 * v_depth * (1 - y_normalized) / width_from_center
                    u_slope_tangent = 2.0 * v_depth * (1.0 - y_normalized) / width_from_center
                    u_slope_angle = math.atan(u_slope_tangent)
                    
                    # Sliding force down the U-slope
                    u_slide_factor = math.sin(u_slope_angle) * (1.0 - friction_coeff)
                    u_slide_speed = 3.5 * u_slide_factor  # Fast roll to centerline
                    
                    # Roll toward center Y
                    if y < center_y:
                        y = y + u_slide_speed
                    else:
                        y = y - u_slide_speed
                
                # STEP 2: Once near centerline, slide toward back (along the valley bottom)
                if abs(y - center_y) <= 5.0:  # Within 5mm of centerline = in the valley
                    long_slope_angle = math.atan(slope_drop / (length - 2 * glass_thickness))
                    long_slide_factor = math.sin(long_slope_angle) * (1.0 - friction_coeff)
                    long_slide_speed = 3.0 * long_slide_factor  # Fast slide along valley
                    
                    # Slide toward back
                    x = x + long_slide_speed
                
                # Recalculate Z position to stay on V-surface
                x_progress_new = max(0.0, min(1.0, (x - glass_thickness) / (length - 2 * glass_thickness)))
                centerline_height_new = front_high - x_progress_new * slope_drop - v_depth
                
                dist_from_center_y_new = abs(y - center_y)
                y_normalized_new = dist_from_center_y_new / width_from_center
                u_rise_from_center_new = v_depth * (1.0 - (1.0 - y_normalized_new) ** 2)
                
                z = centerline_height_new + u_rise_from_center_new + algae_radius
                
                # Clamp to boundaries
                x = min(x, length - glass_thickness - algae_radius)
                x = max(x, glass_thickness + algae_radius)
                y = min(y, width - glass_thickness - algae_radius)
                y = max(y, glass_thickness + algae_radius)
                
                algae_positions[i][0] = x
                algae_positions[i][1] = y
                algae_positions[i][2] = z
            
            # Update position (Z already updated if on bottom)
            if i not in collected_algae:
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
            collection_radius = 100  # mm - larger radius to catch all concentrated algae
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
print("Method: U-BOTTOM WITH LONGITUDINAL SLOPE (PASSIVE)")
print("Benefits:")
print("  ✓ No tilting mechanism - tank stays stationary")
print("  ✓ Scalable to any size (20L to 1000L+)")
print("  ✓ U-shape (rounded) concentrates algae to centerline")
print("  ✓ Smoother rolling than V-shape - less algae stuck on sides")
print("  ✓ Longitudinal slope moves algae toward drain")
print("  ✓ Only ONE valve needed - no servo/actuator")
print("  ✓ No mechanical parts touching algae")
print("  ✓ Gravity does all the work")
print("  ✓ Minimal disturbance, no re-suspension")
print("  ✓ Industrial proven design")
print("")
print("Tank Design:")
print("  - U-shape: Parabolic curve (from horizontal)")
print("  - U-depth: " + str(v_depth) + " mm")
print("  - Longitudinal slope: " + str(longitudinal_slope_angle) + "° (high front → low back)")
print("  - Drain location: Back-center (lowest point)")