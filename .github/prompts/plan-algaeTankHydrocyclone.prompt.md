## Plan: 20L Blender Algae Tank Simulation & Hydrocyclone Collection

This plan revamps your existing 3D simulation to correctly display a precise 20L cube model, ripping out the broken bubble simulation and replacing it with realistically circulating algae particles. It also pivots the hardware collection approach to use a hydrocyclone separator based on your boss's requirements—meaning when turbidity peaks, a high-pressure pump forces the dense algae slurry through a hydrocyclone, cleanly saving the algae and cycling water back.

**Steps**
1. **Configure 20L Cube in Blender**: Modify the script geometry settings so the domain volume equals exactly 20 liters. Since $1\text{L} = 1000\text{cm}^3$, a perfect cube of $20,000\text{cm}^3$ is $27.14\text{cm} \times 27.14\text{cm} \times 27.14\text{cm}$ ($0.2714\text{m}$).
2. **Setup Algae Flow Demo**: Strip out the non-working air bubble logic (tube generation, bubble emitters). Replace it with a standard Particle System emitting from a *Random* volume throughout the tank. This allows Blender's Mantaflow fluid dynamics to push the "algae" particles naturally with the water currents.
3. **Hardware & Logic Updates (Hydrocyclone)**: Add a mini-hydrocyclone separator to your setup. Update the state machine: when the turbidity sensor crosses the threshold, open the drain valve and turn on the pump. The algae/water mix gets forced through the hydrocyclone (spinning the heavy algae out), and the valve closes when the tank turbidity drops back to baseline.

**Relevant files**
- `simulations/blender_tank_setup.py` — Change `TANK_X, TANK_Y, TANK_Z` to `0.2714`. Delete lines referencing `TUBE` variables, and swap out the bubble particle logic with standard volume-based algae emitter.
- `TAOBAO_SHOPPING_LIST.md` — Insert a "Mini Hydrocyclone Separator" (often sold as a cyclone dust collection cone that works with fluids) and ensure the pump specified has enough PSI (at least a 60W diaphragm pump) to create the centrifugal force required.
- `hardware/SETTLING_TANK_DESIGN.md` — Update the state machine flowchart from "gravity settling" to "active cyclone pumping" flow.

**Verification**
1. Check the dimensions of the generated target object in Blender to confirm it hits exactly $0.2714\text{m}$ in Scale XYZ.
2. Play the Mantaflow timeline cache; verify random green particles spawning in the water and flowing cleanly around without the old bubbly physics interfering.
3. Verify updated harvest flow handles a high-PSI pump start alongside the solenoid opening.

**Decisions**
- Removing `buoyancy_flow.py` dependencies and bubble settings from Blender because they were distracting and breaking the flow.
- A hydrocyclone requires pressure. Standard micro 12v pumps (like those currently requested on the list) are often too weak, so the Taobao list will be upgraded.