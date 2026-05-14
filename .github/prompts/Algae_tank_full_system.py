import FreeCAD as App
import Part

def create_full_system_cfd_domain():
    doc = App.newDocument("Algae_Tank_Full_System")

    # ==========================================
    # 1. PARAMETERS (in mm)
    # ==========================================
    # Tank Parameters
    neck_r = 55.0 / 2.0
    neck_h = 50.0
    shoulder_h = 80.0
    main_r = 270.0 / 2.0
    main_h = 300.0
    
    # Aeration Ring Parameters
    ring_major_r = 75.0
    ring_minor_r = 6.0
    ring_z_height = neck_h + 40.0
    
    # Valve Parameters
    valve_r = neck_r
    valve_h = 60.0
    
    # Hydrocyclone Parameters
    cylindrical_section_r = 60.0
    cylindrical_section_h = 100.0
    conical_section_h = 150.0
    underflow_r = 10.0          # The bottom tip (apex) where algae drops out
    feed_inlet_r = 15.0         # Tangential side pipe
    feed_inlet_length = 100.0

    # ==========================================
    # 2. BUILD THE TANK (Z = 0 and going UP)
    # ==========================================
    tank_neck = Part.makeCylinder(neck_r, neck_h)
    tank_shoulder = Part.makeCone(neck_r, main_r, shoulder_h, App.Vector(0, 0, neck_h), App.Vector(0, 0, 1))
    tank_main = Part.makeCylinder(main_r, main_h, App.Vector(0, 0, neck_h + shoulder_h), App.Vector(0, 0, 1))
    
    fluid_domain = tank_neck.fuse(tank_shoulder).fuse(tank_main)

    # 3. Cut out the Aeration Ring
    feed_pipe_h = (neck_h + shoulder_h + main_h) - ring_z_height + 10.0
    ring = Part.makeTorus(ring_major_r, ring_minor_r, App.Vector(0, 0, ring_z_height), App.Vector(0, 0, 1))
    feed_pipe = Part.makeCylinder(ring_minor_r, feed_pipe_h, App.Vector(ring_major_r, 0, ring_z_height), App.Vector(0, 0, 1))
    aeration_hardware = ring.fuse(feed_pipe)
    
    fluid_domain = fluid_domain.cut(aeration_hardware)

    # ==========================================
    # 4. BUILD THE VALVE (Z = 0 going DOWN)
    # ==========================================
    # Starts at Z=0 and goes down to Z= -60
    z_valve_bottom = -valve_h
    valve_body = Part.makeCylinder(valve_r, valve_h, App.Vector(0, 0, z_valve_bottom), App.Vector(0, 0, 1))
    
    fluid_domain = fluid_domain.fuse(valve_body)

    # ==========================================
    # 5. BUILD THE HYDROCYCLONE (Going further down)
    # ==========================================
    z_cylindrical_bottom = z_valve_bottom - cylindrical_section_h
    z_conical_bottom = z_cylindrical_bottom - conical_section_h

    # Cylindrical section (Swirl Chamber)
    cylindrical_section = Part.makeCylinder(cylindrical_section_r, cylindrical_section_h, App.Vector(0, 0, z_cylindrical_bottom), App.Vector(0, 0, 1))
    
    # Conical section
    conical_section = Part.makeCone(cylindrical_section_r, underflow_r, conical_section_h, App.Vector(0, 0, z_cylindrical_bottom), App.Vector(0, 0, -1))
    
    # Feed inlet (Tangential pipe) shooting out along the X-axis
    tangential_offset_y = cylindrical_section_r - feed_inlet_r  # Offset to make it tangential
    feed_inlet = Part.makeCylinder(feed_inlet_r, feed_inlet_length, 
                                        App.Vector(0, tangential_offset_y, z_valve_bottom - 30.0), 
                                        App.Vector(1, 0, 0)) # Pointing in +X direction
    
    # Fuse cyclone parts to the main domain
    fluid_domain = fluid_domain.fuse(cylindrical_section).fuse(conical_section).fuse(feed_inlet)

    # ==========================================
    # 5.5 BUILD VORTEX FINDER (The Overflow pipe)
    # ==========================================
    # The clean water goes UP through this pipe (Overflow)
    overflow_outer_r = 20.0
    overflow_inner_r = 16.0  # 4mm thick wall
    overflow_length = 50.0
    
    # The Overflow pipe hangs down from the roof (z_valve_bottom)
    z_vf_bottom = z_valve_bottom - overflow_length
    vf_outer = Part.makeCylinder(overflow_outer_r, overflow_length, App.Vector(0, 0, z_vf_bottom), App.Vector(0, 0, 1))
    vf_inner = Part.makeCylinder(overflow_inner_r, overflow_length, App.Vector(0, 0, z_vf_bottom), App.Vector(0, 0, 1))
    overflow_wall_hardware = vf_outer.cut(vf_inner)
    
    # Cut this physical pipe out of our solid water block
    fluid_domain = fluid_domain.cut(overflow_wall_hardware)

    # ==========================================
    # 6. CLEANUP & EXPORT
    # ==========================================
    fluid_domain = fluid_domain.removeSplitter()

    cfd_part = doc.addObject("Part::Feature", "FluidVolume")
    cfd_part.Shape = fluid_domain
    cfd_part.Label = "Fluid_Domain_Full_System"

    doc.recompute()
    
    try:
        import FreeCADGui
        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.activeDocument().activeView().viewAxometric()
    except Exception as e:
        pass

create_full_system_cfd_domain()
print("Full System Model successfully generated!")