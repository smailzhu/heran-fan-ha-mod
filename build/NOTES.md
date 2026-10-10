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
- **Level shifter 3.3→5 V** (74AHCT125 / BSS138) — **required** (this fan is 5 V); not in the kit.
- **Multimeter** — any DMM for voltages; Hz/duty or a diode+cap trick confirms the PWM peak.

## 🔎 To confirm (can't read from the photos)
- Resistor values = **330 Ω / 100 Ω / 10 kΩ** (and at least **two** 10 kΩ).
- Capacitor value = **1 µF**.
- Fuse rating ≈ **0.5 A**.

## Optional (nice to have)
- **5-pin JST matching CN2** → reversible interposer (`../BUILD_GUIDE.md` §2b).
- **Female header strip** → socket the ESP32-C3 so it stays reflashable on the perfboard.

## ❗ CONFIRMED: this fan is 5 V logic
The control-board **MCU rail measures 5 V** (`../pcb_1/control_back_clear.jpg` "+5V"
silk). So the PWM is **5 V logic** → build the **§2d (5 V) variant**:
- **GPIO3 mirror input:** add a **resistor divider** (you have resistors) so the ADC
  stays ≤ ~3.3 V.
- **GPIO4 output:** add **level translation 3.3 → 5 V** — a **74AHCT125** (preferred)
  or **BSS138** module. **This part is NOT in the current kit — order it.**
- Stock duty range at 5 V ≈ **16 % (L1) → 60 % (L12)** (already set in the config).
- (For 100 % certainty, confirm the PWM pin peak directly — diode+cap method, §4.)

## Photo index
| File | Shows |
|------|-------|
| `parts_kit.jpg` | full kit incl. glass fuses |
| `parts_kit_alt.jpg` | same kit, alt angle |
| `../pcb_1/control_front_clear.jpg` | clear control-board front (buttons/LEDs/IR, CN1/CN2) |
| `../pcb_1/control_back_clear.jpg` | clear control-board back (MCU, "+5V" rail) — replaces the old low-res shot |
