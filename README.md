# Heran / Hanny Stand Fan → Home Assistant (ESP32-C3)

Make a cheap **Hanny / Heran DC stand fan** smart — a real Home Assistant `fan`
entity with **continuously variable speed** and **oscillation**, while the
**physical buttons still working** (a design goal — see the status note below).

This is done with a small **ESP32-C3** that taps into the fan's internal
low‑voltage control bus. No cloud, no app — local ESPHome + Home Assistant.

> 🚧 **Status — work in progress, NOT yet hardware-tested.** The teardown,
> measurements, and firmware are complete on paper, but nothing has been
> bench/hardware-validated yet. In particular the **PWM logic level (3.3 vs 5 V)
> and frequency are unverified** — you must measure them on your own fan before
> wiring. Treat every value here as a starting point, not a proven fact.
>
> ⚠️ **Safety:** the fan's power board is mains-powered. This mod only touches the
> **isolated 24 V secondary** side — **never** the mains/SMPS primary. If you are
> not comfortable working safely inside a mains appliance, don't. You do this at
> your own risk (see the disclaimer at the bottom).

---

## Will this work for my fan?

This was reverse-engineered from a **Hanny (www.hanny.com.cn)** DC stand fan.
Yours is likely the same platform if, on teardown, you find these markings
(photos are in [`pcb_1/`](pcb_1/) and [`pcb_2/`](pcb_2/)):

- Control/display board: **`KB-3151C`**, **`FY-HG-FLD35-16BR`**
- Power board: **`E355240` / `YF-1`**, transformer **`HYL16H/100-240V`**, `PCB181020L1`
- In-motor BLDC driver: **`FK-EGP00962`**
- Oscillation motor: **`TYJ50-8`** synchronous (24 V~, 2.5 rpm)
- A 5-pin control harness **`CN2`** labelled **`PWM · GND · +24V · OSC-A · OSC-B`**

Even if your board differs, the **method** (take over the motor PWM, reuse the
board for the AC oscillation motor) transfers to most similar DC fans.

---

## How it works (the short version)

The fan has 3 PCBs. The control board sends the motor a **logic-level PWM** (likely
3.3 V — unverified) speed
command on `CN2` and drives a **24 V AC synchronous** oscillation motor on
`OSC-A/OSC-B`. So:

- **Speed** → the ESP32 sits in the middle of the PWM line and, by default,
  **mirrors** the stock board (physical buttons still work). When you set a speed
  in Home Assistant it **overrides**; a physical button press hands control back.
- **Oscillation** → left to the stock board (it generates the AC the synchronous
  motor needs); the ESP just **taps the 摇头/SW5 button** through an optocoupler.

Full teardown + measurements: **[HA_MOD_NOTES.md](HA_MOD_NOTES.md)**.
Wiring + parts: **[BUILD_GUIDE.md](BUILD_GUIDE.md)**.

---

## What you need

- ESP32-C3 (this repo uses an **ESP32-C3 SuperMini**, see [`esp32/`](esp32/))
- 24 V→5 V buck converter (MP1584 / "mini-360")
- 1× PC817 optocoupler; resistors 330 Ω, 100 Ω, 2× 10 kΩ; 1× 1 µF capacitor; 0.5 A inline fuse; wire
- *(optional insurance)* a BSS138 level shifter — only if PWM turns out to be 5 V
- Home Assistant with the ESPHome add-on
- A **multimeter** (ideally with **Hz/duty** mode) to verify the PWM before wiring

Full bill of materials: [BUILD_GUIDE.md §1](BUILD_GUIDE.md).

---

## Step-by-step

### Phase 1 — Bench the ESP (no fan, ~15 min)
*(Breadboard is fine here — but it's bench-only; the final build must be soldered. See BUILD_GUIDE.md §2d.)*
1. Install the **ESPHome** add-on in Home Assistant.
2. Copy [`esphome/heran-fan.yaml`](esphome/heran-fan.yaml) into ESPHome, and copy
   [`esphome/secrets.yaml.example`](esphome/secrets.yaml.example) → `secrets.yaml`
   and fill in your Wi-Fi + API key.
3. **Flash over USB-C.** If the SuperMini isn't detected on the first flash:
   **hold BOOT, tap RST, release BOOT**, then flash.
4. Confirm a **"Fan"** entity and a **"Toggle Oscillation"** button appear in HA.
5. **Verify outputs with a multimeter (still no fan):** meter on **GPIO4 → GND**,
   raise the HA speed → the average voltage should climb (~0.8 V → ~3.0 V).
   Pressing "Toggle Oscillation" should briefly pulse **GPIO5**.

### Phase 2 — Wire into the fan (power OFF)
6. Open the fan base/head; find the **`CN2`** harness (`PWM/GND/+24V/OSC-A/OSC-B`).
7. Follow **[BUILD_GUIDE.md](BUILD_GUIDE.md)** Tables A–C + §5b (Option B):
   - **Cut** the `PWM` wire. Motor side → **GPIO4** (+ ~10 kΩ pull-down to GND);
     control-board side → **RC low-pass (10 kΩ+1 µF) → GPIO3** (mirror input).
     ⚠️ First confirm the PWM's real high level ≤ 3.3 V (Section 4 of the notes);
     if it's 5 V, add proper level translation — a series resistor is not enough.
   - `GND` common to the ESP; `+24V` → **fuse** → **buck** → set buck to **5.0 V**
     → ESP `5V` pin.
   - `OSC-A/OSC-B` pass through untouched.
   - **PC817** across the **SW5 (摇头)** button pads; LED side ← **GPIO5** (330 Ω).
8. Double-check: one common ground; buck verified at **5.0 V** before connecting
   the ESP; the cut control-side wires are insulated.

### Phase 3 — Power up & test
9. Power on. The ESP boots in **mirror** mode → the fan obeys the **physical panel**.
10. **Speed:** set a speed in HA → the motor follows (override). Press the physical
    **风速** button → control returns to the panel. 
11. **Oscillation:** press the **Toggle Oscillation** button → head swings;
    press again → stops.
    (If nothing, swap PC817 pins 3/4 — polarity.)
12. **Fail-safe:** reboot the ESP → the fan should follow the panel (motor off if
    the panel is off).

### Phase 4 — Tune
13. If the fan **doesn't respond to the PWM**: it may be 5 V logic — insert the
    **BSS138 level shifter** on GPIO4→PWM. If it responds oddly, try a different
    `pwm_freq` (1000/5000/20000 Hz) in the YAML.
14. Adjust `min_duty` / `max_duty` in the YAML to match your measured L1/L12 duty.

---

## Repo structure

```
README.md            – this file
BUILD_GUIDE.md       – bill of materials, wiring tables, test & safety
HA_MOD_NOTES.md      – full teardown reverse-engineering + all measurements
NOTES.md             – pcb_1 board inventory (control + power boards)
CONTRIBUTING.md      – how to report results / submit changes
LICENSE              – MIT (code); docs & photos CC BY 4.0
esphome/
  heran-fan.yaml     – ready-to-flash ESPHome config (Option B)
  secrets.yaml.example
esp32/               – ESP32-C3 SuperMini board photos + pinout notes
pcb_1/               – control + power board photos
pcb_2/               – fan-head motor driver + motor photos
```

---

## Status

Reverse-engineering and measurements are **done** (see `HA_MOD_NOTES.md`):
- PWM: active-high, 12 levels, ~24%→90% duty. **Logic level (3.3 vs 5 V) and
  frequency still to be confirmed on a scope/Hz meter before wiring.**
- Oscillation: `TYJ50-8` AC synchronous, symmetric ~50/60 Hz (~16.5 V), reused via SW5.
- Firmware: Option B config provided; **bench/hardware bring-up in progress**.

Contributions welcome — if you have the same (or a similar) fan, PRs with your
measurements, board photos, and tweaks are appreciated. See
[CONTRIBUTING.md](CONTRIBUTING.md).

---

## License & disclaimer

**Code** (the ESPHome YAML) is released under the **MIT License** (see
[LICENSE](LICENSE)). **Documentation and photos** are © the contributors and
licensed **CC BY 4.0**.

*This is an independent, unofficial project — not affiliated with, authorized by,
or endorsed by Hanny/Heran. Brand names and board markings are referenced only to
identify the appliance.*

**Disclaimer:** This project involves opening and modifying a mains-powered
appliance. It is provided **as-is, with no warranty**. Mains electricity and
modified appliances can cause **electric shock, fire, injury, or death**. You are
solely responsible for your own safety and for any damage. Only proceed if you are
qualified and comfortable doing so, and always work on the **isolated low-voltage
side** with the fan unplugged while wiring.
