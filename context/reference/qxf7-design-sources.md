# QxF7 report: "Our design" section — sources and notes (updated 2026-10-12)

Section location: after "Success criterias", before "Competitors around the world" (about pages 12–15). Contents:
- Three VTOL layouts table
- How a flight works
- Why this layout fits
- Flightory Stork intro and photo
- Full Stork VTOL spec table (page 14)
- Where the stock Stork falls short (criteria table)
- Conclusion: scale it up

User edits to respect (don't re-add):
- The user removed the price sentence and the licence sentence.
- The user deleted the "Why we chose the Stork" subsection.
- The user rewrote the conclusion to drop the ~7 kg / 2.4 m estimate. The new conclusion says scale, span and mass are not yet chosen.
- The doc body font is now Times New Roman. The new tables were set to match.

## Spec table layout (45 rows, 2 columns, header row pinned)
- Section rows are merged across both columns and shaded blue-grey:
  - Airframe (Flightory, official)
  - Recommended equipment (Flightory, official)
  - Build (Flightory, official)
  - Flightony build (third-party vendor)
- The Flightony rows are highlighted amber (#FFF2CC). The amber note under the table says they come from a third-party vendor's build, that its other specs match Flightory's, and that its figures assume optimal conditions and appear calculated.
- Flightony specs identical to Flightory's are not repeated: configuration, span, length, wing area, airfoil, AR, material, AUW, FC, GPS, receiver, servos, motors.

## Sources to cite

### Stork (Flightory)
- Flightory, Stork VTOL User Manual v2 (2025): https://flightory.com/wp-content/uploads/2026/04/STORK-USER-MANUAL-VTOL.pdf
  - General data (p. 5)
  - Electronics (p. 8)
  - Accessories and carbon (p. 9)
  - Powertrain: 3.8 kg / 1,280 W / 50 A on 6S, about 2 kg on 4S, under 50% throttle on 4S (p. 11–13)
  - Print settings (p. 15)
  - Skids tested to 3,000 g (p. 29)
- Flightory, Stork User Manual v2 (2026): project file STORK-USER-MANUAL.pdf
  - CFD (p. 6–7)
  - Bay dimensions (p. 9)
- Product pages:
  - Stork VTOL Pack (AUW 1.8–3.1 kg): https://flightory.com/product/stork-vtol-pack/
  - Stork: https://www.flightory.com/stork
- Photo: https://flightory.com/wp-content/uploads/2026/04/8.jpg

### Stork performance (Flightony, third-party vendor)
- Source: Flightony (Beverly Hills, CA), https://www.flightony.com/stork-vtol/specs
- Values in the table:
  - cruise 54–60 km/h
  - range 104–130 km (4S4P) and 70–85 km (4S3P)
  - payload 200 g and 500 g
  - 2.0–2.5 Wh/km, 80–110 W cruise, about 300 W hover
  - battery: 4S4P INR21700-50E, 14.4/16.8 V, 20,000 mAh, 288 Wh (259 usable), 39.2 A, about 1.2 kg
  - props: 7 in lift (2 CW, 2 CCW), APC 10×6E pusher
  - ESCs: Velox V50A and Lumenier 51A
  - camera: DJI O3 Air Unit (1/1.7 in, 4K60, 155°, 10 km, RockSteady)
  - telemetry: MAVLink over 4G LTE via Pi Zero 2W + Huawei E3372
  - ground control: QGC or Mission Planner, RadioMaster TX16S MK II, ELRS
- Flightony's disclaimer: "Range, payload, and performance figures are based on optimal conditions and may vary."
- Our observation: range = usable energy ÷ Wh/km (259/2.5 = 104, 259/2.0 = 130).

### Other Flightory designs compared
- Stallion: https://flightory.com/product/stallion/
- Super Stingray: https://flightory.com/product/super-stingray/

### Example aircraft for the three layouts
- Wingcopter 198: https://wingcopter.com/wingcopter-198
- WingtraOne: https://wingtra.com
- DeltaQuad: https://www.deltaquad.com

### ArduPilot
- https://ardupilot.org/plane/docs/quadplane-support.html
- https://ardupilot.org/plane/docs/assisted_fixed_wing_flight.html

## Our own calculations
- Headwind multiplier v/(v−w): 57/(57−25) ≈ 1.78 for the Stork, and 70/(70−25) = 1.56 for QxF7.

## Notes
- "Polish designer" is inferred from the designer's name and the site's Polish alt text.
- The layout trade-offs come from general engineering knowledge.
