import os
import sys

try:
    import FreeCAD as App
    import Part
except Exception as exc:
    raise SystemExit("Run this with FreeCAD or freecadcmd. FreeCAD modules not found.") from exc


def create_full_system_cfd_domain():
    doc = App.newDocument("Algae_Tank_Full_System_V3_Pump")

    # Tank parameters (mm)
    neck_r = 55.0 / 2.0
    neck_h = 50.0
    shoulder_h = 80.0
    main_r = 270.0 / 2.0
    main_h = 300.0

    # Aeration ring
    ring_major_r = 75.0
    ring_minor_r = 6.0
    ring_z_height = neck_h + 40.0

    # Valve and connection
    valve_r = neck_r
    valve_h = 60.0
    cyclone_offset_x = 150.0

    # Hydrocyclone
    cylindrical_section_r = 60.0
    cylindrical_section_h = 100.0
    conical_section_h = 150.0
    underflow_r = 10.0
    feed_inlet_r = 15.0

    cyclone_offset_y = -(cylindrical_section_r - feed_inlet_r)

    # Tank (Z=0 upward)
    tank_neck = Part.makeCylinder(neck_r, neck_h)
    tank_shoulder = Part.makeCone(
        neck_r,
        main_r,
        shoulder_h,
        App.Vector(0, 0, neck_h),
        App.Vector(0, 0, 1),
    )
    tank_main = Part.makeCylinder(
        main_r,
        main_h,
        App.Vector(0, 0, neck_h + shoulder_h),
        App.Vector(0, 0, 1),
    )

    fluid_domain = tank_neck.fuse(tank_shoulder).fuse(tank_main)

    # Cut aeration ring
    feed_pipe_h = (neck_h + shoulder_h + main_h) - ring_z_height + 10.0
    ring = Part.makeTorus(
        ring_major_r, ring_minor_r, App.Vector(0, 0, ring_z_height), App.Vector(0, 0, 1)
    )
    feed_pipe = Part.makeCylinder(
        ring_minor_r,
        feed_pipe_h,
        App.Vector(ring_major_r, 0, ring_z_height),
        App.Vector(0, 0, 1),
    )
    aeration_hardware = ring.fuse(feed_pipe)
    fluid_domain = fluid_domain.cut(aeration_hardware)

    # Valve and pump train
    z_valve_bottom = -valve_h
    valve_body = Part.makeCylinder(
        valve_r, valve_h, App.Vector(0, 0, z_valve_bottom), App.Vector(0, 0, 1)
    )
    fluid_domain = fluid_domain.fuse(valve_body)

    base_z = z_valve_bottom + 20.0
    suction_pipe = Part.makeCylinder(
        feed_inlet_r, 35.0, App.Vector(0, 0, base_z), App.Vector(1, 0, 0)
    )
    pump_chamber = Part.makeCylinder(
        25.0, 45.0, App.Vector(30.0, 0, base_z), App.Vector(1, 0, 0)
    )
    check_valve = Part.makeCylinder(
        18.0, 35.0, App.Vector(70.0, 0, base_z), App.Vector(1, 0, 0)
    )
    discharge_pipe = Part.makeCylinder(
        feed_inlet_r, 60.0, App.Vector(100.0, 0, base_z), App.Vector(1, 0, 0)
    )

    fluid_domain = (
        fluid_domain.fuse(suction_pipe)
        .fuse(pump_chamber)
        .fuse(check_valve)
        .fuse(discharge_pipe)
    )

    # Hydrocyclone
    z_cyclone_top = z_valve_bottom + 40.0
    z_cylindrical_bottom = z_cyclone_top - cylindrical_section_h

    cylindrical_section = Part.makeCylinder(
        cylindrical_section_r,
        cylindrical_section_h,
        App.Vector(cyclone_offset_x, cyclone_offset_y, z_cylindrical_bottom),
        App.Vector(0, 0, 1),
    )
    conical_section = Part.makeCone(
        cylindrical_section_r,
        underflow_r,
        conical_section_h,
        App.Vector(cyclone_offset_x, cyclone_offset_y, z_cylindrical_bottom),
        App.Vector(0, 0, -1),
    )
    fluid_domain = fluid_domain.fuse(cylindrical_section).fuse(conical_section)

    # Vortex finder (overflow)
    overflow_outer_r = 20.0
    overflow_inner_r = 16.0
    overflow_length = 80.0

    z_vf_bottom = z_cyclone_top - 40.0
    vf_outer = Part.makeCylinder(
        overflow_outer_r,
        overflow_length,
        App.Vector(cyclone_offset_x, cyclone_offset_y, z_vf_bottom),
        App.Vector(0, 0, 1),
    )
    vf_inner = Part.makeCylinder(
        overflow_inner_r,
        overflow_length,
        App.Vector(cyclone_offset_x, cyclone_offset_y, z_vf_bottom),
        App.Vector(0, 0, 1),
    )
    overflow_wall_hardware = vf_outer.cut(vf_inner)
    fluid_domain = fluid_domain.cut(overflow_wall_hardware)

    fluid_domain = fluid_domain.removeSplitter()

    cfd_part = doc.addObject("Part::Feature", "FluidVolume")
    cfd_part.Shape = fluid_domain
    cfd_part.Label = "Fluid_Domain_Harvesting_Ready_Pumped"

    doc.recompute()
    return doc, cfd_part


def _set_first_property(obj, name_candidates, value):
    for name in name_candidates:
        if hasattr(obj, name):
            setattr(obj, name, value)
            return True
    return False


def _add_to_group(group_obj, child_obj):
    if hasattr(group_obj, "addObject"):
        group_obj.addObject(child_obj)
        return
    if hasattr(group_obj, "Group"):
        group_obj.Group = list(group_obj.Group) + [child_obj]


def setup_cfdof_analysis(doc, fluid_obj):
    try:
        from CfdOF import CfdOFObjects as CfdObjects
    except Exception:
        try:
            from Cfd import CfdObjects  # fallback for older installs
        except Exception as exc:
            raise SystemExit(
                "CfdOF workbench not found. Install CfdOF in FreeCAD and retry."
            ) from exc

    analysis = CfdObjects.makeCfdAnalysis(doc)

    # Mesh
    mesh_obj = CfdObjects.makeCfdMesh(doc, analysis)
    _set_first_property(mesh_obj, ["Part", "Geometry", "LinkedObject"], fluid_obj)
    _set_first_property(mesh_obj, ["Feature", "Shape"], fluid_obj.Shape)

    # Solver
    if hasattr(CfdObjects, "makeCfdSolverFoam"):
        solver_obj = CfdObjects.makeCfdSolverFoam(doc, analysis)
    else:
        solver_obj = CfdObjects.makeCfdSolver(doc, analysis)

    _set_first_property(solver_obj, ["Solver", "SolverType"], "simpleFoam")
    _set_first_property(solver_obj, ["SteadyState"], True)

    # Material (water)
    if hasattr(CfdObjects, "makeCfdFluidMaterial"):
        mat_obj = CfdObjects.makeCfdFluidMaterial(doc, analysis)
    else:
        mat_obj = CfdObjects.makeCfdMaterial(doc, analysis)

    _set_first_property(mat_obj, ["Density"], 1000.0)
    _set_first_property(mat_obj, ["KinematicViscosity"], 1.0e-6)

    # Attach to analysis group
    for obj in [fluid_obj, mesh_obj, solver_obj, mat_obj]:
        _add_to_group(analysis, obj)

    doc.recompute()
    return analysis


def main():
    doc, fluid_obj = create_full_system_cfd_domain()
    setup_cfdof_analysis(doc, fluid_obj)

    # Optional GUI view handling
    try:
        import FreeCADGui

        FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.activeDocument().activeView().viewAxometric()
    except Exception:
        pass

    print("CfdOF analysis setup completed. Review mesh settings and BCs in FreeCAD.")


if __name__ == "__main__":
    main()
