# Revision history

## Revision B — populated 3D assembly, 2026-11-06

- Added portable `${KIPRJMOD}/3dmodels` references for all 30 fitted component
  bodies, with source manifest and KiCad model-license notice. H1–H4 and TP1–TP9
  remain mounting holes and bare test pads without component bodies.
- Added populated angled, top, and bottom previews and a standalone assembly
  STEP for KiCad/FreeCAD presentation and mechanical inspection.
- Used representative models for U1 and L1; documented their dimensional limits
  in [3D/README.md](3D/README.md). D3/D4 body colors identify the green/red LEDs
  and do not indicate illumination. The external battery, panel, and NTC are
  outside the board assembly; JP1 is shown without a shunt.
- Changed no electrical routing or fabrication geometry. Existing Gerbers remain
  applicable. The 3D assembly adds no simulation or evidence of circuit operation.

## Revision B — 2026-11-06

Adds testability and solar-input protection to the Rev A engineering prototype.
The board remains a single protected 4.2 V lithium-ion cell charger with 500 mA
nominal maximum charging current, a 25 V maximum cold panel open-circuit voltage,
and a 60 × 55 mm two-layer PCB.

- Inserted F1, a 1 A fast-acting soldered 1206 fuse, rated at least 32 V DC.
  The exact selected part still needs DC interrupt and land-pattern verification.
- Inserted D5, an SS16-class SMA Schottky rated at least 60 V / 1 A, with anode at
  VIN_FUSED and cathode at protected VIN. All former VIN loads are downstream.
- Added TP1 VIN_RAW, TP2 VIN_FUSED, TP3 protected VIN, TP4 BAT, TP5 R6/SENSE,
  TP6 R6/BAT, TP7 SW, TP8 scope GND, and TP9 bench GND.
- Added JP1 between EN/SHDN and GND. Closed disables charging; open enables it
  through the existing protected-VIN 100 kΩ pull-up.
- Renamed the former J4 SET label to VIN_REG. Retained the VIN-level status warning.
- Added a staged test plan and an expected-versus-measured worksheet. No bench
  values are filled in because no assembled-board measurements have been made.
- Prepared the project for fresh schematic/PCB consistency, ERC/DRC, and fabrication
  exports. Consult the Rev B `validation/` reports for the actual final outcomes.

The input divider remains on protected VIN at a nominal 17.874 V. The corresponding
panel-side voltage includes D5's forward drop and the fuse/wiring drops. Reverse
blocking is obtained at the cost of forward-drop power loss. This is not dynamic
MPPT, surge/overvoltage protection, battery reverse-polarity protection, or proof
that a small panel can supply enough fault current to open F1.

## Revision A

Established the corrected LT3652EMSE MSOP charger design with green charge and red
fault LEDs, corrected current-sense/output wiring, 0.20 Ω charge-current sensing,
4.2 V precision feedback, suitable Schottky diodes/power inductor, external NTC
access, portable KiCad libraries, and a two-layer PCB. Rev A is retained in
`../solar-charger-led-revA/` for comparison.

## Upstream source

The user supplied the original KiCad archive from
<https://github.com/Hirusha785/solar-battery-charge-controller-pcb>, whose README
credits Fernando S.M.H.G. See [ATTRIBUTION.md](ATTRIBUTION.md).

Neither revision has been fabricated or physically validated here. No manufacturer
LT3652 simulation model was used for Rev B. CAD checks and calculations do not
establish actual charging, thermal, efficiency, or fault performance.
