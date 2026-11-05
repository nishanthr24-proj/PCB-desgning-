# Solar charger simulation demonstration

## Start here — easiest option

1. Extract the complete ZIP.
2. Double-click **START_HERE.html** and open it in **Microsoft Edge, Google Chrome,
   or Firefox**. You do not need KiCad, Python, or a simulator to view this page.
3. Select **Charge, taper, and finish**, then press **Play results**.
4. Use the timeline or the event buttons to jump to a condition. Try the
   **Hot / cold fault and recovery** and **Bad-battery timeout** cases next.

The page works offline. It shows battery voltage and model state of charge,
charging current, net cell current, solar-panel voltage, sensor temperature, and
the green/red LEDs. The LEDs are driven by the **simulated LED branch currents**.
CSV export and plots are included. Green and red also have ON/OFF text labels.

**The browser is a viewer of completed SPICE results, not a live SPICE engine.**
Changing the playback position or speed does not re-run the circuit. To change
component values or test inputs, use ngspice as described below.

## What this simulation establishes

This is a runnable **educational averaged behavioral equivalent** of the intended
Rev A charger. It is **not** the Analog Devices/Linear Technology LT3652
manufacturer model, a pin-for-pin LT3652 model, a KiCad-board simulation, or proof
that an assembled board works. The manufacturer model-download host was blocked
by this environment's network policy; a manufacturer model was not obtained or
validated. No claim is made that such a model is unavailable elsewhere.

The behavioral charger controls and status logic implement selected nominal
datasheet behaviors. The solar-source and battery models make explicit simplifying
assumptions. Resistors, capacitors, diodes, switches, and behavioral sources are
solved by **ngspice 44.2**. The supplied seven transient runs completed, with
**40 regression checks passed and 0 failed**. Read `results/VALIDATION.json` for
the actual checks and values, rather than interpreting that as hardware approval.

The project PCB and its ERC/DRC checks are separate from this simulation package.

## Files and recommended apps

| File | Open with | Purpose |
| --- | --- | --- |
| `START_HERE.html` | **Edge / Chrome / Firefox** | Offline presentation viewer with animated indicators and interactive plots |
| `Simulation_Report.pdf` | Edge, Adobe Reader, or any PDF reader | Static report and waveforms for a project presentation |
| `spice/*.cir` | **ngspice** | Actual runnable circuit testbenches |
| `spice/behavioral_core.inc` | Text editor; included automatically by ngspice | Shared educational charger/battery/panel model |
| `results/*.csv` | Excel / LibreOffice Calc | Full transient data, including measured branch currents |
| `results/*.raw` | ngspice (`load filename.raw`) | Native ngspice simulation results |
| `results/*.log` | Text editor | Completion evidence from the simulator |
| `results/VALIDATION.json` | Text editor or browser | Numerical test results and scope |
| `run_simulations.py`, `validate_results.py` | Python 3 | Re-run and verify all cases |
| `viewer_template.html` | Text editor | Viewer source, before SPICE data is embedded |

KiCad's PCB Editor does not run these files. No LTspice compatibility claim has
been tested; use **ngspice** for reproduction, and a browser for presentation.

## Conditions demonstrated

| Test | Input / fixture | Expected modeled behavior |
| --- | --- | --- |
| 01: Normal charge | Bright sun; initial SOC 20% | 500 mA CC charging, voltage approaches 4.2 V, current taper, green goes off below C/10, timer termination near 6 simulated hours |
| 02: Temperature | Sensor goes from 25°C to 55°C, normal, −10°C, normal | Charging pauses for hot/cold faults, both LEDs turn on; charging resumes after recovery |
| 03: Sunlight | Irradiance 100%, 15%, 2%, 0%, then 100% | Current reduces under cloud, can reach zero before the cell is full, stops overnight, and resumes at sunrise |
| 04: Bad battery | Deliberately stuck low-voltage battery fixture | 75 mA preconditioning, then red-only timeout fault at approximately 22.4 minutes; charge stops |
| 05: Preconditioning | Low-voltage model cell whose voltage can recover | Starts at 75 mA, then transitions to 500 mA after the threshold is exceeded |
| 06: Load / restart | 150 mA external load after termination | Cell discharges, then the charger restarts below the recharge threshold; net cell current differs from charger current |
| 07: Open sensor | Sensor disconnected before a hot condition, then reconnected | Temperature monitoring is disabled while open; reconnecting it while hot triggers the fault |

The bad-battery fixture freezes its model state of charge. It represents a failure
to recover voltage, not a detailed electrochemical failure or a real cell test.
The preconditioning example is not advice to recover an overdischarged real cell.

## Time, battery, and panel assumptions

- **One SPICE simulation second represents one hour of charging.** The SOC
  integrator and timers are scaled accordingly. Thus a 12-second transient shows
  a 12-hour charging scenario. The viewer labels the horizontal axis in hours.
- The display playback speed is separate: at 0.5 hours per wall-clock second,
  an eight-hour scenario plays in about 16 seconds. It does not predict a real
  cell's exact charge time.
- Battery capacity is **2.5 Ah**, chosen for the demonstration; this was not a
  specified or measured capacity of your real 18650 cell.
- The cell model uses **0.15 ohm** series resistance and a piecewise approximate
  open-circuit-voltage versus SOC curve. SOC is computed by integrating **net cell
  current**; it is not inferred from a voltage animation.
- The panel model is a simple one-diode source with **22 V open circuit**, about
  **0.32 A short circuit**, and a maximum-power voltage around **18 V** at full
  irradiance. It is a surrogate for the selected nominal 12 V panel.
- `sun=1` means full relative irradiance; `sun=0` means night. These are normalized
  inputs, not a weather forecast, exact light level, or temperature-corrected panel.
- The input regulator target is **17.874 V**, the same nominal divider setting as
  Rev A. This is fixed input-voltage regulation, not dynamic perturb-and-observe MPPT.
- A fixed **88% power-stage efficiency** is an assumption used for panel loading,
  not a measured or predicted efficiency of the board.

## Correspondence to Rev A

- `R6 = 0.20 ohm`: `I_MAX = 0.100/R6 = 0.500 A`.
- `RFTOP = 60 kohm`, `RFBOT = 220 kohm`:
  `V_FLOAT = 3.3 × (1 + 60/220) = 4.200 V`.
- `RIN_TOP = 562 kohm`, `RIN_BOT = 100 kohm`:
  `V_IN_REG = 2.7 × (1 + 562/100) = 17.874 V`.
- Preconditioning uses **15% of I_MAX = 75 mA** below the nominal 2.3/3.3
  feedback threshold. Preconditioning hysteresis is simplified.
- Timer period is **0.68 µF × 4.4e6 = 2.992 hours**, with approximate one-eighth
  preconditioning timeout. End-of-cycle decisions use a narrow sampling window;
  they are not cycle-accurate digital models of the IC's internal timer.
- NTC uses **10 kohm at 25°C, B3380 K**, with 50 µA nominal bias and approximate
  datasheet voltage thresholds/hysteresis. Its low-supply bias ramp is a numerical
  modeling choice. Disconnected-pin voltage is not modeled; monitoring is explicitly
  disabled by the test-fixture input, matching the intended open-sensor behavior.
- LED branches use the Rev A **10 kohm current-limiting resistors** and **100 kohm
  pull-ups**, with generic green/red diode models. The zero-volt `VLED_GREEN`,
  `VLED_RED`, `VSENSE`, and `VBATMON` sources are virtual current meters.

## Re-run one case in ngspice

Download a current ngspice build from the official page:
<https://ngspice.sourceforge.io/download.html>.

On Windows, extract/install the package and find `ngspice.exe`. Depending on the
build, the console executable can instead be called `ngspice_con.exe`. Substitute
its actual path in the commands. On Debian/Ubuntu a normal installation is
`sudo apt install ngspice`; other systems can use their normal package manager.

Open a terminal **inside the extracted `spice` folder**, then start:

```text
ngspice 01_normal_charge.cir
```

At the ngspice prompt:

```text
run
plot v(bat)
plot i(vsense) i(vbatmon)
plot i(vled_green) i(vled_red)
```

Here the raw SPICE time axis is in seconds: **1 second = 1 modeled charging hour**.
`i(vsense)` is charger current; `i(vbatmon)` is net current entering the model cell.
Positive cell current means charging; negative means discharge.

For a batch run, for example:

```text
ngspice -b -r ../results/my_run.raw -o ../results/my_run.log 02_temperature_faults.cir
```

Use an installed ngspice with graphics support for interactive `plot`. If that
build has no plot window, use the supplied browser viewer or export/plot CSV data.
The ngspice program itself is not bundled in this ZIP.

## Re-run all cases and rebuild the browser viewer

Python 3 is optional for viewing, but is needed for the automation scripts.
Those scripts use only Python's standard library; no pip packages are required.
From the top-level simulation folder:

```text
python run_simulations.py --ngspice "C:/path/to/ngspice.exe"
python validate_results.py
```

On Linux/macOS, replace the path with the local executable or omit `--ngspice`
when it is on PATH. Reopen/reload `START_HERE.html` to view the new results.

Each `.cir` file can be edited directly. To regenerate all fixtures from
`build_cases.py`, first run `python build_cases.py`; this overwrites those case
files. Do not regenerate after manually editing a case unless you want to
replace that edit. `behavioral_core.inc` is shared by all cases. If you alter
Rev A's nominal settings, also update the viewer labels, expected test values,
and documentation that assume 4.2 V / 500 mA.

## What is NOT verified

No real LT3652 transistor/switch model, inductor/boost/catch-diode switching
waveforms, loop compensation, startup transient accuracy, fault-edge transient
accuracy, efficiency prediction, junction heating/thermal foldback, PCB parasitics,
EMC, reverse-polarity behavior, lithium chemistry, cell protection electronics,
production tolerances, or real hardware charging has been verified.

The model deliberately replaces the switching power stage with an averaged source.
The browser omits the first 0.01 modeled hour from plots of long-term behavior;
the full raw files and CSV data remain available. Plots use hour-scale ranges
and are not a basis for interpreting fast transient spikes.

For a presentation, say:

> “We designed the charger PCB in KiCad and demonstrated its intended charging
> and LED logic with an averaged behavioral model in ngspice. This demonstrates
> the control behavior under the modeled assumptions. Manufacturer-model and
> physical-board validation remain to be completed.”

## References

- Project revision: <https://github.com/nishanthr24-proj/PCB-desgning-/tree/main/solar-charger-led-revA>.
- Analog Devices/Linear Technology LT3652 datasheet, revision 3652fe:
  <https://www.analog.com/media/en/technical-documentation/data-sheets/3652fe.pdf>.
  Pin functions, status truth table, timer, NTC, and component-setting formulas
  inform the nominal behavioral equivalent. It is not an official vendor model.
- ngspice documentation: <https://ngspice.sourceforge.io/docs.html>.
- Viewer requires a modern JavaScript-enabled browser, uses system fonts and
  embedded simulation data, and makes no external network requests to operate.
