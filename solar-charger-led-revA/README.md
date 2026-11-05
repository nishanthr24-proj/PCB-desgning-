# Solar battery charger with charging and fault LEDs — Revision A

Open **Solar_Charger_LED_RevA.kicad_pro** in **KiCad 9 or newer**, then open the
schematic or PCB from the project manager. Extract the complete ZIP first.
The project-local symbol and footprint libraries use `${KIPRJMOD}`; no Windows
paths or third-party library download is required. Standard KiCad 3D models are
optional and may need the normal KiCad 3D-model package on your computer.

## Design specification

| Item | Revision A target |
| --- | --- |
| Battery | One **protected 3.7 V nominal Li-ion 18650 cell**, rated by its manufacturer for at least 500 mA charging; 4.2 V CC/CV chemistry only |
| Charging voltage | 4.200 V nominal; actual tolerance includes IC and resistor tolerances |
| Maximum charging current | 500 mA nominal, set by the 0.20 ohm sense resistor |
| Solar panel | Nominal 12 V panel, approximately 18 V at maximum power, at least 5 W recommended |
| Maximum panel open-circuit voltage | **25 V, including the cold-weather Voc increase** |
| Panel voltage regulation | 17.874 V nominal, fixed-voltage regulation; not a dynamic MPPT algorithm |
| Charger | LT3652EMSE#PBF, thermally enhanced MSOP-12 |
| PCB | 60 × 55 mm; 2 copper layers; 1.6 mm FR4; 1 oz copper; four M2.5 clearance holes |
| Minimum fabrication geometry | 0.15 mm tracks/clearance; smallest signal vias 0.45 mm diameter / 0.20 mm drill; confirm with your fabricator |
| Temperature sensing | External 10 kohm NTC, B = 3380 K, attached to the cell; approximately 0–40 °C charging window |

Do not connect a LiFePO4 cell, multiple cells in series, a 12 V battery, or an
unidentified battery. A protection circuit and a charger serve different purposes;
this PCB does not replace the protected cell's protection circuit.

## Changes from the uploaded project

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
  and four thermal vias. The uploaded project remains unchanged in its original
  directory.
- Selected a 22 µF / 16 V 1210 X7R output ceramic capacitor so a suitable part can
  retain at least the required 10 µF effective capacitance under DC bias and tolerance.

## Connectors

| Connector | Pin | Function |
| --- | --- | --- |
| J1 | 1 | Panel positive, VIN |
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
pulled up to VIN, potentially 25 V. Do not connect them directly to a GPIO. The SET
pin is a high-impedance analog sense node, not a digital control input; external
loading changes the panel-regulation voltage. Use a high-impedance meter for checks.

An open/disconnected NTC **disables** the LT3652 temperature-monitoring function;
it is not an open-sensor alarm. Fit and attach the specified sensor before charging
a real cell. Do not replace it with a fixed resistor for battery operation.

## LED meanings while panel input is present

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
- `V_PANEL_REG = 2.7 × (1 + R10/R11) = 2.7 × (1 + 562k/100k) = 17.874 V`.
- `t_TIMER = 0.68 µF × 4.4e6 = 2.992 h`; preconditioning timeout is about 22.4 min.
- L1 is 22 µH. At 25 V input and 4.2 V output, approximate 1 MHz ripple is
  `4.2 × (1 − 4.2/25)/(1e6 × 22e-6) = 0.159 A peak-to-peak`.
  Peak current is approximately 0.58 A at 500 mA charging. Specify Isat ≥1 A and
  Irms ≥0.5 A, including component temperature and tolerance effects.
- With 10 kohm LED resistors, each status pin sinks less than about 2.8 mA at
  25 V, including the 100 kohm pull-up; below the LT3652's 10 mA capability.

These are nominal design calculations, not measurements of assembled hardware.

## Assembly and first power-up

1. Cross-check the selected components' pinouts, land patterns, voltage/current
   ratings, and the latest LT3652 datasheet before ordering. The BOM gives ratings
   and package requirements; an unspecified substitute is not automatically valid.
2. Use stencil/paste and controlled reflow for U1, including its exposed ground
   pad. Inspect all leads for bridges. Thermal-via solder wicking must be addressed
   in the assembly process; filled/plugged vias or suitable tenting can help.
   Check the inductor, diode cathodes, LED cathodes, and C5 polarity carefully.
3. With all power and the battery disconnected, verify connector polarity,
   continuity, and the absence of VIN-to-GND and BAT-to-GND shorts. Fit external
   appropriately rated fuses/current limiting: there is no onboard fuse or
   reverse-polarity input protection in this revision.
4. **No lithium cell for initial tests.** Connect a current-limited bench supply
   to J1, set to 20 V with an initial 0.10 A current limit. Connect the correct NTC
   or a temporary 10 kohm test resistor to J3. A fixed resistor is for bench checks
   only. Observe startup and raise the input limit to 0.30 A when appropriate.
5. Measure BAT+ relative to GND using a high-impedance meter and oscilloscope.
   Expect approximately 4.20 V when regulating; allow IC/resistor tolerances
   (roughly 4.17–4.23 V). **Stop if it exceeds 4.25 V**, oscillates excessively,
   draws unexpected input current, or any component becomes excessively hot.
   Do not treat a brief no-load reading as complete charging validation.
6. Use a battery simulator capable of **sinking** current, or a suitable electronic
   load in constant-voltage mode, set near 3.7 V. An ordinary source-only bench
   supply is not a battery simulator. Verify approximately 500 mA output, about
   100 mV across R6, acceptable ripple/temperature, and the green LED indication.
7. With the simulator attached, test J3 with resistors: 10 kohm represents normal
   temperature; 33 kohm represents a cold fault and 4.7 kohm a hot fault. Both LEDs
   should illuminate during the temperature fault and charging should pause.
   Verify the actual thermistor's hot/cold operation separately.
8. Test the input-regulation action using a current-limited panel simulator or
   actual characterized panel, and verify charge taper, termination, and restart
   using the battery simulator. A stiff bench supply alone does not establish
   solar maximum-power operation. Observe SW with a short probe-ground connection.
9. Only after those checks pass, connect the selected protected cell with its
   attached NTC, verify charge limits against the cell manufacturer's requirements,
   and perform an attended complete charge/temperature test.

## Files and validation

- `Solar_Charger_LED_RevA.kicad_pro`, `.kicad_sch`, `.kicad_pcb`: editable project.
- `SolarCharger.kicad_sym`, `SolarCharger.pretty/`, library tables: portable libraries.
- `BOM.csv`: component values, packages, and selection/assembly notes.
- `previews/`: schematic PDF/SVG, assembly drawing, and PCB views. The 3D image
  shows the bare PCB; component 3D models are not bundled.
- `validation/`: fresh KiCad ERC, PCB DRC, schematic-parity, and connectivity checks.
- `manufacturing/`: prototype plotting/drill outputs if the final geometric checks pass.
- `ATTRIBUTION.md`: upstream project, reference documents, and library information.

The board has **not** been fabricated, powered, electrically simulated, or physically
validated here. ERC/DRC and connectivity checks establish CAD consistency and
geometry only. Analog stability, efficiency, thermal performance, transient
behavior, EMC, and actual battery charging still require bench verification.

