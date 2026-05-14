# Project Progress & Mac Migration Guide

## 🚀 Current Work Progress
- **CAD & Geometry**: Developed fully parameterized Python scripts for FreeCAD that generate a cohesive fluid domain encompassing an air-lift bioreactor, hydrocyclone, bottom valve, and aeration torus.
- **CFD Simulation (Cultivation Phase)**:
  - Configured boundary conditions (zero gravity, isothermal, steady-state, `simpleFoam` solver) to mimic aeration momentum via velocity boundaries without the overhead of heavy multiphase solvers.
  - Successfully generated the mesh using Gmsh (Tetrahedral meshes) and solved the simulation, achieving stable convergence with exceptionally low residuals.
  - Overcame multiple CfdOF workbench issues regarding missing static pressure boundaries, gravity/thermal conflicts, and patch naming.
- **Post-Processing (ParaView)**: 
  - Created a fully automated ParaView Python script (`paraview_postprocess.py`) utilizing `paraview.simple`.
  - The script automates loading the OpenFOAM `.foam` case, focusing purely on the interior water flow (`internalMesh`), applying a centerline Y-axis Slice, and rendering high-resolution streamline tracer tubes to visualize the internal vortex.

---

## 🍎 Mac Setup & Migration Guide

Assuming your Mac is a clean slate and only has VS Code installed, here is what you need to download and configure to resume your CFD and IoT work seamlessly.

### 1. Applications & Core Software
- **[Git](https://git-scm.com/downloads/mac)**: Open the Mac terminal and type `git --version`. It will prompt you to install Apple's Command Line Tools if you haven't already. Alternatively, install via homebrew: `brew install git`.
- **[FreeCAD (1.1.1+)](https://www.freecadweb.org/downloads.php)**: To run your Python CAD generation macros.
  - *Crucial Step*: Open FreeCAD on Mac > Tools > Addon Manager, and reinstall the **CfdOF** workbench.
- **[OpenFOAM](https://openfoam.org/download/mac/)**: For running simulations. On Mac, this is normally installed via Docker. Follow the official instructions to create the OpenFOAM Docker container, which will provide you with commands like `simpleFoam` and `decomposePar`.
- **[ParaView](https://www.paraview.org/download/)**: For visualizing the CFD data and executing `paraview_postprocess.py`.
- **[Gmsh](https://gmsh.info/)**: The meshing software required by the CfdOF workbench. Install it and configure FreeCAD's CfdOF preferences to point to the Gmsh Mac binary.
- **[Arduino IDE v2](https://www.arduino.cc/en/software)** (Optional but recommended): Good as a fallback for the ESP32 files if you aren't strictly using PlatformIO.

### 2. VS Code Extensions You Will Need
Search for and install these extensions inside VS Code on your Mac:
1. **Python** (by Microsoft): Required for modifying and running the CAD and simulation scripts.
2. **C/C++** (by Microsoft): For intellisense on your ESP32 Arduino (`.ino`, `.cpp`) files.
3. **PlatformIO IDE** (by PlatformIO): Required for compiling and uploading code to the ESP32 using the `platformio.ini` environment setup.
4. **Wokwi Simulator** (by Wokwi): To run and simulate your ESP32 hardware diagrams (`diagram.json`, `sketch.ino`) without the physical board.

### 3. File Transfers (Important!)
- **Code Repository**: Run `git clone <your_repo_url>` in the Mac terminal. All code scripts, Wokwi simulations, and `.md` hardware guides will safely transfer over automatically.
- **CFD Solved Output Data (Manual Transfer Required)**: OpenFOAM generated cases and large mesh files are stored locally on your Windows machine at `C:\Users\admin\CfdOF\case` and `C:\Users\admin\CfdOF\meshCase`. **These are not tracked by Git** due to their immense file size. 
  - *Action*: If you want to open ParaView on your Mac to view the solved Cultivation Phase flow immediately (saving you from running the hour-long simulation again), you must ZIP the `C:\Users\admin\CfdOF` folder on Windows and transfer it to your Mac via USB drive or Google Drive. Make sure to update the `case_path` inside `paraview_postprocess.py` to match the new Mac folder structure.

### 4. ESP32 Hardware Environment
When you physically plug the ESP32-S3 into your Mac, macOS generally has better native driver support than Windows. However, depending on your ESP32's USB-to-UART chip, you might need to install [CP210x Drivers](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) or [CH340 Drivers](https://learn.sparkfun.com/docs/ch340-mac-install) so VS Code/PlatformIO can detect the COM port to flash updates.