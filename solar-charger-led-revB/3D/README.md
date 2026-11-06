# Revision B populated 3D assembly

The assembly shows the 60 × 55 mm Rev B PCB with its 30 fitted component bodies.
Use it to present the design and inspect placement, component orientation, and
connector access before manufacturing.

## Open and inspect

1. Extract the complete project folder, keeping `3dmodels/` beside the KiCad files.
2. In **KiCad 9 or newer**, open `Solar_Charger_LED_RevB.kicad_pro`, then its PCB.
3. Choose **View → 3D Viewer** or press **Alt+3**. Rotate and zoom to inspect the
   assembly. Model paths use `${KIPRJMOD}/3dmodels` and need no global KiCad model
   package.

To view the standalone assembly in **FreeCAD**, choose **File → Open** and select
[`Solar_Charger_LED_RevB_Assembly.step`](Solar_Charger_LED_RevB_Assembly.step).
The STEP is an exported assembly; make PCB changes in the native KiCad project.

For slides or a report, use the [angled](../previews/PCB_3D.png),
[top](../previews/PCB_3D_Top.png), and [bottom](../previews/PCB_3D_Bottom.png)
PNG views.

## What the model includes

- Component bodies for all 30 fitted parts, aligned with their PCB footprints.
- The board, copper, solder mask, silkscreen, mounting holes, and bare test pads.
- An unshunted JP1 header, corresponding to the normal charging-enabled position.
- Green D3 and red D4 bodies to distinguish the LED parts. These are material
  colors, not illuminated LEDs or a charging/fault demonstration.

H1–H4 are holes and TP1–TP9 are bare pads, so those 13 footprints intentionally
have no separate bodies. The external protected battery, solar panel, external
NTC sensor, connecting wires, mounting screws, and enclosure are not modeled.

## Model accuracy and sources

Most bodies are generic official KiCad package models. Two require particular
care when interpreting dimensions:

| Component | Representation | Limit |
| --- | --- | --- |
| U1, LT3652EMSE | Representative MSOP-12 with 0.65 mm lead pitch and a 3.0 × 4.000 mm body | The nominal LT3652EMSE body length is 4.039 mm; this is not a verified vendor-specific model |
| L1 | Locally created representative envelope, 6.6 × 6.2 × 2.8 mm | Not validated against a selected vendor's mechanical drawing |

Use the actual chosen parts' drawings for procurement, final assembly dimensions,
and enclosure-clearance decisions. A visually plausible fit does not establish
those tolerances.

The official KiCad models are pinned to commit
`b8b3cfdfad88ba66f21002b3de51dc6f7d55ba5a`. See
[`../3dmodels/SOURCES.json`](../3dmodels/SOURCES.json) for individual sources and
[`../licenses/kicad-packages3D-LICENSE.md`](../licenses/kicad-packages3D-LICENSE.md)
for CC BY-SA 4.0 with the KiCad library design exception. Project lineage is in
[`../ATTRIBUTION.md`](../ATTRIBUTION.md).

## Explain it in a presentation

“The populated 3D assembly shows the component arrangement, orientation, and
connector access before manufacturing. We can inspect it in KiCad and share a
STEP assembly with mechanical CAD tools. Charging, LED behavior, and thermal
performance still require electrical testing on an assembled board.”

The 3D addition changes no electrical routing or Gerber geometry. It is a visual
and mechanical review aid, not a simulation or functional test.
