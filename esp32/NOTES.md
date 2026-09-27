# esp32 — the controller board

Photos of the ESP32 board on hand for the fan mod (see `../BUILD_GUIDE.md`).

## Board: ESP32-C3 SuperMini (USB-C)
- Confirmed from the photos: silk reads **"ESP32 C3 Super Mini"**; ESP32-C3 QFN
  with Wi-Fi, **USB-C**, **BOOT** + **RST** buttons, power LED.
- Native USB (USB-Serial/JTAG) → **flash directly over USB-C**, no external adapter.
- Onboard LED is on **GPIO8** (also a strapping pin) → don't use GPIO8.
- Not broken out: GPIO18/19 (used for native USB) — nothing to avoid there.

### Pin header (as printed on the back)
```
 left  : 5V  G(GND)  3.3  GPIO4  GPIO3  GPIO2  GPIO1  GPIO0
 right : GPIO5  GPIO6  GPIO7  GPIO8  GPIO9  GPIO10  GPIO20  GPIO21
```
- **Strapping/boot pins to avoid for outputs:** GPIO2, GPIO8 (LED), GPIO9 (BOOT).
- GPIO20/21 = UART0 (TX/RX) — usable but avoid if using serial logging.
- ADC-capable: GPIO0–GPIO4.

### Pin assignment for this build
| Signal | Pin | Notes |
|--------|-----|-------|
| Speed **PWM** out → CN2 PWM (motor side) | **GPIO4** | LEDC PWM, 3.3 V |
| **Oscillation** → optocoupler across SW5 | **GPIO5** | momentary tap |
| *(Option B)* control-board PWM in (mirror/override) | **GPIO3** | RC low-pass → ADC |
| *(optional)* extra button injections | GPIO7, GPIO10 | if doing Option A |

All chosen pins are broken out on this board and are safe (non-strapping).

### Flashing notes
- Board key in ESPHome: `esp32-c3-devkitm-1`, `variant: esp32c3`.
- Plug USB-C; it should enumerate as a serial/USB-JTAG device. If the first flash
  doesn't detect: **hold BOOT, tap RST, release BOOT** to enter download mode.
- Power in final install: feed the **buck 5 V → the `5V` pin** (USB unplugged);
  the onboard LDO makes 3.3 V. Share ground with `CN2 GND`.

## Photo index
| File | View |
|------|------|
| `esp32c3_1.jpg` | Back — pin labels (5V/G/3.3/4/3/2/1/0 · 5/6/7/8/9/10/20/21) |
| `esp32c3_2.jpg` | Front — USB-C, C3 chip, BOOT/RST buttons |
