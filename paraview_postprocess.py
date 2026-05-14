from paraview.simple import *

# ==========================================================
# Automated ParaView Post-Processing for Algae Tank
# ==========================================================

# 1. Load the OpenFOAM case
# Assuming you run this where the .OpenFOAM file is located
# Or set the path explicitly, e.g., reader = OpenFOAMReader(FileName='case.OpenFOAM')
reader = OpenFOAMReader(FileName='C:/Users/admin/CfdOF/case/case.foam')
reader.MeshRegions = ['internalMesh'] # Important to only render the inside!
reader.CellArrays = ['U', 'p'] # Load Velocity and Pressure
reader.UpdatePipeline()

# Convert OpenFOAM Cell Data to Point Data so StreamTracer can use it
c2p = CellDatatoPointData(registrationName='Cell_To_Point', Input=reader)
c2p.UpdatePipeline()

# Get the active view
renderView = GetActiveViewOrCreate('RenderView')

# Go to the last timestep (the final converged result), otherwise it loads time=0 where U=0!
if len(reader.TimestepValues) > 0:
    renderView.ViewTime = reader.TimestepValues[-1]

# 2. Slice the model down the middle (YZ plane to see the vortex)
slice1 = Slice(registrationName='Middle_Slice', Input=c2p)
slice1.SliceType = 'Plane'
slice1.HyperTreeGridSlicer = 'Plane'
slice1.SliceOffsetValues = [0.0]

# Set Slice plane normal to X axis (so it cuts along YZ)
slice1.SliceType.Origin = [0.0, 0.0, 0.0]
slice1.SliceType.Normal = [1.0, 0.0, 0.0]

# Update bounding box
slice1.UpdatePipeline()

# 3. Apply StreamTracer to see the flow paths
# CRITICAL FIX: StreamTracer needs to look at the 3D volume (c2p), NOT the 2D slice!
streamTracer1 = StreamTracer(registrationName='Aeration_Streamlines', Input=c2p)
streamTracer1.Vectors = ['POINTS', 'U']
streamTracer1.MaximumStreamlineLength = 2000.0

# Set seed type to Line (for ParaView 6.1+)
streamTracer1.SeedType = 'Line'

# Draw a line from one side of the tank to the other, safely inside the main tank height
# Main tank starts at z=130. We use z=200 to guarantee we are inside the fluid.
streamTracer1.SeedType.Point1 = [-80.0, 0.0, 200.0]
streamTracer1.SeedType.Point2 = [80.0, 0.0, 200.0]
streamTracer1.SeedType.Resolution = 150

streamTracer1.UpdatePipeline()

# 4. Visualization Settings
# Hide the raw OpenFOAM shell and the raw c2p volume
Hide(reader, renderView)
Hide(c2p, renderView)

# Show the Slice (colored by pressure using POINT data)
sliceDisplay = Show(slice1, renderView, 'GeometryRepresentation')
ColorBy(sliceDisplay, ('POINTS', 'p'))
pLUT = GetColorTransferFunction('p')
sliceDisplay.SetScalarBarVisibility(renderView, True)
sliceDisplay.RescaleTransferFunctionToDataRange(True, False)

# Show the Streamlines (colored by velocity magnitude)
streamDisplay = Show(streamTracer1, renderView, 'GeometryRepresentation')
ColorBy(streamDisplay, ('POINTS', 'U', 'Magnitude'))
uLUT = GetColorTransferFunction('U')
uLUT.ApplyPreset('Jet', True) # Set Streamlines to 'Jet' to pop out
streamDisplay.LineWidth = 2.0
streamDisplay.SetScalarBarVisibility(renderView, True)

# 5. Final Render
renderView.ResetCamera()
RenderAllViews()

print("ParaView pipeline setup complete! Slice and Streamlines generated.")