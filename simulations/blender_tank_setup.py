import bpy
import bmesh
import random

# ═══════════════════════════════════════════════════════════════
#  20L Algae Tank — Hydrocyclone Demo & Suspended Algae Flow
#  Technique: Mantaflow liquid + Volume Particles (Algae)
# ═══════════════════════════════════════════════════════════════

QUALITY_PRESET = "FAST_PREVIEW"  # Switch to "PPT_QUALITY" for final renders
TARGET_FPS = 30 
RESOLUTION = 64 if QUALITY_PRESET == "FAST_PREVIEW" else 128
END_FRAME = 250

# ── 20 Liters Exact Dimensions ($1L = 1000cm^3) ──────────────────
# Cube root of 20,000 cm^3 = 27.14 cm = 0.2714 m
TANK_X = 0.2714
TANK_Y = 0.2714
TANK_Z = 0.2714
WALL_THICKNESS = 0.005 # 5mm acrylic/glass
FILL_FRACTION = 0.85   # 85% full
DOMAIN_MARGIN = 0.05   # smaller margin for small scale

ALGAE_COUNT = 8000
ALGAE_SIZE = 0.002     # 2mm visual algae flecks

fill_height = TANK_Z * FILL_FRACTION

# ── Step 0: Clear the default scene ────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
for collection in [bpy.data.meshes, bpy.data.materials, bpy.data.particles]:
    for block in collection:
        if block.users == 0:
            collection.remove(block)

# ── Step 1: Create the 20L tank ────────────────────────────────
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, TANK_Z / 2))
tank = bpy.context.active_object
tank.name = "Tank_20L"
tank.scale = (TANK_X, TANK_Y, TANK_Z)
bpy.ops.object.transform_apply(scale=True)

# Open top
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(tank.data)
bm.faces.ensure_lookup_table()
top_face = max(bm.faces, key=lambda f: sum(v.co.z for v in f.verts) / len(f.verts))
bmesh.ops.delete(bm, geom=[top_face], context='FACES')
bmesh.update_edit_mesh(tank.data)
bpy.ops.object.mode_set(mode='OBJECT')

mod = tank.modifiers.new(name="Solidify", type='SOLIDIFY')
mod.thickness = WALL_THICKNESS
mod.offset = -1
bpy.ops.object.modifier_apply(modifier="Solidify")

# Glass Material
mat = bpy.data.materials.new(name="TankGlass")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.95, 1.0, 1.0)
bsdf.inputs["Alpha"].default_value = 0.05
bsdf.inputs["Roughness"].default_value = 0.01
mat.blend_method = 'BLEND'
tank.data.materials.append(mat)
tank.display_type = 'SOLID'

# ── Step 2: Create Fluid Domain ────────────────────────────────
domain_size = (TANK_X + DOMAIN_MARGIN, TANK_Y + DOMAIN_MARGIN, TANK_Z + DOMAIN_MARGIN)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, TANK_Z / 2))
domain = bpy.context.active_object
domain.name = "FluidDomain"
domain.scale = domain_size
bpy.ops.object.transform_apply(scale=True)

bpy.ops.object.modifier_add(type='FLUID')
ds = domain.modifiers["Fluid"].domain_settings
domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
ds.domain_type = 'LIQUID'
ds.resolution_max = RESOLUTION
ds.cache_frame_end = END_FRAME
ds.use_mesh = True
ds.mesh_particle_radius = 1.2
domain.display_type = 'WIRE'

# ── Step 3: Tank as Effector ──────────────────────────────────
bpy.context.view_layer.objects.active = tank
tank.select_set(True)
bpy.ops.object.modifier_add(type='FLUID')
tank.modifiers["Fluid"].fluid_type = 'EFFECTOR'
tank.modifiers["Fluid"].effector_settings.effector_type = 'COLLISION'

# ── Step 4: Water Volume ──────────────────────────────────────
inner = WALL_THICKNESS * 2
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, fill_height / 2))
water = bpy.context.active_object
water.name = "WaterVolume"
water.scale = (TANK_X - inner, TANK_Y - inner, fill_height)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.object.modifier_add(type='FLUID')
water.modifiers["Fluid"].fluid_type = 'FLOW'
flow = water.modifiers["Fluid"].flow_settings
flow.flow_type = 'LIQUID'
flow.flow_behavior = 'GEOMETRY'
water.display_type = 'WIRE'

# ── Step 5: Liquid Inflow (Pump to cause swirl) ───────────────
bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=0.02, location=(TANK_X/2.5, -TANK_Y/2.5, 0.05))
inflow = bpy.context.active_object
inflow.name = "PumpJet"
inflow.rotation_euler = (0, 1.57, 2.0) # Angle to create a vortex

bpy.ops.object.modifier_add(type='FLUID')
inflow.modifiers["Fluid"].fluid_type = 'FLOW'
inflow_flow = inflow.modifiers["Fluid"].flow_settings
inflow_flow.flow_type = 'LIQUID'
inflow_flow.flow_behavior = 'INFLOW'
inflow_flow.use_initial_velocity = True
inflow_flow.velocity_coord[0] = -0.5  # Push water to stir
inflow_flow.velocity_coord[1] = 0.5 

# ── Step 6: Algae Instance & Material ──────────────────────────
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, -5, 0))
algae_obj = bpy.context.active_object
algae_obj.name = "AlgaeCell"
bpy.ops.object.shade_smooth()
algae_obj.hide_render = True

algae_mat = bpy.data.materials.new(name="GreenAlgae")
algae_mat.use_nodes = True
bsdf_a = algae_mat.node_tree.nodes["Principled BSDF"]
bsdf_a.inputs["Base Color"].default_value = (0.01, 0.6, 0.1, 1.0) # Bright green
algae_obj.data.materials.append(algae_mat)

# ── Step 7: Algae Emitter (Random Volume spread) ───────────────
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, fill_height / 2))
emitter = bpy.context.active_object
emitter.name = "AlgaeEmitter"
emitter.scale = (TANK_X * 0.8, TANK_Y * 0.8, fill_height * 0.8)
bpy.ops.object.transform_apply(scale=True)
emitter.display_type = 'BOUNDS'
emitter.hide_render = True

# ── Step 8: Algae Particle System ──────────────────────────────
bpy.ops.object.modifier_add(type='PARTICLE_SYSTEM')
ps = emitter.modifiers[-1].particle_system.settings
ps.count = ALGAE_COUNT
ps.frame_start = 1
ps.frame_end = 1          # Emit everything at once
ps.lifetime = 1000        # Lasts the whole simulation
ps.emit_from = 'VOLUME'
ps.distribution = 'RAND'  # Random starting point

# Buoyancy: Neutral (moves with water, doesn't sink immediately)
ps.effector_weights.gravity = 0.05 
ps.physics_type = 'NEWTON'
ps.drag_factor = 0.8
ps.mass = 0.001

ps.render_type = 'OBJECT'
ps.instance_object = algae_obj
ps.particle_size = ALGAE_SIZE
ps.size_random = 0.4

# Add Force Field to make particles follow Mantaflow water
bpy.ops.object.effector_add(type='FLUID_FLOW', location=(0,0,0))
fluid_force = bpy.context.active_object
fluid_force.modifiers.new(name="Field", type='FLUID')

# ── Step 9: Camera and Lighting for Small scale ────────────────
bpy.ops.object.camera_add(location=(0.4, -0.55, 0.35))
cam = bpy.context.active_object
cam.rotation_euler = (1.1, 0.0, 0.6)
bpy.context.scene.camera = cam

bpy.ops.object.light_add(type='AREA', location=(0.3, -0.3, 0.6))
light = bpy.context.active_object
light.data.energy = 15
light.data.size = 0.4
light.rotation_euler = (0, 0.4, 0.8)

# Render specifics
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.fps = TARGET_FPS
scene.cycles.samples = 64

print("✅ Setup Complete: 20L Tank generated. Algae particles injected into Mantaflow flow.")
# [finished]
