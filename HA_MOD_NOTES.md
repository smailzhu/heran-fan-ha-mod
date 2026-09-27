# Home Assistant Mod — "Cleanest" Option (direct motor-board drive)

Goal: get a **true analog `fan` entity in Home Assistant** (continuous speed %,
oscillation on/off) instead of just emulating button presses. The cleanest way
to do that on this fan is to **take over the `CN2` control bus** and drive the
motor/oscillation assembly directly with an ESP32 running ESPHome.

> **The fan has 3 PCBs** (updated after the fan-head teardown, see `pcb_2/NOTES.md`):
> a **power supply board** (base), a **control/display board** (head), and an
> **in-motor BLDC driver board `FK-EGP00962`** on the main motor. The head photos
> **confirm the key assumptions**: `CN2 PWM` is a **logic speed command** into the
> BLDC driver (main-motor link is just `24V/GND/PWM`; `F.G`/`SS` are unused), and
> **`OSC-A/OSC-B`
> drive a 24 V synchronous oscillation motor (`TYJ50-8`)** — i.e. the OSC lines are
> **power drive, not logic**. See §2 and §3 for how this shapes the plan.

> Companion docs: `NOTES.md` (pcb_1: control + power boards),
> `pcb_2/NOTES.md` (fan head: motor driver + motors), and
> **`BUILD_GUIDE.md`** (the ready-to-build ESP32-C3 wiring + ESPHome package).

---

## 1. System architecture (as reverse-engineered from the photos)

Three boards + two motors, connected by low-voltage harnesses:

```
   MAINS (100-240 V)
        |
        v
 +------------------------------+   DC out
 | POWER SUPPLY board (base)     |---- +24V / GND -------+
 | E355240 / YF-1 / PCB181020L1  |  (2-pin harness)      |
 | xfmr HYL16H/100-240V (SMPS)   |                       |
 +------------------------------+                        |
                                                         v  CN1 (2-pin)
 +-------------------------------------------------------------+
 | CONTROL / DISPLAY board (head)   (the BRAIN)                |
 | KB-3151C / FY-HG-FLD35-16BR                                 |
 | front: buttons SW1-5 + LEDs + IR rx + buzzer               |
 | back:  MCU (wide SOP) + SMT                                 |
 +-----------------+--------------------------+---------------+
      CN2 pin1 PWM (+24V/GND)          CN2 OSC-A / OSC-B
           | (logic speed cmd)              | (~24V drive, CW/CCW)
           v                                v
 +------------------------------+   +----------------------------+
 | IN-MOTOR BLDC DRIVER          |   | Oscillation motor TYJ50-8  |
 | FK-EGP00962 (on main motor)   |   | synchronous 24V~ 2.5rpm    |
 | CN1: 24V GND PWM F.G SS        |   | CW/CCW, 4W                 |
 |  -> drives blade motor,       |   +----------------------------+
 |  (F.G/SS pads unused)         |
 +------------------------------+
```

**Key insight (now confirmed by the head photos):** the control/display board is
the *brain*. Its `CN2` bus splits into two very different things:
- **`PWM` -> a logic speed command** into the main motor's **integrated BLDC
  driver (`FK-EGP00962`)**. The main-motor link is just **`24V/GND/PWM`** (the
  driver's `F.G` tach and `SS` pads are unused/unwired). Clean, low-current input.
- **`OSC-A` / `OSC-B` -> ~24 V drive to a synchronous oscillation motor
  (`TYJ50-8`, CW/CCW)** - i.e. **power, not logic**. An ESP must *switch/reverse
  24 V* here (relay or H-bridge), never drive it from a GPIO.

So it is a *hybrid* bus: one clean logic line (PWM) + one power pair (OSC).

---

## 2. The `CN2` control bus

Silkscreen on the control/display board, left → right at the connector. The
"Function" column is now informed by the fan-head teardown (`pcb_2/NOTES.md`):

| Pin | Label   | Function                                                        |
|-----|---------|-----------------------------------------------------------------|
| 1   | `PWM`   | **Logic** speed command into BLDC driver `FK-EGP00962` (its `CN1 PWM`). The driver's `F.G` tach and `SS` pins are **not wired** (main-motor link = 24V/GND/PWM only). |
| 2   | `GND`   | Common ground                                                   |
| 3   | `+24V`  | 24 V rail (motor supply), passed from the power board           |
| 4   | `OSC-A` | **~24 V drive** to synchronous oscillation motor `TYJ50-8` (one lead / direction) |
| 5   | `OSC-B` | **~24 V drive** to `TYJ50-8` (other lead — CW/CCW pair)          |

`CN1` (control board) = 2-pin **+24V / GND** power input from the SMPS (power board).

> Note the asymmetry: **pin 1 is a clean logic input**, but **pins 4/5 are motor
> power** to a 24 V synchronous gearmotor. Treat the two halves of the plan
> differently (logic PWM vs. switched/reversed 24 V).

---

## 3. Control strategy

> **Updated after fan-head teardown.** The head photos resolve the biggest unknown
> the Codex review flagged: `CN2` is a **hybrid** bus, not uniform.
> - **`PWM` = logic** into the BLDC driver → **drive it directly** (still confirm
>   level/polarity/frequency in Section 4 before wiring).
> - **`OSC-A/OSC-B` = ~24 V motor power** to the `TYJ50-8` → **do NOT GPIO-drive**;
>   switch/reverse 24 V with a relay or H-bridge.
> - Still verify secondary/mains isolation (Section 4, Step 1) before probing.

### Decision tree (per signal)
```
SPEED  (CN2 pin 1, PWM)
  confirm PWM level/polarity/freq  → drive from ESP LEDC output (logic).  GO.
  (main-motor link is just 24V/GND/PWM; F.G/SS are unused/unwired)

OSCILLATION  (CN2 pins 4/5, OSC-A/OSC-B = the TYJ50-8 coil, ~80 Ω)
  TYJ50-8 is a claw-pole PM *AC synchronous* motor: it needs a genuine ~50/60 Hz
  AC field. It will NOT run on DC or arbitrary PWM (hums/overheats/stalls).
  From the 24 V DC bus the stock board *synthesizes* that AC across A–B.
   -> PREFERRED: leave oscillation to the stock board; toggle it by injecting the
      摇头/SW5 button (optocoupler). No AC synthesis needed. (hybrid, see below)
   -> FULL takeover: reproduce a *symmetric* ~50/60 Hz square-wave AC (full
      H-bridge, ~0 V DC offset) at the measured Vrms/frequency.
  measure AC-V (~24 Vrms), Hz (~50/60), DC-V (~0) across A–B first.

If any measurement contradicts the above (e.g. PWM is actually 24 V on a
load path), fall back to button+LED injection (Section 3a).
```

> **Recommended split (given oscillation needs AC):** the *speed* side is trivial
> to take over (3-wire logic PWM), but the *oscillation* side needs true ~50/60 Hz
> AC synthesis. Easiest robust design = **ESP owns speed (drive `PWM` directly) +
> reuse the stock board for oscillation** by tapping the `摇头/SW5` button through
> an optocoupler. You get a full HA `fan` + oscillation switch without building an
> AC drive. Only do full OSC takeover if you remove the control board (Variant C2).

Replace the control board MCU's `CN2` outputs (at least `PWM`) with an ESP32. Two
build variants:

### Variant C1 — Piggyback / override (reversible, recommended first)
- Leave both original boards in place and powered.
- Unplug the `CN2` harness from the **control/display** board and plug it into a
  small adapter driven by the ESP32. The ESP supplies `PWM`, `OSC-A`, `OSC-B`.
- **Power routing (blocker fix):** unplugging `CN2` from the control board also
  removes the `+24V`/`GND` that the control board was passing onto that harness.
  So you **must feed the `CN2` `+24V` and `GND` pins explicitly from the power
  board's DC output** (the same rail that fed `CN1`) — do **not** assume power
  still arrives on the unplugged connector. Verify polarity and common ground.
- Fully reversible: re-plug `CN2` into the control board to restore stock behavior.
- The physical buttons/remote stop affecting the motor (the control board is now
  disconnected from the motor lines), which is fine — HA becomes the controller.

### Variant C2 — Remove the control-board brain from the loop (cleanest end state)
- Leave only the **power supply board**; power the ESP + motor from its `+24V`.
- ESP32 becomes the only brain: HA `fan` entity → PWM; oscillation switch →
  OSC-A/B. (You can keep the control/display board physically in place but unused,
  or repurpose its `SW1–SW5`/LEDs on spare ESP GPIOs for local control later.)
- Slightly less reversible, but the tidiest result.

Either way the **power supply board is kept** (mains→24 V) and the **fan motor /
oscillation assembly is kept** — the ESP simply provides the PWM + OSC signals the
control-board MCU used to generate.

### 3a. Fallback — button + LED injection (use if CN2 is raw motor drive)
If measurements show `CN2` carries motor current, **do not touch it**; keep the
stock motor electronics (and its built-in soft-start / oscillation end-stops /
current limiting) and instead control the fan through the control board's *logic*:
- **Actuate** the isolated tactile buttons `SW1`–`SW5` from ESP GPIOs via
  optocouplers / analog switches (momentary "presses").
- **Sense** the status LEDs (`LED1`–`LED11`, `SLP`, `RHY`, oscillation) into ESP
  inputs so Home Assistant tracks the *actual* state (speed/timer/mode/oscillation).
- Trade-off: speed is limited to the stock Low/Med/High steps (not continuous),
  but all stock protections stay intact and nothing high-current is modified.
- This is also the safest **first experiment** and can be prototyped before any
  CN2 measurement (see also IR emulation as an even more reversible probe).

---

## 4. Bench measurements to take BEFORE building (critical)

The **functions** are now identified from the fan-head teardown (`pcb_2/NOTES.md`):
`PWM` = logic speed command into the `FK-EGP00962` BLDC driver (`F.G`/`SS` unused),
and `OSC-A/OSC-B` = ~24 V power to the `TYJ50-8` oscillation motor. What
remains is to **measure the electrical specifics** (levels, frequency, duty,
drive type) with a scope/meter on the running stock fan. **Order matters** — do
the unpowered/continuity checks first, then powered scope work, then go/no-go:

**Step 0 — unplugged (no power):**
- Photograph/label the `CN2` connector orientation before unplugging.
- Trace each `CN2` pin to its components and to the motor wires; note any
  MOSFETs, driver ICs, diodes, or oscillation limit switches on the motor side.
- Continuity: confirm `CN1`→`CN2` `+24V` and `GND` paths; measure resistance
  between the motor-side pins (but treat resistance **alone** as inconclusive).

**Step 1 — isolation check (before attaching an earth-referenced scope):**
- **Verify the `CN2`/secondary ground is truly isolated from mains** and confirm
  the secondary reference before clipping a grounded scope probe. If the
  reference is uncertain, use a **differential/isolated probe**. The power board
  contains live mains — this is a safety gate, not optional.

Then probe `CN2` against its `GND` pin while operating via the buttons:

1. **`PWM` logic level** — 3.3 V or 5 V high? → sets whether a level shifter is
   needed (ESP32 GPIO = 3.3 V). (Only `PWM` is logic; `OSC-A/B` are 24 V power —
   see item 3, do **not** probe them expecting logic.)
2. **`PWM` characteristics:**
   - Frequency (typical 1–25 kHz).
   - Polarity / active sense (does higher duty = faster, or inverted?).
   - Duty at each speed (Low/Med/High) → build the speed map.
   - Minimum duty that actually spins the motor (startup threshold).
   - Is "off" = 0 % duty, steady low, or steady high?
   - **Sanity check** (should already hold given the `FK-EGP00962` driver): a
     3.3/5 V low-current waveform ⇒ logic input (**GO**). If instead you see a
     switched **24 V** load-current waveform, stop and use **Fallback 3a**.
3. **`OSC-A` / `OSC-B` drive** — measured **~80 Ω A–B** (= the `TYJ50-8` coil).
   With oscillation ON, across **A–B**: read **AC-V** (expect ~24 Vrms), **Hz**
   (expect ~50/60 Hz), **DC-V** (≈0 ⇒ symmetric full-bridge; nonzero ⇒ half-bridge).
   Confirms the AC drive + its V/f. **Only needed if you go full-takeover**; the
   recommended hybrid (SW5-tap) reuses the stock AC drive and skips this.
4. **`F.G` tach — optional (not stock-wired).** Measured on the pad: **~1.1 V DC
   at level 1** ⇒ F.G is generated (alive). It's a **frequency** signal, so DC is
   ~constant across speeds; **RPM needs an Hz reading**. If you want RPM: tap the
   pad, add a **10 kΩ pull-up to 3.3 V** (clamp if >3.3 V), read **Hz**, then
   RPM = Hz × 60 ÷ (pulses/rev). pulses/rev unknown → calibrate. Otherwise skip.
5. **`+24V` rail** — confirm it is ~24 V and note current draw at off, startup,
   each speed, and oscillation (sizes the buck converter and any inline fuse).
6. Confirm `CN2` GND is common with the SMPS secondary GND (it should be).

**Go/no-go gate:** connect ESP outputs to `CN2` **only after** the receiving
circuit, required drive type, and safe power-up/off states are identified. A
generic BSS138 level-shifter + direct GPIO wiring is **not** justified until the
logic-bus interpretation is proven.

Record results in the tables below once measured.

>
> ⚠️ **Not yet proven:** these are **DC averages**, which a 3.3 V PWM, a 5 V PWM,
> **or a steady analog voltage** could all produce. The 3.3 V-logic reading below
> is the *likely* interpretation, **not confirmed**. Measure the **actual high
> level, frequency, and waveform** (Hz meter / scope) before wiring GPIO3/GPIO4.
> A series resistor is **not** overvoltage protection.

**Speed — `PWM` (logic), measured 2026-09-27 (DC avg, PWM→GND, motor unplugged):**

Fan has **12 speed levels** (no L13; **L12 is max**). `off` = **0 V** ⇒ PWM idles
low ⇒ **active-high**. Max L12 ≈ 2.9 V, so **logic level not fully pinned** by
averages alone: **3.3 V logic** ⇒ L12 ≈ 88% duty (most likely), or **5 V logic**
⇒ L12 ≈ 58%. Resolve with a duty-% / Hz meter reading at L12. Working assumption:
**3.3 V logic** (ESP drives PWM directly; add a level shifter only if 5 V).

| Level | Avg (V) | Duty | Level | Avg (V) | Duty |
|-------|---------|------|-------|---------|------|
| off   | 0.000   | 0%   | L7    | 1.815   | 55%  |
| L1    | 0.80    | ~24% (min-start) | L8 | 1.99 | 60% |
| L2    | 0.989   | 30%  | L9    | 2.12    | 64%  |
| L3    | 1.255   | 38%  | L10   | 2.23    | 68%  |
| L4    | 1.474   | 45%  | L11   | 2.64    | 80%  |
| L5    | 1.555   | 47%  | L12   | 2.98    | 90%  |
| L6    | 1.70    | 52%  | L13   | ~3.2 (confirm) | ~100% |

- **`+24V` rail:** measured **~23.8 V** (CN2 pin 3 → GND). ✅ ~24 V.
- **PWM frequency:** still unknown (meter gives duty via average, not freq). Pick
  ~1–20 kHz on the ESP and verify response, or read with a meter Hz mode.

**Oscillation — `OSC-A/OSC-B` (TYJ50-8 coil ~80 Ω), measured 2026-09-27:**

| Meas (oscillation ON)      | Value    | Interpretation |
|----------------------------|----------|----------------|
| AC across A–B (`V~`)        | ~16.5 V (connected) / 16.8 (open) | AC drive confirmed (meter under-reads square wave; actual ~17–24 V) |
| DC A(white)→GND             | ~0.55 V  | ~0 DC offset |
| DC B(brown)→GND             | ~0.60 V  | ~0 DC offset ⇒ **symmetric AC** (balanced drive) |
| Hz across A–B               | _____    | expect ~50/60 Hz (TODO) |
| coil resistance A–B (power off) | ~80 Ω | single-winding AC synchronous motor |

⇒ Symmetric ~50/60 Hz AC, ~17–24 V. Reproducing it needs a symmetric full-bridge
AC synth, so the **hybrid plan (reuse stock board, tap SW5) is preferred**.
Note: take voltage readings **with the motor connected** (back-probe) for the
true loaded value; open-circuit reads higher.

**`F.G` tach:** not stock-wired — skip unless you tap the `F.G` pad.

---

## 4a. Tools — do you need a scope?

For this build, **a Hz/duty multimeter beats a scope** — you need a few *numbers*,
not waveform shapes:
- Resolves **3.3 V vs 5 V logic** definitively (duty-% at L12: ~88–90% ⇒ 3.3 V;
  ~58% ⇒ 5 V) → decides whether a level shifter is needed.
- Gives the **PWM frequency** to match on the ESP.
- Confirms oscillation **~50/60 Hz**, and reads **F.G Hz** for optional RPM.

Recommendation: a **~$20–30 Hz/duty meter** (e.g. ANENG AN870/AN8008, ZOYI ZT‑219).
A **pocket scope** (~$30–60) is only worth it if F.G proves too small/noisy for the
meter's counter, or for future projects. A bench scope is unnecessary here.

Note: the speed path doesn't strictly need any of this — the driver reads the PWM
**average**, so you can flash the ESP, drive 3.3 V PWM, sweep duty, and watch the
fan; add a level shifter only if it doesn't respond. The Hz meter just removes the
guesswork.

## 5. Hardware interface

- **Controller:** ESP32 — an **ESP32-C3 is plenty** (uses only 2 GPIOs; its 3.3 V
  I/O matches the fan's PWM). Avoid C3 strap pins GPIO2/8/9 and USB GPIO18/19;
  use GPIO4 (PWM) + GPIO5 (osc). Power its `5V` pin from the 24 V→5 V buck.
- **Power for the ESP:** buck converter **24 V → 5 V** off the SMPS secondary
  (`+24V`/`GND` from `CN1`/`CN2`). Everything stays on the **isolated secondary
  side** — no mains contact. ✔
- **Speed (`PWM`, logic):**
  - If the driver's `PWM` input is 5 V logic, put a **level shifter** (74AHCT125 /
    BSS138) between ESP32 (3.3 V) and pin 1 so highs register correctly.
  - Keep the ESP PWM frequency = measured stock frequency for identical behaviour.
  - Add a series ~100 Ω + small RC to tame edges over the harness.
- **`F.G` tach (optional, not stock-wired):** the `FK-EGP00962` `F.G` pin is an
  unpopulated pad in this fan (the stock harness carries only 24V/GND/PWM). If you
  want RPM in HA, solder a tap wire to the `F.G` pad, then feed it (pull-up + level
  clamp) to an ESP32 input and use ESPHome `pulse_counter`. Skip otherwise.
- **Oscillation (`OSC-A/OSC-B` = the `TYJ50-8` coil, ~80 Ω) — needs TRUE AC:**
  - `TYJ50-8` is a **claw-pole PM AC synchronous motor**: it only runs on a real
    **~50/60 Hz AC** field. **DC on/off or arbitrary PWM will NOT turn it** (hum,
    overheat, locked-rotor). The stock board synthesizes ~50/60 Hz AC across A–B
    from the 24 V DC bus.
  - **Preferred (simplest): don't reproduce the AC** — keep the stock control board
    driving oscillation and have the ESP **tap the `摇头` (SW5) button** via an
    optocoupler to toggle it. HA gets an oscillation switch; the stock board does
    the hard AC synthesis.
  - **Full takeover (only if control board removed):** generate a **symmetric
    ~50/60 Hz square-wave AC** with a **full H-bridge** (DRV8871/L298, 24 V, ≥0.5 A)
    at the measured Vrms/freq, **zero DC offset**. Never wire a GPIO to A/B.
- **Grounding:** single common ground between ESP, buck output, and `CN2` GND.

---

## 6. ESPHome sketch (fill in after measurements)

```yaml
esphome:
  name: heran-fan

esp32:
  board: esp32-c3-devkitm-1
  variant: esp32c3
  framework:
    type: esp-idf

wifi: { ssid: !secret wifi_ssid, password: !secret wifi_password }
api:
logger:
ota:

# --- SPEED: logic PWM to the FK-EGP00962 BLDC driver (CN2 pin 1) ---
output:
  - platform: ledc
    id: fan_pwm
    pin: GPIO4               # ESP32-C3 safe GPIO (avoid strap pins 2/8/9)
    frequency: 20000Hz        # <-- set to measured PWM freq
    min_power: 0.25           # <-- measured minimum spin duty
    max_power: 1.0
    zero_means_zero: true

fan:
  - platform: speed
    output: fan_pwm
    name: "Heran Fan"
    speed_count: 100          # continuous %; or set to 3 to mimic Low/Med/High

# --- OSCILLATION (recommended: reuse stock board via SW5 button tap) ---
# TYJ50-8 needs true ~50/60 Hz AC; easiest is to let the stock board drive it and
# just toggle the 摇头/SW5 button through an optocoupler across the switch:
switch:
  - platform: gpio
    pin: GPIO5                # -> optocoupler across SW5 (摇头) on the control board
    name: "Fan Oscillation"
    # If SW5 is a momentary toggle, pulse it (on_turn_on/off) instead of a level.
#
# FULL-TAKEOVER alternative (only if the control board is removed): drive a FULL
# H-bridge with a symmetric ~50/60 Hz square wave (zero DC offset) at the measured
# Vrms/freq — e.g. an interval:/lambda toggling IN1/IN2 at ~50 Hz.

# --- OPTIONAL RPM feedback: F.G is NOT stock-wired; only if you solder a tap
#     to the FK-EGP00962 F.G pad. Otherwise omit this whole sensor block. ---
# sensor:
#   - platform: pulse_counter
#     pin: GPIO6              # (optional) F.G pad tap via pull-up + level clamp
#     name: "Fan RPM"
#     unit_of_measurement: RPM
#     # filters: divide by (pulses per revolution) once measured
```

Notes:
- If oscillation turns out to need an A/B pattern (direction/enable), replace the
  simple `gpio` switch with a **template switch** toggling two `gpio` outputs.
- To present it as the native HA oscillation toggle, once validated you can bind
  it via the `fan` platform's `oscillation_output`/template as appropriate.

---

## 7. Risks, safety & reversibility

- **Mains isolation:** never bridge primary and secondary of the SMPS. Do all ESP
  wiring on the 24 V **secondary** side only. Keep the mains SMPS in its housing.
- **Back-drive / stalls:** don't command instant full duty from stop if the stock
  MCU ramped it — honor the measured startup threshold / add a soft ramp.
- **Fusing:** the power board carries fusible/inrush resistors (`RX1`/`RX2`) on
  the mains side; if you bypass the control board (C2), add an inline fuse on the
  24 V feed to the motor.
- **Fail-safe output states:** make the ESP's `PWM`/`OSC` outputs **safe during
  boot, reset, and Wi-Fi/API loss** (default to motor-off, oscillation-off).
  Guard against conflicting oscillation commands (never assert both OSC lines in
  an illegal combination). Preserve the enclosure, strain relief, insulation, and
  any thermal protection when reassembling.
- **Isolation is an assumption to verify:** the "isolated secondary" premise must
  be confirmed (Step 1 in Section 4) *before* probing or adding wiring — the
  power board carries live mains.
- **Reversibility:** Variant C1 is plug-reversible (re-seat `CN2` to the control board).
  Photograph and label the `CN2` harness orientation before unplugging.

---

## 8. Open items / to identify

- [x] **Integrated driver confirmed:** main motor uses the `FK-EGP00962` in-motor
      BLDC driver — `CN2 PWM` is a logic speed command (see `pcb_2/NOTES.md`).
- [x] **Oscillation identified:** `TYJ50-8` synchronous 24 V motor on `OSC-A/B`
      — those lines are ~24 V power (relay/H-bridge, not GPIO).
- [x] **Main-motor interface reduced to 3 wires** (`24V/GND/PWM`); `F.G` and `SS`
      are unused/unwired. IC identification is therefore **not required**.
- [ ] (Optional) Read the `FK-EGP00962` IC part number only if PWM measurements
      look ambiguous — otherwise skip.
- [ ] Measure `PWM` level/polarity/frequency and startup duty; fill Section 4.
- [ ] Measure `OSC-A/B` AC-V / Hz / DC-offset; decide **hybrid (SW5 tap, reuse
      stock AC drive)** vs. full H-bridge AC synthesis.
- [ ] Confirm `+24V` on `CN2` is sourced from the power board (C2 routing).
- [ ] Decide C1 vs C2.

## 9. Summary — why this is the "clean" option
`CN2` is a **hybrid** interface: **pin 1 `PWM` is a clean logic speed command** to
the motor's integrated `FK-EGP00962` BLDC driver (a simple `24V/GND/PWM` link;
`F.G`/`SS` unused), while **`OSC-A/OSC-B` are ~24 V power** to the `TYJ50-8`
oscillation motor. So an ESP32 can become a drop-in replacement for the fan's
brain — continuous PWM speed + relay/H-bridge oscillation (optional F.G-tap RPM) —
giving Home Assistant a real variable `fan` entity with no IR line-of-sight.
