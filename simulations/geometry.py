"""Generate a simple 3D mesh for the tank and PVC tubes.

This script builds a box representing the tank and two cylinders for the
horizontal and vertical pipes, then writes them to a single VTK file
(`tank_geometry.vtp`) that ParaView can open alongside flow data.
"""
import numpy as np
import pyvista as pv

# tank outer box dimensions (mm or arbitrary units)
L, W, H = 430.0, 215.0, 215.0

# create tank as a box (shell)
tank = pv.Cube(center=(L/2, W/2, H/2), x_length=L, y_length=W, z_length=H)

# horizontal tube parameters
# tube now penetrates the left/right faces and therefore runs along the Y axis
# place it near the front/bottom region (small X coordinate) and slightly
# above the bottom (Z coordinate)
h_x = 0.1 * L  # offset from front wall in X-direction
h_z = 0.2 * H  # height from bottom
h_radius = 5.0  # arbitrary radius
h_length = W + 20.0  # extend slightly beyond the Y-extents for clarity
h_center = (h_x, W/2, h_z)
# orientation vector along Y axis (penetration direction)
h_dir = (0, 1, 0)
h_tube = pv.Cylinder(center=h_center, direction=h_dir, radius=h_radius, height=h_length)

# vertical tube parameters
v_x = 0.1 * L
v_y = 0.1 * W
v_z0 = 0.25 * H
v_z1 = H
v_radius = 5.0
v_height = v_z1 - v_z0
v_center = (v_x, v_y, (v_z0 + v_z1) / 2)
v_dir = (0, 0, 1)
v_tube = pv.Cylinder(center=v_center, direction=v_dir, radius=v_radius, height=v_height)

# optionally create a water volume inside the tank for visualization
# (slightly smaller than the inner dimensions so it doesn't overlap walls)
inner_offset = 2.0  # mm or whatever units you are using
water = pv.Cube(
    center=(L/2, W/2, H/2),
    x_length=L - 2 * inner_offset,
    y_length=W - 2 * inner_offset,
    z_length=H - 2 * inner_offset,
)
water['water'] = np.ones(water.n_points)  # scalar field to colour by

# combine into a single mesh (tank, tubes, plus water block)
combined = tank.merge(h_tube).merge(v_tube).merge(water)

# save geometry to file
out = "tank_geometry.vtp"
combined.save(out)
print(f"Wrote geometry (with water) to {out}")

# also save the water separately if you want to load it on its own
water.save("tank_water.vtp")
print("Wrote water volume to tank_water.vtp")
