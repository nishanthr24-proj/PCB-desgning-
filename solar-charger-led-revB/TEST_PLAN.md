# Revision B verification and measurement worksheet

This plan separates CAD consistency checks from physical tests. **No assembled
Rev B board has been tested here.** Every bench result below is **Not measured**.
Record failures, unexpected behavior, and test conditions; do not replace a blank
with a calculated value or describe an LED state as observed without a test.

Use the schematic, BOM, actual component datasheets, and the LT3652 datasheet
alongside this plan. The target is one protected 4.2 V lithium-ion cell, 500 mA
nominal charging, and a panel with cold open-circuit voltage no greater than 25 V.

## 1. Review before ordering

- Verify all footprints against the actual orderable parts. F1 is a **1 A fast-acting
  soldered 1206 fuse rated at least 32 V DC**. Verify its DC interrupt rating,
  time/current curve, temperature derating, and land pattern. It is replaceable
  by soldering and is not resettable.
- Verify D5 as an SS16-class **at least 60 V / 1 A SMA Schottky**. Check its actual
  forward drop, leakage, power dissipation, and derating. Its anode faces the fuse;
  its cathode faces protected VIN.
- Review the complete input path: J1 positive → TP1/VIN_RAW → F1 → TP2/VIN_FUSED
  → D5 → TP3/protected VIN. Confirm no track, zone, jumper, or connector bypasses
  F1 or D5. All original VIN loads must be downstream of D5.
- Confirm the 17.874 V divider senses protected VIN. At the panel terminal the
  corresponding voltage is higher by D5's forward drop and fuse/wiring drops.
  Check compatibility with the actual panel; do not claim an exact panel MPPT
  operating point or guaranteed efficiency.
- Review exposed-pad assembly, thermal vias, small IC leads, polarity marks,
  terminal numbering, mounting-hole clearance, and probe access.
- Inspect Gerbers/drills in Gerber Viewer, including copper, masks, paste, outline,
  and holes. Confirm they correspond to the final Rev B files, not copied Rev A
  exports. Check minimum geometry with the PCB fabricator before ordering.

## 2. Required CAD and electrical-intent checks

Run KiCad ERC, PCB DRC, schematic/PCB parity, and connectivity checks after the
final zone refill. Review ignored/excluded checks; a hidden or excluded violation
is not a passed test. Save the actual reports in `validation/`.

The independent exported-netlist checks should establish:

| Check | Required electrical intent |
| --- | --- |
| Input isolation | VIN_RAW, VIN_FUSED and protected VIN are three distinct nets, connected only by the intended F1/D5 series path |
| Fuse orientation/path | F1 connects raw and fused input; no parallel bypass |
| Diode orientation/path | D5 anode is VIN_FUSED, cathode is protected VIN |
| Charger input | U1 VIN, input capacitors, input divider, LED supplies/pull-ups and R7 pull-up use protected VIN |
| Shutdown | JP1 bridges EN/SHDN to GND; R7 remains between protected VIN and EN |
| Charge current sensing | U1 SENSE, L1 output, R6 pin 1 and TP5 share SENSE |
| Battery sensing | U1 BAT, R6 pin 2, J2 positive, output capacitor positives, TP4 and TP6 share BAT |
| Current-sense separation | SENSE and BAT are distinct nets joined through R6, not a copper short |
| Switching probe | TP7 shares the SW node; TP8 is common GND; the SW branch is short and away from feedback routing |
| Bench ground | TP9 is common GND, not a separate floating net |
| Status/control header | J4 pin 4 is VIN_REG; CHRG/FAULT stay VIN-level outputs |
| Battery settings | R6 remains 0.20 Ω; R4/R5/R3 remain 60.0 kΩ/220 kΩ/203 kΩ |
| Core charger wiring | Output capacitors, Schottky diodes, NTC, feedback and timer retain the corrected Rev A topology |

Passing those checks establishes CAD connectivity and geometry. It does not
establish switching stability, thermal performance, efficiency, or real charging.

## 3. Bench equipment and setup

Recommended equipment: current-limited bench supply, voltage meter, appropriate
probes/oscilloscope, a battery emulator that can **sink charge current**, suitable
load equipment, and a way to monitor component/cell temperatures. A source-only
bench supply is not a battery emulator.

A resistor can demonstrate loaded operation, but cannot establish charge taper,
termination, or restart as a battery's voltage changes. A suitable electronic load
in constant-voltage mode can support a controlled charging-current test, provided
its startup and compliance behavior suit this charger.

Identify every terminal and test point before applying power. Use voltage mode
for voltage measurements. **Never connect a current-meter input directly across
J2, between TP5 and TP6, or across the input.** A current meter goes in series;
voltage across R6 is the convenient current indication: `I ≈ (TP5 − TP6)/0.20`.
Both R6 terminals are above GND. An earth-referenced oscilloscope ground clip
must not be attached to TP5 or TP6. Use a suitable differential probe or two
channels grounded to board GND and subtract their readings.

For SW measurements, connect a suitable probe to TP7 and use a short ground spring
to TP8. Check the scope, power supply and emulator earth connections before
connecting them. Do not use a long clip-ground loop or accidentally short the
adjacent switch and sense pads. Leave SW probing to a suitably equipped operator.

## 4. Staged physical procedure

1. **Unpowered, no battery:** inspect soldering and component orientation; verify
   F1 continuity, jumper wiring, and the intended input/protected-net connections.
   Check VIN-to-GND and BAT-to-GND for unintended shorts. Capacitors can affect
   resistance readings, so interpret the readings and settling behavior.
2. **No-battery first startup:** fit JP1 closed to disable charging. Connect a
   correctly polarized bench supply at J1, initially 20 V with a 0.10 A limit.
   Confirm TP1, TP2, TP3 and EN/SHDN voltages. Investigate unexpected current draw
   or heating. Input protection does not remove the need for current limiting.
3. **Correct-polarity input path:** verify the fuse drop `TP1 − TP2` and diode
   drop `TP2 − TP3`. Record input current and temperature with the measurement.
   Verify protected VIN is on the intended side of D5.
4. **Reverse-input blocking, still no battery:** disconnect power, discharge and
   verify the relevant capacitors, and retain JP1 closed. Apply a reversed input
   with a low current limit within the source/component ratings. Verify the
   charger-side supply is blocked after settling, apart from leakage/residual
   charge. Record the actual voltages/current. Restore correct polarity before
   proceeding. This is a solar-input test, not a battery-reversal test.
5. **Enable/startup without a lithium cell:** with power removed, open JP1 and
   connect the specified NTC or a temporary 10 kΩ bench resistor at J3. Power from
   the correctly polarized supply and observe BAT voltage and startup waveform.
   When regulating, expect about 4.20 V, including IC/resistor tolerances. A brief
   no-load reading or pulsing behavior needs datasheet/scope assessment; it is not
   proof of stable charging. Stop if BAT exceeds 4.25 V, current/heating is
   unexpected, or the waveform is unexplained.
6. **Controlled charging-current test:** use a suitable battery emulator/load
   near 3.7 V. After safe startup checks, increase the bench input-current limit
   to about 0.30 A if appropriate. The initial 0.10 A setting may limit output;
   do not mistake supply limiting for charger failure. Record current and the
   differential R6 voltage. Nominal targets are 500 mA and 100 mV; the expected
   full-current tolerance is approximately 470–530 mA with the stated parts.
7. **Shutdown test:** compare otherwise equivalent emulator tests with JP1 open
   and closed, changing jumper configuration with power removed. Closed should
   pull EN/SHDN near GND and stop charging after transients; open should restore
   its pull-up and permit charging. Shutdown is not physical battery isolation.
8. **NTC fault tests:** while using the controlled emulator setup, test J3 with
   10 kΩ (normal), 33 kΩ (cold) and 4.7 kΩ (hot). The fault resistors should pause
   charging and turn both LEDs on. A resistor substitution tests the electrical
   threshold path; verify the attached real thermistor's temperature response
   separately. An **open NTC disables monitoring** and is not a shutdown fault.
9. **Regulation/taper/termination/restart:** vary a suitable battery emulator's
   voltage to investigate the CC/CV transition, current taper, and timer behavior.
   The nominal 2.992 h timer can retry if the successful-charge condition has not
   been reached. Both LEDs off does not establish full charge. Record test load,
   input power, cycle duration, threshold readings and current rather than
   asserting a fixed charging time.
10. **Panel/input-regulation test:** use a characterized panel or appropriate
    current-limited panel simulator to check how available input power affects
    charge current and TP3 voltage. Record the actual panel-side voltage as well.
    A stiff bench supply alone does not demonstrate solar maximum-power operation.
11. **Real cell last:** only after the preceding checks are satisfactory, use
    the specified protected lithium-ion cell, correct polarity, and an attached
    10 kΩ/B3380 NTC. Confirm the cell manufacturer permits the charging current
    and voltage. Perform an attended complete charge/temperature test. Use the
    relevant cell protection and appropriately rated battery-side fusing; F1 is
    on the solar input and does not replace those measures.

Do not deliberately short the assembled board to demonstrate F1. A current-limited
small panel may not provide enough fault current to clear a 1 A fuse. Evaluate the
chosen fuse and source from their ratings/curves and a suitable test setup. Neither
F1 nor D5 provides input overvoltage/surge protection or battery reverse-polarity
protection. Inspect and find the cause before replacing a blown fuse.

## 5. Expected-versus-measured worksheet

Record board serial/revision, component substitutions, instrument identities,
input-current limit, panel/emulator settings, ambient temperature, cell model and
capacity, thermistor attachment, date, and photos. Keep the expected column
separate from the measured column. Values below are design expectations.

| Test / condition | Expected | Measured / observed | Pass/fail and notes |
| --- | --- | --- | --- |
| Unpowered VIN/BAT short checks | No unintended short | Not measured | Not measured |
| F1 continuity, no power | Intact series path | Not measured | Not measured |
| TP1 at correctly polarized bench input | Applied input voltage | Not measured | Not measured |
| TP2 / fuse drop | Near input, with part/current-dependent drop | Not measured | Not measured |
| TP3 / D5 drop | TP2 minus D5 forward drop | Not measured | Not measured |
| Reversed input, no battery | Protected side blocked apart from leakage/residual charge | Not measured | Not measured |
| JP1 closed | EN/SHDN near 0 V; charging disabled | Not measured | Not measured |
| JP1 open | EN pulled high through R7; charging permitted | Not measured | Not measured |
| BAT while regulating | About 4.20 V; roughly 4.17–4.23 V tolerance expectation | Not measured | Not measured |
| Emulator near 3.7 V, sufficient input | Approximately 500 mA, roughly 470–530 mA with stated tolerances | Not measured | Not measured |
| TP5 minus TP6 at 500 mA | About 100 mV across R6 | Not measured | Not measured |
| Normal charge indication | Green on above nominal 50 mA status threshold; red off | Not measured | Not measured |
| J3 at 33 kΩ | Cold fault: charging paused; both LEDs on | Not measured | Not measured |
| J3 at 4.7 kΩ | Hot fault: charging paused; both LEDs on | Not measured | Not measured |
| Return J3 to normal condition | Recovery according to NTC hysteresis and charger state | Not measured | Not measured |
| SW at TP7 with short TP8 return | Switching activity consistent with datasheet and load; investigate ringing | Not measured | Not measured |
| Input-regulation point at TP3 | 17.874 V nominal | Not measured | Not measured |
| Corresponding panel-side voltage | TP3 plus D5, fuse and wiring drops | Not measured | Not measured |
| CC/CV taper | Current decreases as battery approaches 4.2 V | Not measured | Not measured |
| Timer termination and restart | According to actual successful-charge/threshold conditions | Not measured | Not measured |
| Component/cell temperatures | Within actual component/cell limits | Not measured | Not measured |
| Complete attended cell charge | Within cell manufacturer's requirements | Not measured | Not measured |

## 6. Evidence for the project presentation

Show the Rev A → Rev B schematic changes, labeled PCB/test points, protection
selection reasoning, fresh CAD reports, and the staged measurement results.
Include photographs and waveforms with identifiable test conditions. Say which
measurements remain unperformed. No manufacturer simulation model was used for
Rev B and no simulation is included; do not use simulation evidence as a claim of
Rev B hardware verification.
