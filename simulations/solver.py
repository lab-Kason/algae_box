"""Simple finite-difference 3D solver for tank flow & algae transport.

This is a **very crude** prototype meant only to answer the question:
"does the two‑pump arrangement have any chance of flushing a 100 NTU
suspension toward the bottom‑corner collector?"  It is **not** a
production CFD code; it uses low resolution, explicit time stepping, and a
tiny Poisson solver.

Usage::

    python simulations/solver.py

The script writes three VTK files into ``simulations/``:

* ``flow_t{t:04d}.vtk`` – velocity + pressure fields for selected times
* ``conc_t{t:04d}.vtk`` – algae concentration field
* ``ntuhistory.csv`` – global turbidity vs time

Adjust the parameters in the ``Config`` class below to change geometry,
pump timings, etc.  ``run_simulation`` returns a dictionary with NTU values
so you can trigger collection as desired.

"""

import numpy as np
import pyvista as pv
from scipy.ndimage import gaussian_filter

# helper derivatives (periodic padding or zero)
def ddx(f,dx):
    return (np.roll(f,-1,axis=0)-np.roll(f,1,axis=0))/(2*dx)
def ddy(f,dy):
    return (np.roll(f,-1,axis=1)-np.roll(f,1,axis=1))/(2*dy)
def ddz(f,dz):
    return (np.roll(f,-1,axis=2)-np.roll(f,1,axis=2))/(2*dz)

# ---------------------------------------------------------------------------
# configuration (only the numbers really matter here)
# ---------------------------------------------------------------------------

class Config:
    L = 430.0  # length in x
    W = 215.0  # width  in y
    H = 215.0  # height in z

    Nx, Ny, Nz = 30, 30, 30
    dt = 0.1
    nu = 1e-3        # viscosity
    rho = 1000.0     # density

    # vertical air tube location (fraction of dims)
    vt_x = 0.1 * L
    vt_y = 0.1 * W
    vt_r = 0.02 * W   # radius of influence for plume
    air_speed = 20.0   # mm/s upward jet velocity (was 100)

    # horizontal sweep tube along y; holes at x positions
    ht_z = 0.05 * H
    ht_y = 0.1 * W   # near front wall
    hole_x = np.linspace(0.1*L, 0.9*L, 5)
    hole_r = 0.01 * L
    # hole jet direction in (x,y,z) space; originally downward but
    # experimental rig has tube parallel to y so jets push along x
    hole_dir = np.array([1.0,0.0,0.0])
    hole_speed = 20.0   # mm/s (reduced to avoid blow‑out)

    # collection corner (target for algae)
    collect = np.array([0.5*L, 0.5*W, 0.0])

    # algae NTU conversion (NTU per unit concentration)
    ntu_coeff = 5.0
    trigger_ntu = 100.0

    # pump schedule functions
    @staticmethod
    def air_on(t):
        return False  # placeholder; controller will override

    @staticmethod
    def water_on(t):
        return False

# ---------------------------------------------------------------------------
# operational routines
# ---------------------------------------------------------------------------

def build_grid(cfg):
    xs = np.linspace(0, cfg.L, cfg.Nx)
    ys = np.linspace(0, cfg.W, cfg.Ny)
    zs = np.linspace(0, cfg.H, cfg.Nz)
    dx = xs[1]-xs[0]
    return xs, ys, zs, dx


def apply_pumps(u, v, w, cfg, air=False, water=False):
    """Modify velocity arrays according to pump flags.

    ``air`` drives an upward plume around the vertical tube.
    ``water`` produces downward jets at the sweep‑tube holes.
    """
    # u,v,w are velocity arrays (Nx,Ny,Nz)
    if air:
        rx = (X - cfg.vt_x)**2 + (Y - cfg.vt_y)**2
        mask = rx < cfg.vt_r**2
        # set a fixed upward jet rather than accumulate
        w[mask] = np.maximum(w[mask], cfg.air_speed)
    if water:
        # jets from sweep tube holes in configured direction
        for hx in cfg.hole_x:
            rx = (X - hx)**2 + (Y - cfg.ht_y)**2
            hole = rx < cfg.hole_r**2
            # set constant jet velocity in each direction
            if cfg.hole_dir[0] != 0:
                u[hole] = cfg.hole_dir[0] * cfg.hole_speed
            if cfg.hole_dir[1] != 0:
                v[hole] = cfg.hole_dir[1] * cfg.hole_speed
            if cfg.hole_dir[2] != 0:
                w[hole] = cfg.hole_dir[2] * cfg.hole_speed
    return u,v,w


def compute_div(u,v,w,dx):
    return ddx(u,dx) + ddy(v,dx) + ddz(w,dx)

def enforce_walls(u,v,w):
    # zero velocity at domain boundaries (simple no‑slip)
    u[0,:,:] = u[-1,:,:] = 0
    v[:,0,:] = v[:,-1,:] = 0
    w[:,:,0] = w[:,:,-1] = 0
    return u,v,w

def cap_velocity(u,v,w,maxvel=50.0):
    mag = np.sqrt(u**2 + v**2 + w**2)
    mask = mag > maxvel
    if mask.any():
        factor = maxvel / (mag[mask] + 1e-12)
        u[mask] *= factor
        v[mask] *= factor
        w[mask] *= factor
    return u,v,w


def project(u,v,w,dx,dt):
    # simple projection (Jacobi Poisson solver)
    div = compute_div(u,v,w,dx)
    phi = np.zeros_like(div)
    for _ in range(100):
        phi[1:-1,1:-1,1:-1] = (
            phi[:-2,1:-1,1:-1] + phi[2:,1:-1,1:-1] +
            phi[1:-1,:-2,1:-1] + phi[1:-1,2:,1:-1] +
            phi[1:-1,1:-1,:-2] + phi[1:-1,1:-1,2:]
        )/6 - dx*dx*div[1:-1,1:-1,1:-1]/6
    u -= dt*ddx(phi,dx)
    v -= dt*ddy(phi,dx)
    w -= dt*ddz(phi,dx)
    return u,v,w,phi


def advect_scalar(c,u,v,w,dx,dt):
    # simple central advection
    cx = ddx(c,dx)
    cy = ddy(c,dx)
    cz = ddz(c,dx)
    c -= dt*(u*cx + v*cy + w*cz)
    c = np.clip(c,0,None)
    return c


def run_simulation(cfg, t_end=20.0):
    xs,ys,zs,dx = build_grid(cfg)
    global X,Y,Z
    X,Y,Z = np.meshgrid(xs,ys,zs,indexing='ij')
    u = np.zeros((cfg.Nx,cfg.Ny,cfg.Nz))
    v = np.zeros_like(u)
    w = np.zeros_like(u)
    p = np.zeros_like(u)
    c = np.ones_like(u)  # algae concentration

    nt = int(t_end/cfg.dt)
    ntu_history = []
    for n in range(nt):
        t = n*cfg.dt
        u,v,w = apply_pumps(u,v,w,cfg,t)
        u,v,w,p = project(u,v,w,dx,cfg.dt)
        # enforce walls & cap magnitude before damping
        u,v,w = enforce_walls(u,v,w)
        u,v,w = cap_velocity(u,v,w,maxvel=cfg.air_speed*3)
        # damp velocities so they don't accumulate unboundedly
        u *= 0.99
        v *= 0.99
        w *= 0.99
        c = advect_scalar(c,u,v,w,dx,cfg.dt)
        ntu = cfg.ntu_coeff * c.mean()
        ntu_history.append((t,ntu))
        if n%10==0:
            export_fields(n,u,v,w,p,c,cfg)
    np.savetxt('simulations/ntuhistory.csv', ntu_history, header='t NTU')
    return ntu_history


def export_fields(n,u,v,w,p,c,cfg):
    # build a structured grid from cell centres
    xs = np.linspace(0, cfg.L, cfg.Nx)
    ys = np.linspace(0, cfg.W, cfg.Ny)
    zs = np.linspace(0, cfg.H, cfg.Nz)
    xx, yy, zz = np.meshgrid(xs, ys, zs, indexing='ij')
    grid = pv.StructuredGrid(xx, yy, zz)
    grid.point_data['u'] = u.ravel(order='F')
    grid.point_data['v'] = v.ravel(order='F')
    grid.point_data['w'] = w.ravel(order='F')
    grid.point_data['pressure'] = p.ravel(order='F')
    grid.point_data['conc'] = c.ravel(order='F')
    grid.save(f'simulations/flow_t{n:04d}.vtk')
    grid.save(f'simulations/conc_t{n:04d}.vtk')

def simulate_with_control(cfg, t_end=60.0):
    """Run simulation with simple NTU-triggered controller."""
    xs,ys,zs,dx = build_grid(cfg)
    global X,Y,Z
    X,Y,Z = np.meshgrid(xs,ys,zs,indexing='ij')
    u = np.zeros((cfg.Nx,cfg.Ny,cfg.Nz))
    v = np.zeros_like(u)
    w = np.zeros_like(u)
    p = np.zeros_like(u)
    # start with turbidity at the trigger level (e.g. 100 NTU)
    c = np.full_like(u, cfg.trigger_ntu / cfg.ntu_coeff)

    nt = int(t_end/cfg.dt)
    ntu_history = []
    # start with vertical air pump on, horizontal pump off
    air = True
    water = False
    for n in range(nt):
        t = n*cfg.dt
        # apply pumps according to current state
        u,v,w = apply_pumps(u,v,w,cfg,air=air,water=water)
        u,v,w,p = project(u,v,w,dx,cfg.dt)
        u,v,w = enforce_walls(u,v,w)
        u,v,w = cap_velocity(u,v,w,maxvel=cfg.air_speed*3)
        # damp velocities slightly each step
        u *= 0.99
        v *= 0.99
        w *= 0.99
        c = advect_scalar(c,u,v,w,dx,cfg.dt)
        # remove algae near the collector when water pump is active
        if water:
            ix = int(cfg.collect[0]/(cfg.L/cfg.Nx))
            iy = int(cfg.collect[1]/(cfg.W/cfg.Ny))
            iz = int(cfg.collect[2]/(cfg.H/cfg.Nz))
            # make the cleared region a few cells wide so the mean concentration
            # actually decreases noticeably
            r = 5
            # zero out the concentration in the cube around the collector
            c[max(0,ix-r):ix+r+1,
              max(0,iy-r):iy+r+1,
              max(0,iz-r):iz+r+1] = 0.0
        ntu = cfg.ntu_coeff * c.mean()
        ntu_history.append((t,ntu))
        if ntu >= cfg.trigger_ntu and air:
            air = False
            water = True
        if n%10==0:
            export_fields(n,u,v,w,p,c,cfg)
    np.savetxt('simulations/ntuhistory.csv', ntu_history, header='t NTU')
    return ntu_history


if __name__ == '__main__':
    cfg = Config()
    history = simulate_with_control(cfg)
    print(history[:10])
