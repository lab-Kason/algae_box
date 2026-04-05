# Simulations

This subdirectory contains simple tools for generating and visualising
fluid-flow data for the 20 L algae tank geometry. The intention is to
keep the numerical code separate from the main application logic, so
you can treat `simulations/` as its own mini‑project (it even can be a
Git sub‑repository if desired).

## Getting started

1. Make sure you have a Python environment with the requirements listed
   in the main `requirements.txt` plus the additional packages below. You
   can install the simulation dependencies with:

   ```bash
   pip install numpy pyvista vtk
   ```

2. Run the generator script to produce a VTK file that ParaView can open:

   ```bash
   cd simulations
   python demo_flow.py
   ```

   This will create `demo_flow.vtk` in the same directory.

3. Open ParaView (installed separately) and load `simulations/demo_flow.vtk`.
   You can then display vectors, slices, streamlines, etc. If you change
   the generator script, rerun it and refresh ParaView to see new results.

### Buoyancy / oxygen injection demo

A second script fabricates a very crude velocity field intended to
simulate the effect of an air/oxygen pump in the vertical tube.  Run
it with:

```bash
python simulations/buoyancy_flow.py
```

This writes `simulations/buoyancy_flow.vtk`, containing a vector field
named `velocity` and a scalar `pressure`.  Load it alongside
`tank_geometry.vtp` (or open it by itself) and:

* Click **Apply**, set `Representation=Surface` and `Opacity ~0.3`
  to see the tank.
* Add a **Glyph** filter on the buoyancy source; set **Vectors** to
  `velocity` and adjust **Scale Factor** to 1–3 to view the rising plume.
* Colour by `pressure` to see the synthetic high/low zones.
* Add **Stream Tracer** or **Slice** filters for further inspection.

Remember that this is only a toy; real air bubbles would require solving
Navier–Stokes with a two‑phase model.  But the file gives you something
visual to display and can be extended with time‑varying data later.


### Automation helpers

* `python open_para.py` will launch the version of ParaView at
  `/Applications/ParaView-6.1.0-RC1.app/Contents/MacOS/paraview` with the
  latest `demo_flow.vtk`.  Adjust the path inside the script if your
  installation lives elsewhere.
* VS Code tasks are defined at `.vscode/tasks.json`: use **Run Task** →
  “Generate flow data” followed by “Open ParaView with latest data” to
  execute the entire workflow from inside the editor.

### Viewing the velocity field

The VTK file contains a structured grid plus a vector field called
`velocity` (and a scalar `speed`).  ParaView does not automatically show
vectors, so follow these steps once the dataset is loaded:

1. Select `demo_flow.vtk` in the **Pipeline Browser** and click **Apply**.
2. In the **Properties** panel set **Representation** to `Surface` or
   `Outline` if nothing appears at first, then click **Reset Camera**.
3. To draw arrows for the flow, choose **Filters → Alphabetical → Glyph**:
   * Set **Vectors** to `velocity` and **Scale Factor** to something
     appropriate (start with 1–5).  Hit **Apply**.  The arrows will show
     the direction and magnitude of the water movement.
4. You can also add a **Slice** filter (choose the Z-plane) or a **Stream
   Tracer** filter to generate streamlines through the field.
5. Adjust colours by changing **Coloring** to `speed` or any scalar.

Once you have a configuration you like, save it as a ParaView state
(`File → Save State…`) into `simulations/default.pvsm`.  Subsequent runs of
`open_para.py` can be edited to pass `--state=simulations/default.pvsm`
and start ParaView with those filters already applied (see note below).

> Tip: the pyvista demo script also includes `speed` magnitude, so you
> can colour by that field if you prefer.



## Making it a sub‑repository

If you want `simulations/` to be a standalone Git repo, run the
following from the workspace root:

```bash
cd simulations
git init
# add files and commit; you can even add a remote
```

This keeps your CFD work isolated while still being versioned with the
main project if you choose.

---

The code in this directory is intentionally simple, so you can extend
it with a real solver later.  Feel free to add more scripts, geometry
exporters, or ParaView Python state files as needed.
