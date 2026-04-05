"""Simple 3D particle-based demo of water in a tank with an air injector.

This is *not* a CFD solver; it treats the liquid as a cloud of
co-moving particles subject to gravity, wall collisions and a small
upward force in the region of a green PVC air tube.  It's intended as a
\"game-like\" physics prototype that can be rendered in 3D.

Run with ``python simulations/particle_tank.py``.  A short animation will
appear showing particles sloshing in a box; every few frames the state is
also written to VTK which can be viewed with ParaView/PyVista.

The script uses only numpy and pyvista, both of which are already in the
requirements.  If you later install ``pygame`` you can adapt the update
loop into a real-time window.
"""

import numpy as np
import pyvista as pv
import os

# tank dimensions (millimetres to match earlier scripts)
L = 430.0
W = 215.0
H = 215.0

# water occupies 18 L = 90% of volume; fill from bottom to this height
fill_fraction = 0.9
H_water = H * fill_fraction

# particle settings
N = 4000  # number of water particles
np.random.seed(1)
positions = np.empty((N, 3))
# uniform distribution in box [0,L]x[0,W]x[0,H_water]
positions[:, 0] = np.random.rand(N) * L
positions[:, 1] = np.random.rand(N) * W
positions[:, 2] = np.random.rand(N) * H_water

velocities = np.zeros_like(positions)

# physics parameters
g = 9.81e3   # gravity mm/s^2 downward
dt = 0.01    # time step (s)
air_force = 5e3  # upward force (mm/s^2) from injector
# simple SPH‑like interaction parameters
h = 15.0        # interaction radius
mass = 1.0      # fictitious particle mass
rho0 = 1000.0   # reference density
k = 50.0        # stiffness for pressure
mu = 10.0       # viscosity coefficient

# air injector geometry
pipe_x = 0.05 * L
pipe_y = 0.05 * W
pipe_r = 0.02 * W
pipe_z = 0.02 * H  # slightly above bottom

output_dir = 'simulations/particles'
os.makedirs(output_dir, exist_ok=True)

# helper collision with walls: reflect and damp

def collide(pos, vel):
    # x walls
    mask = pos[:, 0] < 0
    vel[mask, 0] *= -0.3
    pos[mask, 0] = 0
    mask = pos[:, 0] > L
    vel[mask, 0] *= -0.3
    pos[mask, 0] = L
    # y walls
    mask = pos[:, 1] < 0
    vel[mask, 1] *= -0.3
    pos[mask, 1] = 0
    mask = pos[:, 1] > W
    vel[mask, 1] *= -0.3
    pos[mask, 1] = W
    # z bottom
    mask = pos[:, 2] < 0
    vel[mask, 2] *= -0.3
    pos[mask, 2] = 0
    # z top (free surface) allow escape or simple reflection
    mask = pos[:, 2] > H
    vel[mask, 2] *= -0.3
    pos[mask, 2] = H


# injector force: upward acceleration for particles near the pipe

def injector_force(pos):
    dx = pos[:, 0] - pipe_x
    dy = pos[:, 1] - pipe_y
    dz = pos[:, 2] - pipe_z
    r2 = dx * dx + dy * dy
    mask = r2 < pipe_r**2
    f = np.zeros_like(pos)
    f[mask, 2] = air_force
    return f

# compute inter-particle forces mimicking SPH pressure+viscosity
# naive O(N^2) implementation, fine for a few thousand points

def sph_forces(pos, vel):
    Np = pos.shape[0]
    f = np.zeros_like(pos)
    for i in range(Np):
        for j in range(i+1, Np):
            rij = pos[i] - pos[j]
            r = np.linalg.norm(rij)
            if r < h and r>1e-8:
                # density estimate (not used explicitly)
                # simple linear kernel W = (h - r)
                W = (h - r)
                # pressure term (repulsive)
                # p = k*(rho - rho0) approx using W
                fp = k * W * (rij / r)
                # viscosity term
                dv = vel[j] - vel[i]
                fv = mu * dv * W
                f[i] += fp + fv
                f[j] -= fp + fv
    return f


# VTK export

def export(step, pos):
    grid = pv.PolyData(pos)
    grid['velocity'] = velocities
    grid.save(os.path.join(output_dir, f'particles_{step:04d}.vtk'))


# set up PyVista plotter for animation
plotter = pv.Plotter(window_size=(600, 400))
plotter.set_background('white')
# create a mesh so we can update its coordinates each frame
particle_mesh = pv.PolyData(positions)
particle_mesh['velocity'] = velocities
plotter.add_mesh(particle_mesh, color='blue', point_size=4, render_points_as_spheres=True)
plotter.add_axes()
plotter.enable_eye_dome_lighting()
plotter.camera_position = [(L*1.2, W*1.2, H*1.2), (L/2, W/2, H/2), (0, 0, 1)]

# show the plotter once and keep it open
plotter.show(auto_close=False)

steps = 500
for step in range(steps):
    # apply gravity
    velocities[:, 2] -= g * dt
    # injector
    velocities += injector_force(positions) * dt
    # inter-particle SPH-like forces
    velocities += sph_forces(positions, velocities) * dt / mass
    # update positions
    positions += velocities * dt
    collide(positions, velocities)
    # update plot: either assign new points or use update_coordinates
    particle_mesh.points = positions
    plotter.render()
    if step % 50 == 0:
        export(step, positions)

# once done, keep the window open until user closes it
plotter.close()
