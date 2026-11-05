# Sources and attribution

- Starting project: <https://github.com/Hirusha785/solar-battery-charge-controller-pcb>,
  archive supplied by the user, commit identifier in the ZIP:
  `8adcedc8ef8a8e4cd02e30468040b93200b75584`.
  Its README credits **Fernando S.M.H.G.** This revision is a new corrected
  schematic and PCB layout based on the requested functionality. The supplied
  archive does not include a license; no new license is asserted for upstream work.
- Circuit reference: Analog Devices / Linear Technology **LT3652**, datasheet
  revision `3652fe`, particularly pin functions, component selection, feedback
  compensation, status decoding, temperature monitoring, and layout guidance:
  <https://www.analog.com/media/en/technical-documentation/data-sheets/3652fe.pdf>.
  The official host was blocked by this environment's network policy. The same
  document was read from the public copy at
  <https://github.com/BEEMB/LT3652-MPPT-Solar-Battery-Charger/blob/main/Datasheets/LT3652.pdf>.
  Verify the latest manufacturer documentation and exact orderable part before assembly.
- SparkFun's SunnyBuddy LT3652 schematic was consulted to understand the uploaded
  circuit's origins: <https://github.com/sparkfun/SunnyBuddy>. Its Eagle geometry,
  artwork, and logos were not copied into this PCB. Do not imply either upstream
  author has reviewed or endorsed this revision.
- Local symbols and footprints are copies of standard **KiCad 9 libraries**,
  with project-local library nicknames. They retain the upstream library license
  and its exception. See the included `licenses/` copyright files. The project
  is not assigned a new license on the user's behalf.
