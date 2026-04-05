"""SPH-based 3-D tank simulation using PySPH.

A 20 L rectangular tank (430 x 215 x 215 mm) filled to 90 % with water.
A vertical PVC air-injection tube sits near the left-front corner and
drives an upward plume.

Run::

    conda activate pysph_env
    python simulations/sph_tank.py

Output files are written to ``sph_tank_output/`` and can be viewed with
``python simulations/view_results.py``.
"""

import numpy as np
from pysph.sph.equation import Equation
from pysph.tools.geometry import get_3d_block, get_particle_array_wcsph
from pysph.solver.application import Application
from pysph.sph.scheme import WCSPHScheme

# ---------------------------------------------------------------------------
# Tank geometry (all dimensions in metres)
# ---------------------------------------------------------------------------
L = 0.430        # length  (x)
W = 0.215        # width   (y)
H = 0.215        # height  (z)
FILL = 0.90      # fraction filled with water
H_WATER = H * FILL

# particle spacing — coarse for fast prototyping
DX = 0.01        # 10 mm spacing

# reference density and speed of sound
RHO0 = 1000.0
G = 9.81
C0 = 10.0 * np.sqrt(2.0 * G * H)   # ~10 x sqrt(2*g*H)

# air-injection pipe parameters
PIPE_X = 0.05 * L      # near left wall
PIPE_Y = 0.05 * W      # near front wall
PIPE_R = 0.02           # 20 mm influence radius
AIR_ACCEL = 50.0        # m/s^2 upward push (~5g, strong plume)


# ---------------------------------------------------------------------------
# Custom equation: air-injection body force
# ---------------------------------------------------------------------------
class AirInjectionForce(Equation):
    """Apply upward acceleration to fluid particles near the injector pipe.

    This runs inside the SPH evaluation loop (post_loop) so it is NOT
    overwritten by MomentumEquation's initialize step.
    """
    def __init__(self, dest, sources, pipe_x, pipe_y, pipe_r, az):
        self.pipe_x = pipe_x
        self.pipe_y = pipe_y
        self.pipe_r2 = pipe_r * pipe_r
        self.az = az
        super().__init__(dest, sources)

    def post_loop(self, d_idx, d_x, d_y, d_aw):
        dx = d_x[d_idx] - self.pipe_x
        dy = d_y[d_idx] - self.pipe_y
        r2 = dx * dx + dy * dy
        if r2 < self.pipe_r2:
            d_aw[d_idx] += self.az


def _make_open_tank_walls(dx, length, width, height, n_layers=2):
    """Create wall particles for five faces (open top) of a box.

    Each face is a slab of thickness ``n_layers * dx``.
    Returns arrays (x, y, z).
    """
    _x, _y, _z = [], [], []

    # bottom  (z = 0 .. -n_layers*dx)
    xb, yb, zb = get_3d_block(
        dx, length + 2*n_layers*dx, width + 2*n_layers*dx, n_layers*dx)
    xb += length/2
    yb += width/2
    zb -= n_layers*dx/2
    _x.append(xb); _y.append(yb); _z.append(zb)

    # front wall  (y = 0)
    xf, yf, zf = get_3d_block(dx, length + 2*n_layers*dx, n_layers*dx, height)
    xf += length/2
    yf -= n_layers*dx/2
    zf += height/2
    _x.append(xf); _y.append(yf); _z.append(zf)

    # back wall  (y = W)
    xb2, yb2, zb2 = get_3d_block(dx, length + 2*n_layers*dx, n_layers*dx, height)
    xb2 += length/2
    yb2 += width + n_layers*dx/2
    zb2 += height/2
    _x.append(xb2); _y.append(yb2); _z.append(zb2)

    # left wall  (x = 0)
    xl, yl, zl = get_3d_block(dx, n_layers*dx, width, height)
    xl -= n_layers*dx/2
    yl += width/2
    zl += height/2
    _x.append(xl); _y.append(yl); _z.append(zl)

    # right wall  (x = L)
    xr, yr, zr = get_3d_block(dx, n_layers*dx, width, height)
    xr += length + n_layers*dx/2
    yr += width/2
    zr += height/2
    _x.append(xr); _y.append(yr); _z.append(zr)

    return np.concatenate(_x), np.concatenate(_y), np.concatenate(_z)


class TankApp(Application):
    """PySPH Application — water tank with air injector."""

    def create_particles(self):
        dx = DX

        # --- fluid particles (fill from bottom to H_WATER) ---
        xf, yf, zf = get_3d_block(dx, L, W, H_WATER)
        xf += L / 2
        yf += W / 2
        zf += H_WATER / 2
        m = dx**3 * RHO0
        h0 = dx * 1.3
        fluid = get_particle_array_wcsph(
            name='fluid', x=xf, y=yf, z=zf,
            m=m, rho=RHO0, h=h0,
        )

        # --- boundary (wall) particles ---
        xw, yw, zw = _make_open_tank_walls(dx, L, W, H)
        boundary = get_particle_array_wcsph(
            name='boundary', x=xw, y=yw, z=zw,
            m=m, rho=RHO0, h=h0,
        )

        print(f"Fluid particles : {fluid.get_number_of_particles()}")
        print(f"Wall particles  : {boundary.get_number_of_particles()}")
        return [fluid, boundary]

    def create_scheme(self):
        s = WCSPHScheme(
            ['fluid'], ['boundary'], dim=3,
            rho0=RHO0, c0=C0,
            h0=DX * 1.3, hdx=1.3,
            gamma=7.0, alpha=0.1,
            gz=-G,                    # ← GRAVITY
        )
        return s

    def create_equations(self):
        """Get default WCSPH equations, then append air-injection force."""
        equations = self.scheme.get_equations()
        # Append our custom force to the last equation group
        # (the momentum/force group)
        equations[-1].equations.append(
            AirInjectionForce(
                dest='fluid', sources=None,
                pipe_x=PIPE_X, pipe_y=PIPE_Y,
                pipe_r=PIPE_R, az=AIR_ACCEL,
            )
        )
        return equations

    def configure_scheme(self):
        self.scheme.configure_solver(
            dt=1e-5, tf=2.0,
            adaptive_timestep=True,
            output_at_times=[0.0, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0],
        )


if __name__ == '__main__':
    app = TankApp()
    app.run()
