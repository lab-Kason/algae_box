"""Simple demo to generate a flow field inside the 20L tank.

This script produces a structured-grid VTK file that can be opened in
ParaView.  It is intentionally easy to read and modify; extend it later
with a proper solver if you wish.
"""

import os
import numpy as np
import pyvista as pv

# tank dimensions (mm)
L, W, H = 430.0, 215.0, 215.0

# grid resolution (coarse for demo)
nx, ny, nz = 40, 20, 20

# build a regular grid of points
x = np.linspace(0, L, nx)
y = np.linspace(0, W, ny)
z = np.linspace(0, H, nz)
xx, yy, zz = np.meshgrid(x, y, z, indexing="ij")

# create a structured grid object
grid = pv.StructuredGrid(xx, yy, zz)

# example velocity field: uniform + simple boundary profile
U_bulk = 50.0  # mm/s
velocity = np.zeros((nx * ny * nz, 3))
# apply 1/7 power law in z to simulate boundary layer
depth_factor = (zz.ravel() / H) ** 0.2
velocity[:, 0] = U_bulk * depth_factor

grid["velocity"] = velocity

# optional scalar field: speed magnitude
grid["speed"] = np.linalg.norm(velocity, axis=1)

# save to file in this directory
out_dir = os.path.dirname(__file__)
output = os.path.join(out_dir, "demo_flow.vtk")
grid.save(output)
print(f"Wrote {output} with shape {nx}×{ny}×{nz}")

# optionally make a quick PyVista plot and screenshot for preview
try:
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(grid, show_edges=True, opacity=0.25)
    # add glyphs for velocity
    glyphs = grid.glyph(orient="velocity", scale="speed", factor=2.0)
    plotter.add_mesh(glyphs, color="red")
    screenshot = os.path.join(out_dir, "demo_flow.png")
    plotter.show(screenshot=screenshot)
    print(f"Saved preview image to {screenshot}")
except Exception as e:
    print("PyVista preview skipped (headless or display issues):", e)
