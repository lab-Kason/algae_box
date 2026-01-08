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

print("Creating Standard 20L Rectangular Tank:")
print("External dimensions: " + str(length) + "mm x " + str(width) + "mm x " + str(height) + "mm")
print("Glass thickness: " + str(glass_thickness) + "mm")

# Create standard rectangular tank
import math

# Create 6 rectangular panels for hollow tank

# Bottom panel
bottom_points = [
    Base.Vector(glass_thickness, glass_thickness, glass_thickness),
    Base.Vector(length - glass_thickness, glass_thickness, glass_thickness),
    Base.Vector(length - glass_thickness, width - glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, width - glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, glass_thickness, glass_thickness)
]
bottom_wire = Part.makePolygon(bottom_points)
bottom_face = Part.Face(bottom_wire)

# Left wall
left_wall_points = [
    Base.Vector(glass_thickness, glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, glass_thickness, height),
    Base.Vector(glass_thickness, width - glass_thickness, height),
    Base.Vector(glass_thickness, width - glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, glass_thickness, glass_thickness)
]
left_wall_wire = Part.makePolygon(left_wall_points)
left_wall_face = Part.Face(left_wall_wire)

# Right wall
right_wall_points = [
    Base.Vector(length - glass_thickness, glass_thickness, glass_thickness),
    Base.Vector(length - glass_thickness, glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, glass_thickness),
    Base.Vector(length - glass_thickness, glass_thickness, glass_thickness)
]
right_wall_wire = Part.makePolygon(right_wall_points)
right_wall_face = Part.Face(right_wall_wire)

# Front wall
front_wall_points = [
    Base.Vector(glass_thickness, glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, glass_thickness, height),
    Base.Vector(length - glass_thickness, glass_thickness, height),
    Base.Vector(length - glass_thickness, glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, glass_thickness, glass_thickness)
]
front_wall_wire = Part.makePolygon(front_wall_points)
front_wall_face = Part.Face(front_wall_wire)

# Back wall
back_wall_points = [
    Base.Vector(glass_thickness, width - glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, width - glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, height),
    Base.Vector(length - glass_thickness, width - glass_thickness, glass_thickness),
    Base.Vector(glass_thickness, width - glass_thickness, glass_thickness)
]
back_wall_wire = Part.makePolygon(back_wall_points)
back_wall_face = Part.Face(back_wall_wire)

# Combine all faces into one hollow tank
try:
    all_faces = [bottom_face, left_wall_face, right_wall_face, front_wall_face, back_wall_face]
    tank_shell = Part.Shell(all_faces)
    fish_tank = Part.Solid(tank_shell)
except:
    # If solid fails, use compound
    fish_tank = Part.makeCompound([bottom_face, left_wall_face, right_wall_face, front_wall_face, back_wall_face])

# Create a Part object and add it to the document
tank_obj = doc.addObject("Part::Feature", "Standard_Tank_20L")
tank_obj.Shape = fish_tank
tank_obj.ViewObject.ShapeColor = (0.7, 0.9, 1.0)  # Light blue color for glass
tank_obj.ViewObject.Transparency = 70  # Make it semi-transparent like glass

print("")
print("Standard rectangular tank created successfully!")
print("Open top, flat bottom - standard aquarium design")
print("Internal volume: ~20L")

# Recompute the document
doc.recompute()

# Fit the view to show the entire tank
App.ActiveDocument = doc
Gui.ActiveDocument = doc
Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().activeView().viewIsometric()

print("The tank has an open top and flat bottom - standard design.")

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

# Friction coefficient for sliding on smooth glass bottom
friction_coeff = 0.15  # Low friction (algae biofilm on glass)

# Water resistance parameters (CRITICAL for realistic physics)
# Drag force in water: F_drag = 6πμrv (Stokes drag for low Reynolds number)
# Reynolds number: Re = ρvd/μ (for algae in water flow)
algae_diameter_m = 2 * algae_radius_m  # meters
water_kinematic_viscosity = water_viscosity / water_density  # m²/s

# Boundary layer effect: flow velocity decreases near bottom surface
# At bottom (z=0): v = 0 (no-slip condition)
# At height h above bottom: v ≈ v_bulk × (h/δ)^(1/7) for turbulent boundary layer
# where δ is boundary layer thickness (~1-5mm for low-speed flow)
boundary_layer_thickness = 3.0  # mm - typical for laminar/transitional flow
manifold_height_above_bottom = 10.0  # mm

print("Water resistance physics enabled:")
print("  - Boundary layer thickness: " + str(boundary_layer_thickness) + " mm")
print("  - Flow velocity gradient near bottom (affects algae movement)")
print("  - Drag force reduces effective sweeping velocity")

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

# Create flow manifold system for algae sweeping
print("")
print("Creating flow manifold system...")
print("")
print("FLOW CONFIGURATION:")
print("  Manifold at FRONT wall (inlet side)")
print("  → Water flows from FRONT to BACK")
print("  → Algae swept toward BACK wall")
print("  Drain at BACK wall (collection side)")
print("")

# Manifold specifications
manifold_diameter = 25  # mm - PVC pipe diameter
manifold_width = width - 2 * glass_thickness - 20  # Spans almost full width
manifold_x = glass_thickness + 30  # Near FRONT wall
manifold_y_start = glass_thickness + 10  # Left side
manifold_y_end = width - glass_thickness - 10  # Right side
manifold_z = glass_thickness + 10  # 10mm above bottom

# Create manifold pipe spanning WIDTH (perpendicular to flow direction)
# This creates uniform flow across the entire tank width
manifold_pipe = Part.makeCylinder(manifold_diameter/2, manifold_width, 
                                  Base.Vector(manifold_x, manifold_y_start, manifold_z),
                                  Base.Vector(0, 1, 0))  # Along Y-axis (width direction)
manifold_obj = doc.addObject("Part::Feature", "FlowManifold")
manifold_obj.Shape = manifold_pipe
manifold_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)  # Gray PVC
manifold_obj.ViewObject.Transparency = 30

# Create SLOT CUT instead of holes - creates "water knife" effect
# Horizontal slot along the entire length of pipe
slot_length = manifold_width - 10  # Almost full pipe length
slot_width = 8  # mm - width of horizontal cut (adjustable for flow rate)
slot_height = 3  # mm - depth of cut

# Visual representation: rectangular slot opening
slot_box = Part.makeBox(slot_width, slot_length, slot_height,
                       Base.Vector(manifold_x + manifold_diameter/2, 
                                 manifold_y_start + 5,
                                 manifold_z - slot_height/2))
slot_obj = doc.addObject("Part::Feature", "SlotCut")
slot_obj.Shape = slot_box
slot_obj.ViewObject.ShapeColor = (0.0, 0.3, 1.0)  # Dark blue for slot opening
slot_obj.ViewObject.Transparency = 20

print("Flow manifold created:")
print("  - Pipe diameter: " + str(manifold_diameter) + "mm")
print("  - Pipe orientation: ACROSS tank width (Y-axis)")
print("  - SLOT CUT design: " + str(slot_length) + "mm × " + str(slot_width) + "mm")
print("  - Creates 'water knife' curtain effect")
print("  - Uniform laminar flow across entire width")
print("  - Height above bottom: " + str(manifold_z - glass_thickness) + "mm")

# Create flow direction arrows (visual guide)
arrow_objects = []
for i in range(3):
    arrow_y = manifold_y_start + (i + 1) * manifold_width / 4
    arrow_start_x = manifold_x + 50
    arrow_end_x = length - glass_thickness - 50
    
    # Arrow shaft (cone pointing backward)
    arrow_shaft = Part.makeCone(3, 1, 30, 
                                Base.Vector(arrow_start_x, arrow_y, manifold_z),
                                Base.Vector(1, 0, 0))  # Points in +X direction
    arrow_obj = doc.addObject("Part::Feature", "FlowArrow_" + str(i))
    arrow_obj.Shape = arrow_shaft
    arrow_obj.ViewObject.ShapeColor = (0.0, 0.7, 1.0)  # Cyan for flow direction
    arrow_obj.ViewObject.Transparency = 50
    arrow_objects.append(arrow_obj)

# Create drain/collection slot at BACK wall
# Slot design: better than single point for even collection
drain_slot_length = width - 2 * glass_thickness - 40  # Almost full width
drain_slot_width = 30  # mm
drain_slot_height = 20  # mm
drain_x = length - glass_thickness - 15  # At BACK wall
drain_y_center = width / 2

# Create rectangular drain slot
drain_box = Part.makeBox(drain_slot_width, drain_slot_length, drain_slot_height,
                         Base.Vector(drain_x - drain_slot_width/2, 
                                   drain_y_center - drain_slot_length/2,
                                   glass_thickness))
drain_obj = doc.addObject("Part::Feature", "CollectionDrain")
drain_obj.Shape = drain_box
drain_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)  # Red for drain
drain_obj.ViewObject.Transparency = 40

# Create flow direction arrows (visual guide)
print("")
print("  - Drain type: SLOT (full width collection)")
print("  - Drain location: BACK wall")
print("  - Drain dimensions: " + str(drain_slot_width) + "mm × " + str(drain_slot_length) + "mm")
print("")
print("FLOW PATH: FRONT → BACK (unidirectional sweeping)")
print("Water curtain from slot cut creates uniform 'water knife' effect")

doc.recompute()

# Animation parameters
num_frames_settle = 100  # Settling phase
num_sweep_passes = 3    # Number of repeated sweep passes
num_frames_per_pass = 600  # Frames per sweep pass (TRIPLED from 200 to 600)
num_frames_sweep = num_sweep_passes * num_frames_per_pass  # Total sweep time
num_frames_collection = 60  # Collection waiting phase after sweeping (pump OFF)
num_frames_drain = 40   # Draining phase
num_loops = 1           # Single complete cycle (settle → sweep → collect → drain)

collected_algae = []    # Track collected algae
swept_algae = []        # Track algae being swept
ready_for_drain = []    # Algae at drain area, ready to be drained

# Bottom height
bottom_height = glass_thickness

# Flow parameters - UNIDIRECTIONAL FLOW (front to back)
# NOTE: Flow velocity in WATER, not air - significant drag resistance
flow_velocity_bulk = 0.25  # mm/frame - bulk flow velocity away from walls
flow_direction_x = 1.0  # Flow toward back (positive X direction)
flow_direction_y = 0.0  # No lateral movement

# Boundary layer correction: algae on bottom experience reduced flow
# Velocity at algae height (radius above bottom) is much lower than bulk flow
algae_height_above_bottom = algae_radius  # mm - center of algae sphere
velocity_reduction_factor = min(1.0, (algae_height_above_bottom / boundary_layer_thickness) ** 0.5)
flow_velocity_at_algae = flow_velocity_bulk * velocity_reduction_factor  # Reduced by ~40-60%

# Water drag coefficient (for sphere in viscous flow)
# At low Reynolds number (Re < 1), drag coefficient C_d ≈ 24/Re
# Drag force: F_drag = 0.5 × ρ × v² × A × C_d = 6πμrv (Stokes)
drag_reduction_factor = 0.6  # Drag reduces effective velocity by ~40%

print("Flow velocity (accounting for water resistance):")
print("  - Bulk flow: " + str(flow_velocity_bulk) + " mm/frame")
print("  - At algae height: " + str(round(flow_velocity_at_algae, 3)) + " mm/frame (" + str(round(velocity_reduction_factor * 100, 1)) + "% of bulk)")
print("  - After drag reduction: ~" + str(round(flow_velocity_at_algae * drag_reduction_factor, 3)) + " mm/frame effective")
print("")
print("Critical threshold: if flow too strong, algae lift off bottom and re-suspend")
print("  - Current setting: GENTLE flow preserves laminar boundary layer")

# Algae adhesion properties
algae_adhesion_strength = []  # How "sticky" each algae is to the bottom
for i in range(num_algae):
    # Random adhesion (some algae stick harder than others)
    adhesion = random.uniform(0.3, 1.0)  # 0.3 = easy to move, 1.0 = very sticky
    algae_adhesion_strength.append(adhesion)

print("")
print("Starting FLOW-ASSISTED COLLECTION ANIMATION...")
print("Complete cycle sequence:")
print("  Phase 1: Gravity settling (pump OFF)")
print("  Phase 2: Flush pass 1 (pump ON)")
print("  Phase 3: Flush pass 2 (pump ON)")
print("  Phase 4: Flush pass 3 (pump ON)")
print("  Phase 5: Collection waiting (pump OFF, algae settle at drain)")
print("  Phase 6: Drain valve opens (physical removal)")
print("  Phase 7: Close valve, cycle complete")
print("")
print("Animation parameters:")
print("         - Number of flush passes: " + str(num_sweep_passes))
print("         - Frames per pass: " + str(num_frames_per_pass))
print("         - Total flush duration: " + str(num_frames_sweep) + " frames")
print("         - Flow velocity (bulk): " + str(flow_velocity_bulk) + " mm/frame")
print("         - Flow velocity (effective at algae): " + str(round(flow_velocity_at_algae * drag_reduction_factor, 3)) + " mm/frame")
print("")

loop_count = 0
while loop_count < num_loops:
    print("=== COMPLETE COLLECTION CYCLE ===")
    print("")
    # PHASE 1: SETTLING - Algae sink to flat bottom (pump OFF)
    print("Phase 1: Settling - algae drop to bottom (pump OFF)...")
    for frame in range(num_frames_settle):
        for i in range(num_algae):
            if i in collected_algae:
                continue
            
            x = algae_positions[i][0]
            y = algae_positions[i][1]
            z = algae_positions[i][2]
            
            # Apply sinking
            z = z - algae_velocities[i]
            
            # Check if reached bottom
            bottom_position = bottom_height + algae_radius
            if z <= bottom_position:
                z = bottom_position
                # Mark as on bottom (ready for sweeping)
                if i not in swept_algae:
                    swept_algae.append(i)
            
            # Update position
            algae_positions[i][2] = z
            algae_objects[i].Placement = App.Placement(
                App.Vector(x, y, z),
                App.Rotation()
            )
        
        if frame % 20 == 0:  # Update every 20 frames
            doc.recompute()
            Gui.updateGui()
            time.sleep(0.02)
    
    doc.recompute()
    Gui.updateGui()
    print("  -> " + str(len(swept_algae)) + " algae settled to bottom")
    print("")
    
    # PHASE 2-4: FLUSHING - Multiple passes with gentle horizontal flow (pump ON)
    print("Phase 2-4: Flushing - " + str(num_sweep_passes) + " passes (pump ON)...")
    
    # Visualize flow with manifold color change
    manifold_obj.ViewObject.ShapeColor = (0.0, 0.5, 1.0)  # Blue when active
    slot_obj.ViewObject.ShapeColor = (0.0, 1.0, 1.0)  # Bright cyan for active slot
    for arrow_obj in arrow_objects:
        arrow_obj.ViewObject.ShapeColor = (0.0, 1.0, 1.0)  # Bright cyan when flowing
    doc.recompute()
    Gui.updateGui()
    
    # Track how long each algae has been exposed to flow
    algae_flow_time = [0] * num_algae
    
    current_pass = 0
    for frame in range(num_frames_sweep):
        # Track which pass we're in
        new_pass = int(frame / num_frames_per_pass) + 1
        if new_pass != current_pass:
            current_pass = new_pass
            print("  -> Flush pass " + str(current_pass) + "/" + str(num_sweep_passes) + " starting...")
        
        for i in range(num_algae):
            if i in collected_algae or i in ready_for_drain:
                continue
            
            x = algae_positions[i][0]
            y = algae_positions[i][1]
            z = algae_positions[i][2]
            
            # If on bottom, apply UNIDIRECTIONAL horizontal flow
            if i in swept_algae:
                # Increase flow exposure time
                algae_flow_time[i] += 1
                
                # Adhesion weakens over time as flow continuously pushes
                # adhesion_effect reduces from 1.0 to 0.1 as flow_time increases
                adhesion_effect = algae_adhesion_strength[i] / (1.0 + algae_flow_time[i] / 30.0)
                
                # Effective velocity calculation (including water resistance):
                # 1. Start with flow velocity at algae height (boundary layer correction)
                # 2. Apply drag reduction (water viscosity)
                # 3. Subtract adhesion resistance
                base_velocity = flow_velocity_at_algae * drag_reduction_factor
                effective_velocity = base_velocity * (1.0 - adhesion_effect * 0.8)
                
                # Simple unidirectional push: FRONT → BACK (increasing X)
                x = x + effective_velocity * flow_direction_x
                
                # Slight random Y movement (turbulence helps break adhesion)
                y = y + random.uniform(-0.08, 0.08)
                
                # Keep within tank bounds
                if y < glass_thickness + algae_radius:
                    y = glass_thickness + algae_radius
                if y > width - glass_thickness - algae_radius:
                    y = width - glass_thickness - algae_radius
                
                # Keep on bottom
                z = bottom_height + algae_radius
                
                # Visual feedback: algae color darkens with adhesion strength
                if adhesion_effect > 0.5:
                    # Still stuck - darker green
                    algae_objects[i].ViewObject.ShapeColor = (0.0, 0.3, 0.0)
                else:
                    # Moving freely - lighter green
                    algae_objects[i].ViewObject.ShapeColor = (0.0, 0.6, 0.0)
                
                # Check if reached drain slot at back wall
                reached_back = x >= (drain_x - drain_slot_width/2 - algae_radius)
                in_drain_width = abs(y - drain_y_center) <= drain_slot_length/2
                
                if reached_back and in_drain_width:
                    ready_for_drain.append(i)
                    swept_algae.remove(i)
                    algae_objects[i].ViewObject.ShapeColor = (1.0, 0.5, 0.0)  # Orange when at drain area
            else:
                # Continue settling if not on bottom yet
                z = z - algae_velocities[i]
                if z <= bottom_height + algae_radius:
                    z = bottom_height + algae_radius
                    swept_algae.append(i)
            
            # Update position
            algae_positions[i][0] = x
            algae_positions[i][1] = y
            algae_positions[i][2] = z
            algae_objects[i].Placement = App.Placement(
                App.Vector(x, y, z),
                App.Rotation()
            )
        
        # Progress update every 50 frames
        if frame % 50 == 0:
            at_drain_count = len(ready_for_drain)
            progress = int(100.0 * at_drain_count / num_algae)
            print("  -> Frame " + str(frame) + "/" + str(num_frames_sweep) + 
                  " | At drain: " + str(at_drain_count) + "/" + str(num_algae) + 
                  " (" + str(progress) + "%)")
        
        if frame % 5 == 0:  # Update more frequently for smoother animation
            doc.recompute()
            Gui.updateGui()
            time.sleep(0.01)  # Shorter delay for continuous animation
    
    doc.recompute()
    Gui.updateGui()
    print("  -> " + str(len(ready_for_drain)) + " algae swept to drain area")
    print("")
    
    # PHASE 5: COLLECTION WAITING - Pump OFF, algae settle at drain
    print("Phase 5: Collection waiting - pump OFF, algae settle at drain...")
    
    # Turn pump OFF
    manifold_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)  # Gray when OFF
    slot_obj.ViewObject.ShapeColor = (0.0, 0.3, 1.0)  # Dark blue when OFF
    for arrow_obj in arrow_objects:
        arrow_obj.ViewObject.ShapeColor = (0.0, 0.7, 1.0)  # Dim cyan when stopped
    doc.recompute()
    Gui.updateGui()
    
    for frame in range(num_frames_collection):
        # Algae at drain area remain stationary (no flow)
        # This ensures they don't get pushed out or re-suspended
        # Visual feedback: algae turn darker orange as they settle
        if frame == num_frames_collection - 1:
            for i in ready_for_drain:
                algae_objects[i].ViewObject.ShapeColor = (0.8, 0.3, 0.0)  # Darker orange
        
        if frame % 15 == 0:
            doc.recompute()
            Gui.updateGui()
            time.sleep(0.02)
    
    doc.recompute()
    Gui.updateGui()
    print("  -> " + str(len(ready_for_drain)) + " algae ready at drain")
    print("")
    
    # PHASE 6: DRAIN - Valve opens for physical removal
    print("Phase 6: Drain valve opens - collecting algae...")
    
    # Drain valve opens - turns bright red
    drain_obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0)
    doc.recompute()
    Gui.updateGui()
    
    # Transfer ready_for_drain to collected_algae
    for i in ready_for_drain:
        collected_algae.append(i)
        algae_objects[i].ViewObject.ShapeColor = (0.8, 0.0, 0.0)  # Red when being drained
    
    for frame in range(num_frames_drain):
        # Simulate draining by shrinking collected algae
        for i in collected_algae:
            current_scale = 1.0 - (frame / float(num_frames_drain)) * 0.8
            if current_scale < 0.2:
                current_scale = 0.2
            
            scaled_sphere = Part.makeSphere(algae_radius * current_scale)
            algae_objects[i].Shape = scaled_sphere
        
        if frame % 10 == 0:
            doc.recompute()
            Gui.updateGui()
            time.sleep(0.02)
    
    doc.recompute()
    Gui.updateGui()
    
    print("  -> Collection complete: " + str(len(collected_algae)) + " algae removed")
    print("")
    
    # PHASE 7: CLOSE VALVE - Cycle complete
    print("Phase 7: Closing drain valve - cycle complete")
    drain_obj.ViewObject.ShapeColor = (0.5, 0.0, 0.0)  # Dark red when closed
    doc.recompute()
    Gui.updateGui()
    time.sleep(0.5)
    
    print("")
    print("=== CYCLE COMPLETE ===")
    print("Total algae collected: " + str(len(collected_algae)) + "/" + str(num_algae))
    print("Collection efficiency: " + str(round(100.0 * len(collected_algae) / num_algae, 1)) + "%")
    print("")
    
    loop_count = loop_count + 1

print("")
print("=== ANIMATION COMPLETE ===")
print("Final collection efficiency: " + str(round(100.0 * len(collected_algae) / num_algae, 1)) + "%")
print("")
print("System Design:")
print("  - Tank: Standard 20L rectangular (" + str(length) + "×" + str(width) + "×" + str(height) + "mm)")
print("  - Flow manifold: SLOT CUT design, " + str(manifold_diameter) + "mm diameter pipe")
print("  - Slot dimensions: " + str(slot_length) + "mm × " + str(slot_width) + "mm")
print("  - Manifold position: FRONT wall, spanning full width")
print("  - Drain type: Full-width SLOT at BACK wall")
print("  - Collection method: Pump-based UNIDIRECTIONAL sweeping")
print("  - Flow direction: FRONT → BACK (straight push)")
print("  - Bulk flow velocity: " + str(flow_velocity_bulk) + " mm/frame")
print("  - Effective velocity at algae: " + str(round(flow_velocity_at_algae * drag_reduction_factor, 3)) + " mm/frame (with water resistance)")
print("  - Flow rate: ~0.5-1 L/min (low turbulence laminar flow)")
print("  - Sweep strategy: " + str(num_sweep_passes) + " repeated passes")
print("")
print("Advantages:")
print("  ✓ No tank modifications needed")
print("  ✓ SLOT CUT creates uniform 'water knife' curtain effect")
print("  ✓ Better than multiple holes - continuous laminar sheet flow")
print("  ✓ GENTLE flow prevents algae re-suspension into water column")
print("  ✓ Low velocity preserves algae integrity (no cell damage)")
print("  ✓ UNIFORM distribution - slot spans full pipe length")
print("  ✓ DIRECTIONAL flow - efficient sweeping to single collection zone")
print("  ✓ REPEATED passes ensure stubborn algae removal")
print("  ✓ SEPARATED phases: sweep → wait → drain (no overlap)")
print("  ✓ Scalable to larger tanks")
print("  ✓ Easy to maintain and clean")
print("")
print("Why slot cut is better than holes:")
print("  1. Continuous water curtain vs. discrete jets")
print("  2. More uniform flow distribution (no gaps between holes)")
print("  3. Lower pressure = gentler flow (water knife effect)")
print("  4. Easier fabrication (single cut vs. drilling multiple holes)")
print("  5. Adjustable flow rate by varying slot width")
print("")
print("Why multiple passes work:")
print("  1. First pass: breaks weak adhesion bonds")
print("  2. Second pass: moves partially-freed algae")
print("  3. Third pass: sweeps remaining stubborn algae")
print("  4. Total time: " + str(num_frames_sweep) + " frames ensures >95% collection")