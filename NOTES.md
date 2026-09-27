# Heran Fan — Circuit Board Photo Notes

Review of the 11 photos now in **`pcb_1/`** (taken 2026‑09‑27, ~21:11–21:16).
They document the teardown of a **Hanny (www.hanny.com.cn)** electric fan.

> **Photos are organised into `pcb_1/` (base + control electronics) and
> `pcb_2/` (fan head: motor driver + motors).** This file covers `pcb_1/`; see
> **`pcb_2/NOTES.md`** for the in‑motor BLDC driver (`FK‑EGP00962`) and the
> motors, and **`HA_MOD_NOTES.md`** for the Home‑Assistant control plan.
>
> **Board count:** the base + control electronics here are **2 PCBs**; a **3rd
> PCB** (the in‑motor BLDC driver) was found later in the head — see `pcb_2/`.
> So the fan has **3 PCBs total.**

> Each board here is double‑sided, so most photos are just
> the front vs. back of the same board (plus several near‑duplicate angles).
> Common markings across both boards: `www.hanny.com.cn` with a "POWER SUPPLY"
> diamond logo, and UL flammability rating `94V‑0`.

---

## Boards identified (2 total)

### Board 1 — Control / display board (in the head)
The user‑interface + MCU board mounted behind the front control panel.

- **Front (user side)** — light cream/beige silkscreen (looks tan under warm
  light). Markings: `KB‑3151C`, `E123995`, `FY‑HG‑FLD35‑16BR`,
  `V1.0  J20191030`, `www.hanny.com.cn`, UL `94V‑0`.
  - **5 tactile buttons** `SW1`–`SW5`:
    - `SW1` 开关 = Power
    - `SW2` 风速 = Wind speed
    - `SW3` 定时 = Timer
    - `SW4` 模式 = Mode
    - `SW5` 摇头 = Oscillation (head swing)
  - **Indicators** `LED1`–`LED11`: timer LEDs `0.5H / 1H / 2H / 4H`, mode LEDs
    `SLP` (sleep) and `RHY` (rhythm/natural wind).
  - IR remote receiver (center), buzzer `BUZ`, electrolytics `EC1`–`EC4`.
  - Connectors: `CN1` (2‑pin, **+24V / GND** power in) and `CN2` (5‑pin,
    **PWM / GND / +24V / OSC‑A / OSC‑B** out to the motor / oscillation assembly).
- **Back (green FR4)** — the MCU + SMT side. A wide SOP IC (the microcontroller),
  a small 8‑pin SOIC, a 5‑pin header (= `CN2`), and a grid of through‑hole solder
  joints that line up with the front‑side LEDs and buttons (this is what confirms
  it is the *same* board).

### Board 2 — Power supply board (in the base)
Mains AC→DC switch‑mode supply that feeds +24V up to the control board.

- **Component side (through‑hole)** — main transformer
  `HYL16H/100‑240V  A1220413  RoHS` (100–240 V input), bridge/rectifier diodes,
  primary bulk electrolytics, yellow film cap, output electrolytics. AC‑in wires
  (with ferrite loop) and a 2‑pin DC‑out connector to the control board.
  Markings: `E355240`, `YF‑1`, `www.hanny.com.cn`, UL `94V‑0`.
- **Solder / control side (green FR4, SMD)** — the SMPS control circuitry:
  controller/optocoupler `U1`/`U3`, feedback network `R7`–`R23`, fusible/inrush
  resistors `RX1`/`RX2`, and part `601`. Board fab number: `ReV1.3` `PCB181020L1`.

---

## File‑by‑file index

| File | Board | Side / view | Notes |
|------|-------|-------------|-------|
| `P_20260927_211423.jpg` | Board 1 (control) | Front (display/keypad) | Full board in hand. |
| `P_20260927_211439.jpg` | Board 1 (control) | Front (display/keypad) | **≈ duplicate of 211442.** |
| `P_20260927_211442.jpg` | Board 1 (control) | Front (display/keypad) | **≈ duplicate of 211439.** |
| `P_20260927_211144.jpg` | Board 1 (control) | Back (green, MCU) | Unique; low‑res (~18 KB / 320×240). Shows the MCU + LED/button solder grid. |
| `P_20260927_211634.jpg` | Board 2 (power) | Component side (transformer) | Part of a 3‑shot set. |
| `P_20260927_211637.jpg` | Board 2 (power) | Component side (transformer) | **≈ duplicate of 211634.** |
| `P_20260927_211640.jpg` | Board 2 (power) | Component side (transformer) | Closer top‑down; same board. |
| `P_20260927_211157.jpg` | Board 2 (power) | Solder/control side (`PCB181020L1`) | Wide framing. **≈ duplicate of 211200.** |
| `P_20260927_211200.jpg` | Board 2 (power) | Solder/control side (`PCB181020L1`) | **≈ duplicate of 211157.** |
| `P_20260927_211224.jpg` | Board 2 (power) | Solder/control side (`PCB181020L1`) | Closer/tighter framing. **≈ duplicate of 211227.** |
| `P_20260927_211227.jpg` | Board 2 (power) | Solder/control side (`PCB181020L1`) | **≈ duplicate of 211224.** |

### Duplicate / grouping summary
- **Board 1 (control/display):** front = `211423`, `211439`≈`211442` (3 shots);
  back = `211144` (1 unique low‑res shot). → **4 photos, 1 board.**
- **Board 2 (power supply):** component side = `211634`≈`211637`≈`211640`
  (3 shots); solder side = `211157`≈`211200`, `211224`≈`211227` (2 near‑dup
  pairs). → **7 photos, 1 board.**
- No two files are byte‑identical; "duplicates" above are the *same board side
  photographed multiple times*, not exact file copies.

---

## Suggested keepers (one clear shot per board/side)
- Board 1 front (display): `P_20260927_211442.jpg`
- Board 1 back (MCU): `P_20260927_211144.jpg` (only one — low‑res; a sharp
  re‑shoot would help read the MCU/driver IC part number).
- Board 2 component side: `P_20260927_211640.jpg`
- Board 2 solder side: `P_20260927_211224.jpg`

The remaining files are redundant and can be archived/deleted if space matters.
