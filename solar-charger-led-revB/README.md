# Solar battery charger with charging and fault LEDs — Revision B

Open **Solar_Charger_LED_RevB.kicad_pro** in **KiCad 9 or newer**, then open the
schematic or PCB from the project manager. Extract the complete ZIP first.
The project-local symbol, footprint, and bundled 3D-model libraries use
`${KIPRJMOD}`; no Windows paths or separate library download is required.

## View the populated 3D board

In the PCB Editor, choose **View → 3D Viewer** or press **Alt+3**. Keep the whole
project folder together so the component models in `3dmodels/` load correctly.
For a standalone assembly, open
[`3D/Solar_Charger_LED_RevB_Assembly.step`](3D/Solar_Charger_LED_RevB_Assembly.step)
with **File → Open** in FreeCAD. Presentation images show the
[angled](previews/PCB_3D.png), [top](previews/PCB_3D_Top.png), and
[bottom](previews/PCB_3D_Bottom.png) views.

The assembly includes bodies for all 30 fitted components; the four mounting
holes and nine bare test pads have no separate bodies. The model helps inspect
placement, orientation, and connector access. U1 and L1 use representative bodies;
see [3D/README.md](3D/README.md) for dimensional limits, source information, and
what is included. The LED colors identify D3 and D4; the renders show no operating
state. The 3D addition changes no electrical routing or Gerber geometry.

## Design specification

| Item | Revision B target |
| --- | --- |
| Battery | One **protected 3.7 V nominal Li-ion 18650 cell**, rated by its manufacturer for at least 500 mA charging; 4.2 V CC/CV chemistry only |
| Charging voltage | 4.200 V nominal; actual tolerance includes IC and resistor tolerances |
| Maximum charging current | 500 mA nominal, set by the 0.20 ohm sense resistor |
| Solar panel | Nominal 12 V panel, approximately 18 V at maximum power, at least 5 W recommended |
| Maximum panel open-circuit voltage | **25 V, including the cold-weather Voc increase** |
| Charger-side input regulation | 17.874 V nominal **after D5**; panel-side voltage also includes diode, fuse, and wiring drops; fixed-voltage regulation |
| Charger | LT3652EMSE#PBF, thermally enhanced MSOP-12 |
| PCB | 60 × 55 mm; 2 copper layers; 1.6 mm FR4; 1 oz copper; four M2.5 clearance holes |
| Minimum fabrication geometry | 0.15 mm tracks/clearance; smallest signal vias 0.45 mm diameter / 0.20 mm drill; confirm with your fabricator |
| Temperature sensing | External 10 kohm NTC, B = 3380 K, attached to the cell; approximately 0–40 °C charging window |

Do not connect a LiFePO4 cell, multiple cells in series, a 12 V battery, or an
unidentified battery. A protection circuit and a charger serve different purposes;
this PCB does not replace the protected cell's protection circuit.

## New in Revision B

Revision B builds on the corrected Rev A design and keeps the 4.2 V / 500 mA
charging settings. It adds:

- **F1**, a 1 A replaceable fast-acting 1206 fuse rated at least 32 V DC.
  Verify the chosen part's DC interrupt rating and actual land pattern before purchase.
- **D5**, an SS16-class SMA Schottky diode rated at least 60 V / 1 A, in series
  with the solar input for reverse-polarity blocking.
- **JP1**, a shutdown jumper: closed connects EN/SHDN to GND and disables charging;
  open lets the existing 100 kΩ pull-up enable the charger from protected VIN.
- **Nine labeled test points** for the input stages, battery, current-sense resistor,
  switch node, and ground.
- Corrected **VIN_REG** labeling at J4, replacing the former SET label. The
  open-collector status signals remain VIN-level signals, not MCU-safe logic.

See [CHANGELOG.md](CHANGELOG.md) for the revision history and
[TEST_PLAN.md](TEST_PLAN.md) for staged verification and a measurement worksheet.

## Solar-input protection and limits

The positive input path is:

`J1 pin 1 → VIN_RAW → F1 → VIN_FUSED → D5 → protected VIN → charger and status circuitry`

D5's **anode faces VIN_FUSED; its cathode faces protected VIN**. The original VIN
loads, including the LT3652, input capacitors, input-regulation divider, shutdown
pull-up, and LED circuits, are downstream of D5. J1 pin 2 is the common GND.

The series diode introduces a forward-voltage drop and dissipates `P ≈ I_IN × V_F`.
Its value depends on the selected part, current, and temperature; measure it at
TP2 and TP3. The input-regulation divider is unchanged and senses **protected VIN**.
Thus the nominal panel-side regulation point is **17.874 V + D5 forward drop**,
plus fuse/wiring drops. Check that this suits the actual panel. No exact panel
maximum-power or efficiency claim is made.

F1 provides a sacrificial overcurrent element; it is not resettable. A small panel
may be sufficiently current-limited that it **cannot blow a 1 A fuse during a
short circuit**. Verify the fuse's clearing behavior and interrupt rating against
the actual source. Current limiting remains required for bench tests. Do not
bypass F1 or replace it with a higher rating to make a faulty board run.

These additions do **not** provide input overvoltage/surge protection, battery
reverse-polarity protection, a battery protection circuit, or load management.
Use the specified protected cell, observe battery polarity, and keep input cold
open-circuit voltage at or below 25 V. The NTC-disconnection limitation remains.

## Changes inherited from Revision A

- Added **D3, a green charge LED**, and **D4, a red fault LED**, with current-limiting
  resistors. Indicators run from the panel input rather than draining the battery
  overnight. The open-collector status pull-ups now have a supply connection.
- Connected the LT3652 SENSE and BAT pins to the appropriate sides of R6 and
  connected the battery connector and output capacitors to the charging output.
- Changed R6 to 0.20 ohm for 500 mA rather than the original 0.05 ohm / 2 A setting.
- Replaced the 1N4007 switching/boost diodes with SS14 Schottky diodes and assigned
  a real power-inductor footprint to L1.
- Corrected the precision battery feedback and the panel-voltage divider.
- Added a battery-temperature sensor connector; retained timer termination and
  bad-battery detection.
- Used the pin-equivalent **MSOP LT3652EMSE** variant instead of the original
  0.45 mm-pitch DFN LT3652EDD. The 0.65 mm lead pitch is easier to assemble and
  inspect. **The two IC packages are not footprint-interchangeable.**
- Replaced the onboard unprotected-cell holder, alternative barrel input, and
  uncalibrated potentiometer with clearly labeled terminals and fixed settings.
  Use an external holder suitable for the selected protected cell's length.
- Created a new PCB layout with ground planes, an exposed-pad thermal connection,
  and four thermal vias. Rev A is retained separately for comparison.
- Selected a 22 µF / 16 V 1210 X7R output ceramic capacitor so a suitable part can
  retain at least the required 10 µF effective capacitance under DC bias and tolerance.

## Connectors

| Connector | Pin | Function |
| --- | --- | --- |
| J1 | 1 | Panel positive, VIN_RAW, before F1 and D5 |
| J1 | 2 | Panel negative, GND |
| J2 | 1 | Protected battery positive, BAT+ |
| J2 | 2 | Protected battery negative, GND |
| J3 | 1 | External NTC thermistor |
| J3 | 2 | Other thermistor terminal, GND |
| J4 | 1 | CHRG_N, active-low open-collector status |
| J4 | 2 | FAULT_N, active-low open-collector status |
| J4 | 3 | GND |
| J4 | 4 | VIN_REG analog sense node, approximately 2.7 V at the panel regulation point |

**J4 is not a microcontroller-safe logic interface.** Its two status outputs are
pulled up to protected VIN, potentially close to 25 V. Do not connect them directly
to a GPIO. The VIN_REG pin is a high-impedance analog sense node, not a digital
control input; external
loading changes the panel-regulation voltage. Use a high-impedance meter for checks.

An open/disconnected NTC **disables** the LT3652 temperature-monitoring function;
it is not an open-sensor alarm. Fit and attach the specified sensor before charging
a real cell. Do not replace it with a fixed resistor for battery operation.

## Shutdown jumper and test points

**JP1 open = charging enabled when a suitable solar input is available.**
**JP1 closed = EN/SHDN connected to GND, charging disabled.**
The existing 100 kΩ pull-up limits jumper current to approximately 250 µA at
25 V. Shutdown does not physically disconnect the battery or make the board
safe to rewire. Disconnect input and battery power before changing wiring.

| Test point | Net / location | Intended measurement |
| --- | --- | --- |
| TP1 | VIN_RAW, J1 positive before F1 | Applied panel/bench-supply voltage |
| TP2 | VIN_FUSED, between F1 and D5 | Fuse output and D5 anode voltage |
| TP3 | Protected VIN, after D5 | Charger input and D5 cathode voltage |
| TP4 | BAT, battery/output side | Output voltage relative to ground |
| TP5 | SENSE, R6 pin 1 / inductor side | Positive side of current-sense voltage |
| TP6 | BAT, R6 pin 2 / battery side | Negative side of current-sense voltage |
| TP7 | SW, short branch at the switch node | Switching waveform, using TP8 as nearby ground |
| TP8 | GND_SCOPE, electrically common GND | Short oscilloscope ground connection near TP7 |
| TP9 | GND_BENCH, electrically common GND | Bench meter/supply ground access |

TP4 and TP6 share the BAT net but provide different physical probing locations.
TP8 and TP9 both connect to the common GND net; they are not isolated grounds.
Measure `V(TP5) − V(TP6)` across R6; it is nominally **100 mV at 500 mA**.
Use a meter on its voltage range, or a suitable differential measurement. Never
connect a current-meter input directly between these points or across the battery.
TP5 and TP6 are both above GND. Do not attach an earth-referenced oscilloscope
ground clip to either point. Use a suitable differential probe, or two channels
referenced to board GND with a subtraction measurement, after checking grounding.

Keep the SW connection short. Use a short ground spring to TP8 or a suitable
differential probe, and account for the oscilloscope/supply earth connections.
A long clip-ground loop can distort the waveform or cause an accidental short.
SW probing is optional until the user has suitable equipment and probing practice.

## LED meanings while protected input is present

| Green D3 | Red D4 | Meaning |
| --- | --- | --- |
| On | Off | Charging at or above C/10, approximately 50 mA nominal |
| Off | On | Bad-battery fault / preconditioning timeout |
| On | On | Battery temperature fault; charging paused |
| Off | Off | Standby, shutdown, insufficient solar input, or charging below C/10 |

Both LEDs being off **does not prove that the battery is full**. With timer
termination, charging below C/10 can continue until the timer finishes. The
nominal three-hour timer restarts if the battery has not reached the successful
charge threshold. Low sunlight can reduce charging current and affect completion.

## Electrical calculations

- `I_CHG = 0.100 V / R6 = 0.100 / 0.20 = 0.500 A`.
  With the LT3652 sense-voltage tolerance and a 1% resistor, allow approximately
  470–530 mA at the full-current operating point.
- `P_R6 = I²R = 0.5² × 0.20 = 0.050 W`; use the specified 0.5 W 1206 sense part.
- `V_FLOAT = 3.3 × (1 + R4/R5) = 3.3 × (1 + 60.0k/220k) = 4.200 V`.
- `R3 + (R4 || R5) = 203k + 47.1429k = 250.1429k`, close to the datasheet's
  required 250 kohm input-bias compensation. All three feedback parts are 0.1%.
- `V_IN_REG = 2.7 × (1 + R10/R11) = 2.7 × (1 + 562k/100k) = 17.874 V`
  at TP3 after D5. J1 voltage is higher by the series-path drops.
- `t_TIMER = 0.68 µF × 4.4e6 = 2.992 h`; preconditioning timeout is about 22.4 min.
- L1 is 22 µH. At 25 V input and 4.2 V output, approximate 1 MHz ripple is
  `4.2 × (1 − 4.2/25)/(1e6 × 22e-6) = 0.159 A peak-to-peak`.
  Peak current is approximately 0.58 A at 500 mA charging. Specify Isat ≥1 A and
  Irms ≥0.5 A, including component temperature and tolerance effects.
- With 10 kohm LED resistors, each status pin sinks less than about 2.8 mA at
  25 V, including the 100 kohm pull-up; below the LT3652's 10 mA capability.

These are nominal design calculations, not measurements of assembled hardware.

## Assembly and first power-up

Follow [TEST_PLAN.md](TEST_PLAN.md) in order: component review, unpowered checks,
current-limited no-battery startup, input protection and shutdown, controlled
loaded operation, NTC fault checks, then an attended real-cell test last.
All measurement fields are initially **Not measured**.

Use stencil/paste and controlled reflow for U1, including its exposed ground pad.
Inspect for bridges and verify diode/LED/capacitor polarity. Address thermal-via
solder wicking in the assembly process. F1 is a soldered replaceable fuse, not a
resettable protector. Confirm its and D5's actual component drawings and ratings
before ordering; a generic value or footprint name does not certify a substitute.

A resistor load can check loaded operation, but does not demonstrate battery-charge
taper or termination. Use a battery emulator that can **sink current**, or a
suitable electronic load in constant-voltage mode, for the controlled charging test.
An ordinary source-only bench supply is not a battery emulator.

## Final CAD checks

The prepared Rev B passed ERC with zero errors or warnings and PCB DRC with zero
violations, zero unconnected items, and zero schematic/PCB mismatches. The exported
netlist passed 48 electrical checks; the PCB passed 20 additional probe-layout and
check-configuration checks. Those checks also passed from a separate copied folder.
No ERC rule was set to ignore and no ERC/DRC exclusions were used in this revision.
The 3D checks confirm 30 fitted bodies, local model paths, valid STEP imports,
and unchanged non-model PCB/footprint data and manufacturing files. Run
`python3 validation/check_3d.py` to check the bundle against its recorded evidence.
See `validation/RESULTS.json` and the actual reports. Hardware remains untested.

## Files and validation

- `Solar_Charger_LED_RevB.kicad_pro`, `.kicad_sch`, `.kicad_pcb`: editable project.
- `SolarCharger.kicad_sym`, `SolarCharger.pretty/`, library tables: portable libraries.
- `BOM.csv`: component values, packages, and selection/assembly notes.
- `previews/`: schematic PDF/SVG, assembly drawing, and populated PCB 3D views.
- `3dmodels/`: bundled component STEP models and their `SOURCES.json` manifest.
- `3D/`: standalone board-assembly STEP and viewing/model notes.
- `validation/`: fresh KiCad ERC, PCB DRC, schematic-parity, and connectivity checks.
- `manufacturing/`: prototype plotting/drill outputs if the final geometric checks pass.
- `ATTRIBUTION.md`: upstream project, reference documents, and library information.
- `CHANGELOG.md`: Rev B additions and Rev A lineage.
- `TEST_PLAN.md`: CAD-check criteria, staged bench procedure, and blank results table.

No manufacturer simulation model was used for Rev B, and no simulation is included
in this revision. The board has **not** been fabricated, powered, or physically
validated here. ERC/DRC and connectivity checks establish CAD consistency and
geometry only. Analog stability, efficiency, thermal performance, transient
behavior, EMC, and actual battery charging still require bench verification.

## Presentation summary

“Our Rev B keeps the single-cell 4.2 V / 500 mA charger and its charging/fault
indicators. We added a fused reverse-polarity input path, dedicated measurement
points, a shutdown jumper, and clearer signal labeling. The changes make controlled
testing more convenient. A populated 3D assembly illustrates component placement
and connector access. The CAD reports document design-rule and connectivity
checks; physical charging, thermal, and protection performance remain to be measured.”
