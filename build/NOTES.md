# build — parts on hand & inventory check

Photos of the components gathered for the mod (metadata stripped). Checked against
the BOM in [`../BUILD_GUIDE.md`](../BUILD_GUIDE.md) §1.

## ✅ Present (seen in the photos)
| Part | Notes |
|------|-------|
| ESP32-C3 SuperMini | already flashed with the firmware (not in these photos) |
| MP1584 **24→5 V buck** | `parts_kit.jpg` — set output to **5.0 V** before use |
| **PC817 optocoupler** | the small black 4-pin part — looks **SMD**; usable but fiddlier on perfboard than the DIP version |
| Through-hole **resistors** (3 values) | three bagged values — **confirm they are 330 Ω, 100 Ω, 10 kΩ** (need ≥2× 10 kΩ) |
| **Capacitors** (yellow) | **confirm one is 1 µF** (the RC-filter cap) |
| **Glass fuses** | present — **confirm ~0.5 A rating** |
| **Perfboard 20×80 mm** | for the permanent build (Phase 2) ✓ |

## ⚠️ Missing / still needed
- **Hook-up wire** (silicone/solid) — **required**, not in the photos.
- **Heatshrink tubing** — **required** to insulate every joint.
- **Inline fuse holder / clips** — fuses are present but no holder is shown.
- **Multimeter with Hz/duty mode** — needed for the pre-wiring PWM verification gate
  (any DMM works for voltages; Hz/duty settles the 3.3 vs 5 V question).

## 🔎 To confirm (can't read from the photos)
- Resistor values = **330 Ω / 100 Ω / 10 kΩ** (and at least **two** 10 kΩ).
- Capacitor value = **1 µF**.
- Fuse rating ≈ **0.5 A**.

## Optional (nice to have)
- **5-pin JST matching CN2** → reversible interposer (`../BUILD_GUIDE.md` §2b).
- **Female header strip** → socket the ESP32-C3 so it stays reflashable on the perfboard.

## ❗ Important finding from the clearer board photo
`../pcb_1/control_back_clear.jpg` shows a **"+5V" rail** silk next to the control-board
MCU. That raises the chance the **PWM is 5 V logic, not 3.3 V** — so the
*verify-before-wiring* gate matters even more:
- If PWM is **5 V**, the **GPIO3 mirror input needs a resistor divider** (you have
  resistors for this) and the **GPIO4 PWM output needs level translation up to 5 V**
  (e.g. a small MOSFET/transistor stage or a 5 V-capable buffer — a BSS138 module
  is the usual part; not seen in the kit).
- Measure the **actual PWM high level** first and decide (see `../HA_MOD_NOTES.md` §4).

## Photo index
| File | Shows |
|------|-------|
| `parts_kit.jpg` | full kit incl. glass fuses |
| `parts_kit_alt.jpg` | same kit, alt angle |
| `../pcb_1/control_front_clear.jpg` | clear control-board front (buttons/LEDs/IR, CN1/CN2) |
| `../pcb_1/control_back_clear.jpg` | clear control-board back (MCU, "+5V" rail) — replaces the old low-res shot |
