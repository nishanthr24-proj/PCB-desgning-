# PCB-desgning-

Solar battery charge controller designed in KiCad, with green charging and red fault LEDs.

The editable project, local libraries, drawings, BOM, and prototype fabrication files are in **[solar-charger-led-revA/](solar-charger-led-revA/)**.

## Open the project

Download or clone this repository, then open [`Solar_Charger_LED_RevA.kicad_pro`](solar-charger-led-revA/Solar_Charger_LED_RevA.kicad_pro) in **KiCad 9 or newer**. Keep the project folder and its local libraries together.

- [Circuit schematic (PDF)](solar-charger-led-revA/previews/Schematic.pdf)
- [PCB preview](solar-charger-led-revA/previews/PCB_3D.png) — bare board; component models are not bundled
- [Bill of materials](solar-charger-led-revA/BOM.csv)
- [Design details, connector pinouts, and first-power-up instructions](solar-charger-led-revA/README.md)
- [Validation results](solar-charger-led-revA/validation/RESULTS.json)
- [Sources and attribution](solar-charger-led-revA/ATTRIBUTION.md)

## Design target

- One protected 3.7 V nominal lithium-ion 18650 cell, **4.2 V CC/CV** chemistry.
- **500 mA** nominal maximum charging current; the cell must permit this rate.
- Nominal **12 V solar panel**, approximately 18 V at maximum power, **cold open-circuit voltage no greater than 25 V**.
- **LT3652EMSE#PBF in MSOP-12**, with an external 10 kohm / B3380 K battery-temperature sensor.
- Two-layer, 60 × 55 mm PCB with charge/fault LEDs and labeled connectors.

## Validation and prototype status

The revision passes KiCad ERC and PCB DRC with zero violations, zero unconnected items, and zero schematic/PCB mismatches. The exported netlist passes 26 electrical-topology and critical-value checks.

**This is an unbuilt engineering prototype.** It has not been fabricated, physically tested, or electrically simulated. Complete the documented bench checks before connecting a lithium-ion cell. J4 status outputs are pulled up to the solar input voltage and must not be connected directly to microcontroller GPIOs.

The design builds on the user-supplied [upstream project](https://github.com/Hirusha785/solar-battery-charge-controller-pcb), whose README credits Fernando S.M.H.G. Attribution and KiCad library license notices are included in the project folder.
