# Contributing

Thanks for helping improve this fan → Home Assistant mod! This is an **unverified
work in progress**, so real-world data and fixes are especially valuable.

## Reporting that it worked (or didn't) on your fan
Open an issue and include:
- **Fan model** + the **board markings** you found (control board, power board,
  in-motor driver) and a photo or two (**strip EXIF/GPS first** — e.g.
  `mogrify -strip yourphoto.jpg`).
- Your **measurements**: PWM logic high level, frequency, per-level duty/voltages,
  the oscillation drive (AC volts / Hz), and the +24 V rail.
- **ESPHome version** and your ESP board.
- What you changed in `esphome/heran-fan.yaml` (e.g. `adc_max_v`, `pwm_freq`,
  `min_duty`/`max_duty`) and whether it's **tested on hardware** or only on paper.

## Pull requests
- Keep changes small and focused; explain the reasoning.
- Clearly mark whether a change is **verified on hardware** or **untested**.
- Update the docs (`BUILD_GUIDE.md`, `HA_MOD_NOTES.md`) and keep component values
  consistent across the BOM, tables, and the wiring diagram.
- Don't commit `secrets.yaml` or any personal Wi-Fi/keys (see `.gitignore`).

## Safety
This mod opens a mains-powered appliance. Only submit guidance you've verified is
safe, and never advise bridging the mains/SMPS primary side. See the disclaimer in
the README.
