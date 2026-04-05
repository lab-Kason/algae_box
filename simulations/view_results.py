"""Visualise PySPH tank simulation results with PyVista.

Usage:
    conda activate pysph_env
    python simulations/view_results.py

Shows an interactive 3-D view of fluid particles coloured by velocity
magnitude.  Use the slider to scrub through time-steps.
"""

import glob
import os
import numpy as np
import pyvista as pv

OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), '..', 'sph_tank_output'
)

# ── collect and sort snapshot files ──────────────────────────────
files = sorted(glob.glob(os.path.join(OUTPUT_DIR, 'sph_tank_*.npz')))
if not files:
    raise FileNotFoundError(f"No .npz files found in {OUTPUT_DIR}")
print(f"Found {len(files)} snapshots")


def load_frame(path):
    """Load one PySPH .npz snapshot, return fluid-only point cloud."""
    data = np.load(path, allow_pickle=True)

    # PySPH format: data['particles'] -> dict with 'fluid', 'boundary'
    # Each has 'arrays' dict with 'x', 'y', 'z', 'u', 'v', 'w', 'rho', 'p', ...
    fluid = data['particles'].item()['fluid']['arrays']

    x = np.asarray(fluid['x'])
    y = np.asarray(fluid['y'])
    z = np.asarray(fluid['z'])
    u = np.asarray(fluid.get('u', np.zeros_like(x)))
    v = np.asarray(fluid.get('v', np.zeros_like(x)))
    w = np.asarray(fluid.get('w', np.zeros_like(x)))
    rho = np.asarray(fluid.get('rho', np.ones_like(x) * 1000))
    p = np.asarray(fluid.get('p', np.zeros_like(x)))

    # solver time
    t = data['solver_data'].item().get('t', 0)

    points = np.column_stack([x, y, z])
    speed = np.sqrt(u**2 + v**2 + w**2)

    cloud = pv.PolyData(points)
    cloud['velocity_magnitude'] = speed
    cloud['density'] = rho
    cloud['pressure'] = p
    cloud['vx'] = u
    cloud['vy'] = v
    cloud['vz'] = w
    cloud.field_data['time'] = [t]
    return cloud


# ── load first and last frames for reference ────────────────────
print("Loading first frame...")
frame0 = load_frame(files[0])
print(f"  {frame0.n_points} fluid particles")

# ── tank wireframe for context ──────────────────────────────────
L, W, H = 0.430, 0.215, 0.215
tank = pv.Box(bounds=(0, L, 0, W, 0, H))

# ── interactive plotter ─────────────────────────────────────────
pl = pv.Plotter()
pl.set_background('white')
pl.add_mesh(
    tank, style='wireframe', color='gray', line_width=2, label='Tank'
)
actor = pl.add_mesh(
    frame0, scalars='velocity_magnitude', cmap='turbo',
    point_size=5, render_points_as_spheres=True,
    clim=[0, 0.5], label='Fluid'
)


def update_frame(value):
    """Slider callback — load the selected frame."""
    idx = int(round(value))
    idx = max(0, min(idx, len(files) - 1))
    cloud = load_frame(files[idx])
    actor.mapper.dataset.points = cloud.points
    actor.mapper.dataset.point_data['velocity_magnitude'] = cloud['velocity_magnitude']
    actor.mapper.dataset.point_data['density'] = cloud['density']
    actor.mapper.dataset.point_data['pressure'] = cloud['pressure']
    pl.render()


pl.add_slider_widget(
    update_frame,
    rng=[0, len(files) - 1],
    value=0,
    title='Frame',
    pointa=(0.1, 0.05),
    pointb=(0.9, 0.05),
    style='modern',
)

pl.add_text(
    'SPH Tank Simulation — drag slider to scrub time',
    position='upper_left', font_size=10, color='black',
)
pl.show_axes()
pl.show()
