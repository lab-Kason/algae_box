# Transfer & Setup Guide — Move project from Windows to macOS

This document lists required applications, VS Code extensions, files to transfer, and quick commands to set up the project on a clean macOS machine (assumes only VS Code is installed). It also summarizes current progress of the project.

---

## 1 — Current progress (snapshot)
- FreeCAD CAD model and geometry generation: `Algae_tank_full_system.py` (FreeCAD macro) completed.
- Mesh and OpenFOAM case: directory `CfdOF/case` with converged `simpleFoam` solution (steady-state). Gmsh mesh exported and converted to OpenFOAM.
- Postprocessing script: `paraview_postprocess.py` available to load the `.foam` case and generate slices + streamlines in ParaView.
- Other useful code & data: `modules/`, `simulations/`, `streamlit_qr/`, `data/algae_log.csv`.

In-repo portable CFD package now included (for direct git transfer to Mac):
- `portable_artifacts/CfdOF_case/` (trimmed runtime case: `0`, `constant`, `system`, processor `constant` + final `2000` timestep, logs, run scripts)
- `portable_artifacts/CfdOF_meshCase/` (meshCase export from Gmsh/OpenFOAM)

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

## 8 — Restore CFD folders on Mac from git-tracked artifacts
This repository now includes a trimmed CFD package under:
- `portable_artifacts/CfdOF_case/`
- `portable_artifacts/CfdOF_meshCase/`

Use the helper script to rebuild `CfdOF/case` and `CfdOF/meshCase` after clone:

```bash
cd ~/Projects/algae_box
chmod +x restore_case_on_mac.sh
./restore_case_on_mac.sh
```

Optional:

```bash
# show what would happen without writing files
./restore_case_on_mac.sh --dry-run

# overwrite without creating backups
./restore_case_on_mac.sh --no-backup
```

---

## 9 — GitHub Desktop workflow on Mac (recover everything)
1. Install GitHub Desktop on macOS and sign in to your GitHub account.
2. Click **File -> Clone repository...**
3. Choose repository: `lab-Kason/algae_box`
4. Choose local path, for example: `/Users/<you>/Projects/algae_box`
5. Click **Clone**.
6. Open Terminal in that folder and run:

```bash
cd /Users/<you>/Projects/algae_box
chmod +x restore_case_on_mac.sh
./restore_case_on_mac.sh
```

After this step, you will have:
- `CfdOF/case`
- `CfdOF/meshCase`

Then continue with ParaView/OpenFOAM as documented above.

---

## 10 — WhatsApp fallback bundle
If GitHub is unavailable, use the split archive stored in:
- `whatsapp_bundle/algae_box_portable.tar.gz.part01`
- `whatsapp_bundle/algae_box_portable.tar.gz.part02`

Reassemble on the receiving machine:

```bash
cat algae_box_portable.tar.gz.part* > algae_box_portable.tar.gz
tar -xzf algae_box_portable.tar.gz
```

Send `part01` first, then `part02`.

---

## 11 — Notes & next steps
- If you want to run full OpenFOAM natively (no Docker), we can prepare a Homebrew-based install list, but expect platform-specific troubleshooting.
- For heavy HPC or longer CFD runs consider moving the compute to a Linux VM or remote cluster and use VS Code Remote SSH for editing.

---