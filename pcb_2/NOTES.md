# pcb_2 — Fan head (motor + in-motor driver board)

5 photos taken 2026‑09‑27 ~23:24–23:28 of the **fan head**, after removing the
motor from the housing. These reveal a **third PCB** (the BLDC motor driver, built
into the motor) plus the two motors — important because they **confirm what the
`CN2` bus actually drives**.

> See `../pcb_1/` for the control/display board and power supply board photos,
> and `../HA_MOD_NOTES.md` for the Home‑Assistant control plan (updated with these
> findings).

---

## What's in the head

### PCB 3 — In‑motor BLDC driver board  `FK‑EGP00962`
A round green PCB mounted on the back of the main motor, around the shaft.

- Markings: `FK‑EGP00962`, `PbF` (lead‑free), fuse `F002`.
- **IC markings (recorded 2026-09-27; no public datasheet found):**
  - Main controller/pre-driver (QFN): `44132  207z26` (`207z26` ≈ date/lot code).
  - 3× identical ICs: `NL1115` — one per phase (`HU/HV/HW`), i.e. Hall latches /
    per-phase switches → confirms a **sensored 3-phase BLDC** stage.
  - These are abbreviated house-marks (typical of low-cost fan ICs); they confirm
    "PWM = logic speed input" but are **not needed** for the mod (measure PWM).
- **This is a self‑contained BLDC driver + controller** for the main fan motor:
  - A microcontroller / motor‑driver IC (`IC1`, QFN) + gate/pre‑driver + phase FETs.
  - Hall‑sensor nodes `HU / HV / HW` (silk near the top edge) → sensored BLDC.
  - RC/decoupling passives, `C2 47µF`, etc.
- **`CN1` control connector** (bottom edge) — pin silk reads:
  `SS · F.G · PWM · GND · … · 24V`, with an adjacent programming header
  `VCC · GND · E.PWM · E.SS · E.FG · PROG`.
  - `24V` / `GND` — motor supply.
  - `PWM` — **logic speed command input** (this is the far end of the control
    board's `CN2 PWM`).
  - `F.G` — tacho pad, **NOT connected in the harness** (no stock RPM feedback).
    Measured directly on the pad: **~1.1 V DC at level 1** → the driver **does**
    generate F.G (it's alive). It is a **frequency signal** (pulse train ~50% duty,
    high ~2.2 V), so the DC average stays ~constant across speeds — only the
    frequency rises with RPM. Reading RPM needs an **Hz** measurement, not DC.
  - `SS` — **NOT connected** (unused; not needed for speed/enable).
  - `E.PWM/E.SS/E.FG/PROG` — factory programming/test pads (unused).
- **Confirmed by inspection:** the only wires used between control-board `CN2`
  and driver `CN1` are **`PWM`, `GND`, `24V`** (they match pin-for-pin by the
  labels printed on both connectors). `F.G` and `SS` carry no wire.

**⇒ Key confirmation:** the fan's main motor has an **integrated driver**, and the
real interface is a simple **3-wire logic PWM** (`24V` / `GND` / `PWM`). That makes
clean ESP speed control straightforward. Note: `F.G` RPM feedback is **not stock-
wired**, but the pad exists — you *could* solder a tap to it later if you want RPM.

### Main fan motor
- DC 24 V brushless (label side shows a `MINEBEA` / DC24V marking; the `FK‑EGP00962`
  board is its integrated driver). Drives the fan blade.

### Oscillation motor — `TYJ50‑8` synchronous
- Grey can motor with metal bracket, separate from the blade motor.
- Label: `SYNCHRONOUS MOTOR  爪极式永磁同步电动机  TYJ50‑8`,
  `24V~  50/60Hz`, `2.5/3 r/min  CW/CCW`, `4W (in) / 0.3W (out)`, RoHS,
  Foshan Shunde Hengxing Micro Motor Co., Ltd, `NO: 2022 04 26`.
- Slow geared motor that swings the head. Driven by the control board's
  **`OSC‑A` / `OSC‑B`** lines. **Measured ~80 Ω across A–B** = its coil (A/B are the
  two motor leads). It is a **claw-pole PM AC synchronous** motor (`24V~ 50/60Hz`):
  it runs **only on true ~50/60 Hz AC**, which the stock board synthesizes from the
  24 V DC bus. **DC/PWM will not turn it.** Simplest mod = let the stock board keep
  driving oscillation and tap the `摇头`/SW5 button. Direction is fixed by a crank.

**⇒ Key implication for the mod:** oscillation is a **~24 V synchronous motor**, so
`OSC‑A/OSC‑B` almost certainly carry **≈24 V drive (power), not logic** — likely the
two leads for CW/CCW direction / run. Driving oscillation from an ESP means
**switching 24 V** (relay or H‑bridge), *not* a logic GPIO. This matches the Codex
review's warning that the OSC lines could be power drive.

---

## Photo index (pcb_2)

| File | Subject | Notes |
|------|---------|-------|
| `P_20260927_232419.jpg` | BLDC driver board `FK‑EGP00962` (in‑motor) | Full view; CN1 pinout + ICs. |
| `P_20260927_232424.jpg` | BLDC driver board `FK‑EGP00962` | **≈ duplicate of 232419.** |
| `P_20260927_232815.jpg` | Main motor label side (Minebea DC24V) | Shows motor can + harness. |
| `P_20260927_232832.jpg` | Oscillation motor `TYJ50‑8` (synchronous) | Label readable. |
| `P_20260927_232836.jpg` | Oscillation motor `TYJ50‑8` | **≈ duplicate of 232832.** |

### Duplicate groups
- BLDC driver board: `232419` ≈ `232424`.
- Oscillation motor: `232832` ≈ `232836`.
- Main motor label: `232815` (unique).

---

## Revised full system (now 3 PCBs)
1. **Power supply board** (base) — mains → 24 V. `pcb_1`.
2. **Control / display board** (head front) — MCU, buttons, LEDs, IR; outputs `CN2`
   (`PWM`, `OSC‑A/B`, +24V, GND). `pcb_1`.
3. **In‑motor BLDC driver `FK‑EGP00962`** (this folder) — takes `PWM` (logic) + 24V,
   drives the blade motor, returns `F.G` tach. The `TYJ50‑8` synchronous oscillation
   motor is driven directly by `OSC‑A/B`.
