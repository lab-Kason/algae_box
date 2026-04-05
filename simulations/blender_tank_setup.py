import bpy
import bmesh

# ═══════════════════════════════════════════════════════════════
#  Algae Tank — Fluid Simulation + Air Bubble Particles
#  Technique: Mantaflow liquid + Particle System bubbles
#  (inspired by blenderian's "Air Bubbles in Liquid" tutorial)
# ═══════════════════════════════════════════════════════════════

# ── Settings ────────────────────────────────────────────────────
QUALITY_PRESET = "PPT_QUALITY"  # "FAST_PREVIEW" or "PPT_QUALITY"
DISPLAY_MODE = "MECHANISM"      # "REALISTIC" or "MECHANISM" (mechanism = colored bubbles)
BASE_FPS = 24
TARGET_FPS = 30  # higher fps for smoother playback/recording

if QUALITY_PRESET == "FAST_PREVIEW":
    RESOLUTION = 56
    END_FRAME = 180
    BUBBLE_COUNT = 600
    BUBBLE_LIFETIME = 70
    RENDER_RES_X = 1280
    RENDER_RES_Y = 720
    RENDER_SAMPLES = 96
else:  # PPT_QUALITY
    RESOLUTION = 96
    END_FRAME = 260
    BUBBLE_COUNT = 1800
    BUBBLE_LIFETIME = 95
    RENDER_RES_X = 1920
    RENDER_RES_Y = 1080
    RENDER_SAMPLES = 256

# Re-time to target FPS while keeping approximately the same duration
duration_seconds = END_FRAME / BASE_FPS
END_FRAME = int(round(duration_seconds * TARGET_FPS))
BUBBLE_LIFETIME = int(round(BUBBLE_LIFETIME * TARGET_FPS / BASE_FPS))

TANK_X = 2.0          # tank length (m)
TANK_Y = 2.0          # tank width  (m)
TANK_Z = 0.5          # tank height (m)
WALL_THICKNESS = 0.02 # 2 cm walls
FILL_FRACTION = 0.85  # 85 % water fill
DOMAIN_MARGIN = 0.3   # extra space around tank for domain

# Air tube settings
TUBE_RADIUS = 0.03          # tube outer radius (3 cm)
TUBE_WALL = 0.005           # tube wall thickness
TUBE_X = -0.6               # tube X position (off-centre)
TUBE_Y = 0.0                # tube Y position (centre)
TUBE_BOTTOM_Z = 0.04        # tube exit height from bottom
TUBE_TOP_Z = 0.7            # tube top (above tank, where pump is)

# Bubble settings
BUBBLE_SIZE_MIN = 0.008      # smallest bubble radius
BUBBLE_SIZE_MAX = 0.025      # largest bubble radius
BUBBLE_VELOCITY_Z = 0.4      # upward velocity (m/frame-unit)
BUBBLE_RANDOM = 0.3          # lateral randomness

fill_height = TANK_Z * FILL_FRACTION  # 0.425 m

# ── Step 0: Clear the default scene ────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
# Also purge orphan data
for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)
print("Cleared scene")

# ── Step 1: Create the tank (open-top box with walls) ──────────
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, TANK_Z / 2))
tank = bpy.context.active_object
tank.name = "Tank"
tank.scale = (TANK_X, TANK_Y, TANK_Z)
bpy.ops.object.transform_apply(scale=True)

# Delete the top face for open-top tank
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(tank.data)
bm.faces.ensure_lookup_table()
top_face = max(bm.faces, key=lambda f: sum(v.co.z for v in f.verts) / len(f.verts))
bmesh.ops.delete(bm, geom=[top_face], context='FACES')
bmesh.update_edit_mesh(tank.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Solidify for wall thickness
mod = tank.modifiers.new(name="Solidify", type='SOLIDIFY')
mod.thickness = WALL_THICKNESS
mod.offset = -1
bpy.ops.object.modifier_apply(modifier="Solidify")

# Tank glass material (very transparent)
mat = bpy.data.materials.new(name="TankGlass")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.95, 1.0, 1.0)
bsdf.inputs["Alpha"].default_value = 0.04
bsdf.inputs["Roughness"].default_value = 0.01
if hasattr(bsdf.inputs, "Transmission"):
    bsdf.inputs["Transmission"].default_value = 1.0
elif "Transmission Weight" in bsdf.inputs:
    bsdf.inputs["Transmission Weight"].default_value = 1.0
mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else None
tank.data.materials.append(mat)
tank.display_type = 'SOLID'

# Add particle collision so bubbles don't pass through walls/bottom
bpy.context.view_layer.objects.active = tank
tank.select_set(True)
bpy.ops.object.modifier_add(type='COLLISION')
coll = tank.collision
coll.thickness_outer = 0.02  # enlarge collision shell to stop particle tunneling
coll.damping_factor = 0.4
coll.friction_factor = 0.1
coll.permeability = 0.0
print(f"Created Tank: {TANK_X}x{TANK_Y}x{TANK_Z}m, wall={WALL_THICKNESS}m")

# ── Step 2: Create Fluid Domain ────────────────────────────────
domain_size = (
    TANK_X + DOMAIN_MARGIN * 2,
    TANK_Y + DOMAIN_MARGIN * 2,
    TANK_Z + DOMAIN_MARGIN * 2,
)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, TANK_Z / 2))
domain = bpy.context.active_object
domain.name = "FluidDomain"
domain.scale = domain_size
bpy.ops.object.transform_apply(scale=True)

bpy.ops.object.modifier_add(type='FLUID')
domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
ds = domain.modifiers["Fluid"].domain_settings
ds.domain_type = 'LIQUID'
ds.resolution_max = RESOLUTION
ds.use_adaptive_timesteps = True
ds.cache_frame_end = END_FRAME
ds.use_collision_border_back = True
ds.use_collision_border_front = True
ds.use_collision_border_left = True
ds.use_collision_border_right = True
ds.use_collision_border_bottom = True
ds.use_collision_border_top = False  # open top

# Enable meshing so the liquid is a continuous surface (not particles)
ds.use_mesh = True
ds.mesh_particle_radius = 1.5

domain.display_type = 'WIRE'
print(f"Created FluidDomain: {domain_size}")

# ── Step 3: Set tank as Effector (collision walls) ─────────────
bpy.context.view_layer.objects.active = tank
tank.select_set(True)
bpy.ops.object.modifier_add(type='FLUID')
tank.modifiers["Fluid"].fluid_type = 'EFFECTOR'
eff = tank.modifiers["Fluid"].effector_settings
eff.effector_type = 'COLLISION'
print("Tank set as Effector (collision walls)")

# ── Step 4: Create water fill volume (85%) ─────────────────────
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

# Water material (extra transparent)
water_mat = bpy.data.materials.new(name="Water")
water_mat.use_nodes = True
bsdf_w = water_mat.node_tree.nodes["Principled BSDF"]
bsdf_w.inputs["Base Color"].default_value = (0.03, 0.15, 0.25, 1.0)
bsdf_w.inputs["Alpha"].default_value = 0.04
bsdf_w.inputs["Roughness"].default_value = 0.0
if hasattr(bsdf_w.inputs, "Transmission"):
    bsdf_w.inputs["Transmission"].default_value = 1.0
elif "Transmission Weight" in bsdf_w.inputs:
    bsdf_w.inputs["Transmission Weight"].default_value = 1.0
if "IOR" in bsdf_w.inputs:
    bsdf_w.inputs["IOR"].default_value = 1.333
water_mat.blend_method = 'BLEND' if hasattr(water_mat, 'blend_method') else None
water.data.materials.append(water_mat)
water.display_type = 'WIRE'
water.hide_render = True
print(f"Created WaterVolume: 85% fill, height={fill_height}m")

# ── Step 5: Create the air tube ────────────────────────────────
# Vertical tube going from above the tank down to near the bottom
tube_length = TUBE_TOP_Z - TUBE_BOTTOM_Z
tube_centre_z = (TUBE_TOP_Z + TUBE_BOTTOM_Z) / 2

bpy.ops.mesh.primitive_cylinder_add(
    radius=TUBE_RADIUS,
    depth=tube_length,
    location=(TUBE_X, TUBE_Y, tube_centre_z),
    vertices=16,
)
tube = bpy.context.active_object
tube.name = "AirTube"

# Remove end caps to make the tube hollow (open top and bottom)
bpy.ops.object.mode_set(mode='EDIT')
bm_tube = bmesh.from_edit_mesh(tube.data)
bm_tube.faces.ensure_lookup_table()
caps = [f for f in bm_tube.faces if abs(f.normal.z) > 0.9]
bmesh.ops.delete(bm_tube, geom=caps, context='FACES')
bmesh.update_edit_mesh(tube.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Hollow out the tube with Solidify
tube_solid = tube.modifiers.new(name="Solidify", type='SOLIDIFY')
tube_solid.thickness = TUBE_WALL
tube_solid.offset = -1
bpy.ops.object.modifier_apply(modifier="Solidify")

# Tube material (semi-transparent silicone look)
tube_mat = bpy.data.materials.new(name="TubeSilicone")
tube_mat.use_nodes = True
bsdf_t = tube_mat.node_tree.nodes["Principled BSDF"]
bsdf_t.inputs["Base Color"].default_value = (0.7, 0.7, 0.75, 1.0)
bsdf_t.inputs["Alpha"].default_value = 0.4
bsdf_t.inputs["Roughness"].default_value = 0.3
tube_mat.blend_method = 'BLEND' if hasattr(tube_mat, 'blend_method') else None
tube.data.materials.append(tube_mat)

# Also set tube as fluid effector so water doesn't pass through it
bpy.context.view_layer.objects.active = tube
tube.select_set(True)
bpy.ops.object.modifier_add(type='FLUID')
tube.modifiers["Fluid"].fluid_type = 'EFFECTOR'
tube_eff = tube.modifiers["Fluid"].effector_settings
tube_eff.effector_type = 'COLLISION'
# Add particle collision to tube to stop particles passing through
bpy.ops.object.modifier_add(type='COLLISION')
tube_coll = tube.collision
tube_coll.thickness_outer = 0.02
tube_coll.damping_factor = 0.4
tube_coll.friction_factor = 0.1
tube_coll.permeability = 0.0
print(f"Created AirTube at x={TUBE_X}, bottom z={TUBE_BOTTOM_Z}")

# ── Step 6: Create bubble instance object (small UV sphere) ───
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.01,   # base radius (scaled by particle size)
    segments=12,
    ring_count=8,
    location=(10, 10, 10),  # hide far away — only used as instance
)
bubble_obj = bpy.context.active_object
bubble_obj.name = "BubbleSphere"

# Smooth shading
bpy.ops.object.shade_smooth()

# Bubble material — switchable color for mechanism view
bubble_mat = bpy.data.materials.new(name="BubbleMat")
bubble_mat.use_nodes = True
nodes = bubble_mat.node_tree.nodes
links = bubble_mat.node_tree.links

for n in nodes:
    nodes.remove(n)

output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)

mix_shader = nodes.new('ShaderNodeMixShader')
mix_shader.location = (200, 0)
mix_shader.inputs[0].default_value = 0.12

transp = nodes.new('ShaderNodeBsdfTransparent')
transp.location = (0, 100)
transp.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)

glass = nodes.new('ShaderNodeBsdfGlass')
glass.location = (0, -120)
if DISPLAY_MODE == "MECHANISM":
    glass.inputs["Color"].default_value = (1.0, 0.2, 0.1, 1.0)  # orange-red highlight
else:
    glass.inputs["Color"].default_value = (0.95, 0.97, 1.0, 1.0)  # neutral
glass.inputs["Roughness"].default_value = 0.03
glass.inputs["IOR"].default_value = 1.05

links.new(transp.outputs[0], mix_shader.inputs[1])
links.new(glass.outputs[0], mix_shader.inputs[2])
links.new(mix_shader.outputs[0], output.inputs[0])

bubble_mat.blend_method = 'BLEND' if hasattr(bubble_mat, 'blend_method') else None
bubble_obj.data.materials.append(bubble_mat)

# Hide the template from render (only instances are visible)
bubble_obj.hide_render = True
bubble_obj.hide_viewport = False
print("Created BubbleSphere instance object with glass material")

# ── Step 7: Create bubble emitter (small disc at tube exit) ───
bpy.ops.mesh.primitive_circle_add(
    radius=TUBE_RADIUS * 0.6,  # emitter fits inside tube
    vertices=12,
    fill_type='NGON',
    location=(TUBE_X, TUBE_Y, TUBE_BOTTOM_Z + 0.01),
)
emitter = bpy.context.active_object
emitter.name = "BubbleEmitter"
emitter.hide_render = True

# ── Step 8: Add particle system to emitter ─────────────────────
bpy.context.view_layer.objects.active = emitter
emitter.select_set(True)

ps_mod = emitter.modifiers.new(name="BubbleParticles", type='PARTICLE_SYSTEM')
ps = ps_mod.particle_system
psettings = ps.settings

# Emission
psettings.count = BUBBLE_COUNT
psettings.frame_start = 1
psettings.frame_end = END_FRAME
psettings.lifetime = BUBBLE_LIFETIME
psettings.lifetime_random = 0.3      # ±30% lifetime variation
psettings.emit_from = 'FACE'

# Velocity — upward from face normal + random
psettings.normal_factor = BUBBLE_VELOCITY_Z      # upward (disc faces +Z)
psettings.tangent_factor = 0.0
psettings.object_align_factor[2] = 0.0
psettings.factor_random = BUBBLE_RANDOM           # lateral scatter

# Physics
psettings.physics_type = 'NEWTON'
psettings.mass = 0.001               # very light (air)
psettings.use_multiply_size_mass = False
psettings.drag_factor = 0.3          # water drag slows lateral motion
psettings.brownian_factor = 0.02     # subtle wobble

# Gravity override: bubbles rise, so we use negative gravity effect
# Blender particles fall with scene gravity by default.
# We set effector weight gravity to negative so they float UP.
psettings.effector_weights.gravity = -1.0  # stronger buoyancy

# Size
mid_radius = (BUBBLE_SIZE_MIN + BUBBLE_SIZE_MAX) / 2.0
size_random = (BUBBLE_SIZE_MAX - BUBBLE_SIZE_MIN) / (BUBBLE_SIZE_MAX + BUBBLE_SIZE_MIN)
psettings.particle_size = max(0.001, mid_radius / 0.01)
psettings.size_random = min(1.0, max(0.0, size_random))
psettings.use_size_deflect = True  # respect particle radius when colliding

# Render as instanced object (the BubbleSphere)
psettings.render_type = 'OBJECT'
psettings.instance_object = bubble_obj

# Display in viewport
psettings.display_method = 'RENDER'
psettings.display_size = 0.01

print(f"Created BubbleEmitter with {BUBBLE_COUNT} particles, lifetime={BUBBLE_LIFETIME}f")

# ── Step 9: Add a small upward inflow at tube exit ────────────
# This creates a gentle upward current in the Mantaflow water
# where the bubbles come out (visual turbulence)
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(TUBE_X, TUBE_Y, TUBE_BOTTOM_Z + 0.03),
)
inflow = bpy.context.active_object
inflow.name = "AirInflow"
inflow.scale = (TUBE_RADIUS * 1.5, TUBE_RADIUS * 1.5, 0.02)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.object.modifier_add(type='FLUID')
inflow.modifiers["Fluid"].fluid_type = 'FLOW'
inflow_flow = inflow.modifiers["Fluid"].flow_settings
inflow_flow.flow_type = 'LIQUID'
inflow_flow.flow_behavior = 'INFLOW'
inflow_flow.use_initial_velocity = True
inflow_flow.velocity_coord[2] = 1.2   # upward jet velocity (gentler for cleaner motion)
inflow_flow.velocity_coord[0] = 0.0
inflow_flow.velocity_coord[1] = 0.0

inflow.display_type = 'WIRE'
inflow.hide_render = True

# Keyframe the inflow to pulse (on/off) for realistic effect
# ON for frames 1-20, OFF for 21-30, ON for 31-50, etc. (pulsing pump)
inflow_flow.keyframe_insert(data_path="use_inflow", frame=1)

print("Created AirInflow (upward liquid jet at tube exit)")

# ── Step 10: Set up camera and lighting ────────────────────────
# Camera — angled to see inside the tank
bpy.ops.object.camera_add(location=(3.5, -3.5, 1.8))
cam = bpy.context.active_object
cam.name = "Camera"
cam.rotation_euler = (1.1, 0, 0.78)
bpy.context.scene.camera = cam
cam.data.lens = 45  # less distortion, cleaner for slides

# Key light (sun)
bpy.ops.object.light_add(type='SUN', location=(2, -2, 5))
light = bpy.context.active_object
light.name = "Sun"
light.data.energy = 2.2
light.rotation_euler = (0.5, 0.2, 0)

# Fill light (area light behind camera for softer look)
bpy.ops.object.light_add(type='AREA', location=(-2, 3, 2))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 120
fill.data.size = 3

# Rim light to highlight bubbles and tube edges
bpy.ops.object.light_add(type='AREA', location=(2.0, 2.0, 1.2))
rim = bpy.context.active_object
rim.name = "RimLight"
rim.data.energy = 90
rim.data.size = 2.0
rim.rotation_euler = (1.2, 0.0, -2.4)

# ── Step 11: Render settings ──────────────────────────────────
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = END_FRAME

# Render setup for presentation quality
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = RENDER_RES_X
scene.render.resolution_y = RENDER_RES_Y
scene.render.fps = TARGET_FPS

scene.cycles.samples = RENDER_SAMPLES
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
scene.render.film_transparent = False

# Better world contrast for readable bubbles in PPT
world = scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wlinks = world.node_tree.links
bg = wnodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.02, 0.03, 0.05, 1.0)
    bg.inputs[1].default_value = 0.7

# Optional depth of field for cinematic slide look
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 3.2
cam.data.dof.aperture_fstop = 4.0

# ── Done — select domain and auto-bake fluid ──────────────────
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active = domain
domain.select_set(True)

print("\n" + "=" * 60)
print("✓ SETUP COMPLETE")
print("  Tank + Water + Air Tube + Bubble Particles + Inflow")
print(f"  Preset: {QUALITY_PRESET}")
print("  Now baking Mantaflow fluid simulation...")
print("=" * 60)

# Bake the fluid simulation (bubbles are particle-based, no bake needed)
bpy.ops.fluid.bake_all()

print("\n✓ BAKE COMPLETE!")
print("  Press Space to play the animation")
print("  Bubbles (particles) animate automatically — no bake needed")
print("  Save as .blend to keep your work")
print("  Render with Ctrl+F12 for final output")
