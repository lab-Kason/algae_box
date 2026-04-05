"""Generate a very crude "air‑bubble" velocity/pressure field for the 20 L tank.

This is not a solver – it merely fabricates a vector field that mimics
warm/air‑injected fluid rising near a source and returning elsewhere.  In
ParaView you can colour by velocity magnitude or a synthetic pressure
field to visualise the circulation.

Run the script and open "buoyancy_flow.vtk" in ParaView alongside the
geometry (tank_geometry.vtp) for context.
"""

import os
import numpy as np
import pyvista as pv

# tank dimensions
L, W, H = 430.0, 215.0, 215.0

# grid resolution
nx, ny, nz = 50, 25, 25
x = np.linspace(0, L, nx)
y = np.linspace(0, W, ny)
z = np.linspace(0, H, nz)
xx, yy, zz = np.meshgrid(x, y, z, indexing="ij")

grid = pv.StructuredGrid(xx, yy, zz)

# parameters for upward plume located near vertical tube
source_x = 0.1 * L
source_y = 0.1 * W
sigma = 0.1 * W

# compute radial distance in horizontal plane from plume centre
r2 = (xx - source_x) ** 2 + (yy - source_y) ** 2

# vertical velocity: strong upward plume at source, weak downward
# elsewhere.  no horizontal swirl.
# plume radius and strength
plume_mag = 20.0  # mm/s max upward
w_plume = plume_mag * np.exp(-r2 / (2 * sigma ** 2))
# downward background chosen to conserve volume: subtract mean
avg_w = np.mean(w_plume)
w = w_plume - avg_w

# horizontal components zero
nu = np.zeros_like(w)
nw = np.zeros_like(w)

vel = np.vstack((nu.ravel(), nw.ravel(), w.ravel())).T
grid["velocity"] = vel

# synthetic pressure field (higher near bottom of plume)
pressure = -w.reshape((nx * ny * nz,))
grid["pressure"] = pressure

# save
outdir = os.path.dirname(__file__)
outfile = os.path.join(outdir, "buoyancy_flow.vtk")
grid.save(outfile)
print(f"Wrote {outfile}")

# also optionally write a PVD series if you want times in future
