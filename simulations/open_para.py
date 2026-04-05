"""Helper to launch ParaView from within Python.

This script makes it easier to include the viewer as part of a
workflow/CI; you can call it from VS Code or from another script.
"""
import os
import subprocess
import sys

# default path to ParaView binary (macOS)
PARAVIEW_PATH = "/Applications/ParaView-6.1.0-RC1.app/Contents/MacOS/paraview"

if not os.path.isfile(PARAVIEW_PATH):
    print(f"Warning: ParaView binary not found at {PARAVIEW_PATH}")
    print("You may need to adjust the path or install ParaView first.")

# allow passing a filename on the command line
if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
    vtkfile = sys.argv[1]
else:
    vtkfile = os.path.join(os.path.dirname(__file__), "demo_flow.vtk")

if not os.path.isfile(vtkfile):
    print(f"Data file {vtkfile} does not exist; run demo_flow.py first.")
    sys.exit(1)

# check for a saved ParaView state
state_file = os.path.join(os.path.dirname(__file__), "default.pvsm")
cmd = [PARAVIEW_PATH]
if os.path.isfile(state_file):
    cmd += ["--state=", state_file]
cmd.append(vtkfile)

print(f"Launching ParaView with {vtkfile} ...")
subprocess.Popen(cmd)
