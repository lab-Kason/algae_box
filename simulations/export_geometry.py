"""Utility to export the FreeCAD tank model as a mesh for use in
solvers or ParaView.

This script assumes you can run FreeCAD in headless mode.  It simply
loads the `CADsimulation.py` script, recomputes, and writes an STL mesh.
"""

import sys
import os

# adjust path if needed, or simply import CADsimulation to build the model
import CADsimulation  # when run from workspace root, this will execute the file

# After CADsimulation runs there should be a document in FreeCAD
try:
    import FreeCAD as App
except ImportError:
    print("FreeCAD module not found; cannot export geometry.")
    sys.exit(1)

# grab the tank object
doc = App.ActiveDocument
if not doc:
    print("No active FreeCAD document; please run CADsimulation first.")
    sys.exit(1)

obj = doc.getObject("Standard_Tank_20L")
if not obj:
    print("Tank object not found in document.")
    sys.exit(1)

# export to STL/VTK
out_dir = os.path.dirname(__file__)
stl_path = os.path.join(out_dir, "tank.stl")
obj.Shape.exportStl(stl_path)
print(f"Exported tank mesh to {stl_path}")
