# Algae Settling Tank - Design Overview

## Semi-Auto Harvest System (Option B Implementation)

```
         ╔═══════════════════════╗
         ║  OVERFLOW PIPE        ║←── Clean water exits here
         ║  (35cm height)        ║
    ╔════╩═══════════════════════╩════╗
    ║                                 ║
    ║   CLEAN WATER ZONE (top)        ║  ← Reused water (90%)
    ║   Low turbidity, high pH        ║
    ║═════════════════════════════════║  ← Overflow level
    ║                                 ║
    ║   GROWING ZONE (middle)         ║  ← Pump circulates here
    ║   Algae suspended, turbidity    ║     during GROWING state
    ║   increases, photosynthesis     ║
    ║                                 ║
    ║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║
    ║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║
    ║▓▓▓▓▓▓ SETTLING ZONE ▓▓▓▓▓▓▓▓▓▓▓║  ← Algae concentrates
    ║▓▓▓▓▓▓ (cone bottom) ▓▓▓▓▓▓▓▓▓▓▓║     during SETTLING state
    ║▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓║
     ╚════════════╦══════════════════╝
                  ║
                  ║  DRAIN VALVE (25mm)
                  ║  Opens during HARVESTING
                  ║
                  ▼
              [Collection
               Container]
```

## State Machine Flow

```
┌──────────────┐
│   GROWING    │  Pump ON, Circulating
│ Turb: 36→350 │  Algae multiply
│ Days: 0→3    │  TDS consumed slowly
└──────┬───────┘
       │ Turbidity ≥ 350 NTU
       ▼
┌──────────────┐
│   SETTLING   │  Pump OFF, Gravity settling
│ Timer: 60min │  Algae sink to cone
│ Auto-running │  Display countdown
└──────┬───────┘
       │ 60 minutes elapsed
       ▼
┌──────────────┐
│ HARVEST_READY│  Paused, waiting
│  [FLASHING]  │  "Place bucket & press button"
│ User action  │  Green button enabled
└──────┬───────┘
       │ User presses HARVEST button
       ▼
┌──────────────┐
│  HARVESTING  │  Valve OPEN
│ Timer: 30sec │  Draining algae
│ Auto-running │  Progress shown
└──────┬───────┘
       │ 30 seconds elapsed
       ▼
┌──────────────┐
│   RESTART    │  Reset values
│ Refill water │  Algae: 10, Turb: 36
│ Add nutrients│  Back to GROWING
└──────┬───────┘
       │
       └──────────────┐
                      │
         ┌────────────▼───────────┐
         │   Back to GROWING     │
         └───────────────────────┘
```

## Physical Design Specs

| Component | Dimension | Purpose |
|-----------|-----------|---------|
| Total Height | 400mm (40cm) | Total tank |
| Diameter | 300mm (30cm) | Main cylinder |
| Cone Height | 150mm (15cm) | Settling zone |
| Drain | 25mm (1") | Harvest valve |
| Overflow | 350mm height | Water level control |
| Wall Thickness | 3mm | Structural |
| Volume | ~28 Liters | Total capacity |
| Collection Zone | ~10 Liters | Algae concentrate |

## OLED Display States

### GROWING State
```
┌─────────────────┐
│Day 1 08:00 [DAY]│
│────────────────│
│Algae: 45 units │
│Turb: 92/350 NTU│
│pH: 7.15 T:26.5C│
│Nutrients: 85%  │
│Harvest:[===   ]│
│        32%     │
└─────────────────┘
```

### SETTLING State
```
┌─────────────────┐
│== SETTLING ==  │
│Pump: OFF       │
│Algae sinking...│
│                │
│Time left: 45:23│
│                │
│Turb: 352 NTU   │
└─────────────────┘
```

### HARVEST_READY State
```
┌─────────────────┐
│  HARVEST        │
│  READY!         │
│                 │
│Place bucket below│
│Press GREEN button│
└─────────────────┘
```

### HARVESTING State
```
┌─────────────────┐
│== HARVESTING ==│
│Valve: OPEN     │
│Draining algae..│
│                │
│    25 sec      │
│                │
│Collecting...   │
└─────────────────┘
```

## Why This Design Works

### ✅ Advantages
1. **Gravity-based** - Reliable, no complex machinery
2. **90% water reuse** - Only drain concentrated algae
3. **User control** - Safe, prevents spills
4. **Simple operation** - One button press
5. **Optimal timing** - System monitors turbidity 24/7
6. **Cone shape** - Concentrates algae at single point
7. **Overflow** - Maintains water level automatically

### 🔧 Real Components Needed
- ESP32 + sensors (already simulated)
- 12V water pump (for circulation during GROWING)
- 12V solenoid valve (for drain during HARVESTING)
- 2-channel relay (control pump + valve)
- PVC cone tank (see FreeCAD model)
- Collection bucket

## FreeCAD Model

Open `hardware/algae_settling_tank.py` in FreeCAD to see:
- 3D model with dimensions
- Transparent view showing internal zones
- Water level indicators
- Algae settlement visualization

**To view:**
```bash
# Install FreeCAD first (https://www.freecad.org/)
freecad hardware/algae_settling_tank.py
```

## User Experience

**Day 1-3:** Check phone, see algae growing (automatic)
**Day 3:** Phone alert: "HARVEST READY"
**User:** Places bucket, presses green button
**30 seconds:** Algae drains (automatic)
**System:** Auto-refills, restarts cycle

**Total user effort:** < 2 minutes every 3 days! 🎯
