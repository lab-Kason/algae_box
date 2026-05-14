import FreeCAD as App
import Part

def create_aerated_cfd_tank():
    # 1. Create a new document
    doc = App.newDocument("Algae_Tank_Aerated")

    # 2. Define Tank Parameters (in mm)
    neck_diameter = 55.0
    neck_r = neck_diameter / 2.0
    neck_h = 50.0

    main_diameter = 270.0
    main_r = main_diameter / 2.0
    main_h = 300.0

    shoulder_h = 80.0

    # 3. Build Main Tank Fluid Volume (Solid Water Block)
    neck = Part.makeCylinder(neck_r, neck_h)
    shoulder_cone = Part.makeCone(neck_r, main_r, shoulder_h, App.Vector(0, 0, neck_h), App.Vector(0, 0, 1))
    main_body = Part.makeCylinder(main_r, main_h, App.Vector(0, 0, neck_h + shoulder_h), App.Vector(0, 0, 1))
    
    # Fuse them into one solid block of water
    raw_fluid = neck.fuse(shoulder_cone).fuse(main_body)

    # 4. Define Aeration Hardware Structure
    # Place the ring roughly halfway up the conical shoulder
    ring_major_r = 75.0   # How wide the literal ring is
    ring_minor_r = 6.0    # The thickness of the diffuser tube (12mm total pipe diameter)
    ring_z_height = neck_h + 40.0  # Placed halfway up the 80mm height of the shoulder
    
    # Vertical feed tube (connects from outside down to the ring)
    # We offset it by `ring_major_r` so it connects to the edge of the ring
    feed_pipe_z_start = ring_z_height
    feed_pipe_h = (neck_h + shoulder_h + main_h) - feed_pipe_z_start + 10.0 # Extends slightly past top of tank
    
    # 5. Build Aeration Solid Forms
    # makeTorus( major_radius, minor_radius, center_point, direction_vector )
    ring = Part.makeTorus(ring_major_r, ring_minor_r, App.Vector(0, 0, ring_z_height), App.Vector(0, 0, 1))
    feed_pipe = Part.makeCylinder(6.0, feed_pipe_h, App.Vector(ring_major_r, 0, feed_pipe_z_start), App.Vector(0, 0, 1))
    
    # Combine the ring and pipe into one piece of hardware
    aeration_hardware = ring.fuse(feed_pipe)
    
    # 6. MAKE THE CFD DOMAIN: Cut the hardware *out* of the water
    final_fluid_domain = raw_fluid.cut(aeration_hardware)
    final_fluid_domain = final_fluid_domain.removeSplitter()

    # 7. Add to Document
    cfd_part = doc.addObject("Part::Feature", "FluidVolume")
    cfd_part.Shape = final_fluid_domain
    cfd_part.Label = "Fluid_Domain_15L_Aerated"

    doc.recompute()
    
    # Switch view to center the model (Requires GUI)
    try:
        import FreeCADGui
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.activeDocument().activeView().viewAxometric()
    except Exception as e:
        pass

create_aerated_cfd_tank()
print("Aerated Model successfully generated! The ring has been SUBTRACTED from the fluid domain.")