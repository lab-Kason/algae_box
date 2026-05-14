# Transfer & Setup Guide — Move project from Windows to macOS

This document lists required applications, VS Code extensions, files to transfer, and quick commands to set up the project on a clean macOS machine (assumes only VS Code is installed). It also summarizes current progress of the project.

---

## 1 — Current progress (snapshot)
- FreeCAD CAD model and geometry generation: `Algae_tank_full_system.py` (FreeCAD macro) completed.
- Mesh and OpenFOAM case: directory `CfdOF/case` with converged `simpleFoam` solution (steady-state). Gmsh mesh exported and converted to OpenFOAM.
- Postprocessing script: `paraview_postprocess.py` available to load the `.foam` case and generate slices + streamlines in ParaView.
- Other useful code & data: `modules/`, `simulations/`, `streamlit_qr/`, `data/algae_log.csv`.

Recommended files to copy to mac:
- `CfdOF/` (entire folder: meshCase, case, Any `.foam` files)
- `paraview_postprocess.py`
- `Algae_tank_full_system.py`
- `FreeCADreportview.txt`
- `modules/` folder
- `simulations/` folder
- `requirements.txt` (root and streamlit_qr/requirements.txt)
- `README.md`, `PROJECT_PLAN.md`, `TODO.md`

---

## 2 — macOS required apps (suggested install method: Homebrew / brew cask / Docker)
Prerequisite: install Homebrew (if not present)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install the tools below.

- Git
  ```bash
  brew install git
  ```
- Python 3.11+ (for scripts and streamlit)
  ```bash
  brew install python@3.11
  pip3 install --upgrade pip
  ```
- FreeCAD (GUI, recommended via Homebrew cask)
  ```bash
  brew install --cask freecad
  ```
- Gmsh (meshing)
  ```bash
  brew install gmsh
  ```
- ParaView (GUI + pvpython)
  ```bash
  brew install --cask paraview
  ```
- Docker (recommended for OpenFOAM on macOS)
  ```bash
  brew install --cask docker
  # then run Docker Desktop and sign in/enable privileged access if needed
  ```
- OpenFOAM (via Docker image — easiest on macOS)
  - Pull the official OpenFOAM container (replace version as necessary):
  ```bash
  docker pull openfoam/openfoam2312
  ```
  - Run your case in the container (example)
  ```bash
  docker run -it --rm -v "/Users/yourname/Projects/algae_box/CfdOF:/home/openfoam/case" openfoam/openfoam2312 bash
  # inside the container:
  # cd /home/openfoam/case
  # ./Allrun
  ```

Notes: native macOS builds of OpenFOAM exist but are often out-of-date or fragile; using Docker provides the cleanest parity with your Linux/Windows results.

---

## 3 — VS Code extensions to install on mac
Install the following extensions in VS Code Marketplace (quick list):
- `ms-python.python` — Python language support
- `ms-python.vscode-pylance` — fast Language Server
- `ms-vscode.cpptools` — C/C++ helper (useful for OpenFOAM code reading)
- `eamodio.gitlens` — Git helper
- `ms-vscode-remote.remote-ssh` — if you plan to run jobs on remote Linux host
- `ms-python.black-formatter` or `ms-python.isort` (optional) — formatting

Optional (project-specific):
- `ms-vscode.azure-account` (if using cloud)
- PlatformIO (`platformio.platformio-ide`) for ESP32 firmware (if porting Arduino code)

---

## 4 — Transfer files from Windows to mac
Option A. Use external drive: copy the `algae_box` folder to a USB drive and copy onto the Mac.

Option B. Use `scp` (from Windows PowerShell with OpenSSH installed) to copy to Mac's user folder:

```powershell
# from Windows (PowerShell)
scp -r C:\Users\admin\Desktop\biochem-poster\algae_box your-mac-username@mac-hostname:/Users/your-mac-username/Projects/
```

Option C. Use `rsync` from Mac to pull files (recommended for large meshes):

```bash
# from Mac terminal
rsync -avz --progress admin@windows-host:/cygdrive/c/Users/admin/Desktop/biochem-poster/algae_box ~/Projects/algae_box
```

Option D. Use cloud storage (Dropbox / Google Drive) if network transfer is restricted.

---

## 5 — Quick verification steps on mac
1. Check Python
```bash
python3 --version
pip3 install -r requirements.txt
```
2. Verify ParaView `pvpython` runs the postprocessing script
```bash
/Applications/ParaView.app/Contents/bin/pvpython paraview_postprocess.py
# or open ParaView GUI and run the script via View -> Python Shell -> Run Script
```
3. If using Docker for OpenFOAM, mount the case folder and run `./Allrun` inside the container.

---

## 6 — Running OpenFOAM with Docker (example)
```bash
# on Mac, where CfdOF is at ~/Projects/algae_box/CfdOF
docker run -it --rm -v "$(pwd)/CfdOF:/home/openfoam/case" openfoam/openfoam2312 bash
# inside container
cd case
./Allrun
```

---

## 7 — Git commit & push (short guidance)
After copying the files to the Mac and verifying, on the Mac run:

```bash
cd ~/Projects/algae_box
git status
git add TRANSFER_TO_MAC.md
git commit -m "Add transfer and mac setup instructions"
git push
```

If the repository doesn't have a remote configured, add it with:

```bash
git remote add origin <your-remote-url>
git push -u origin main
```

---

## 8 — Notes & next steps
- If you want to run full OpenFOAM natively (no Docker), we can prepare a Homebrew-based install list, but expect platform-specific troubleshooting.
- For heavy HPC or longer CFD runs consider moving the compute to a Linux VM or remote cluster and use VS Code Remote SSH for editing.

---

If you'd like, I will now commit this file to the repo and attempt to push it. If you want me to push, please confirm that the current workspace git remote is ready (or I can attempt the push and report errors).