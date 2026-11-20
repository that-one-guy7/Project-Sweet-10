# XNU handoff requirements: evidence checklist

This checklist identifies categories that must be documented before any future
platform design. It intentionally contains no guessed values, register recipes,
device-tree payload, or boot commands.

| Area | Information to establish | Current evidence | Status |
|---|---|---|---|
| Kernel identity | Exact XNU source/build corresponding to selected OS build | Candidate xnu-8796.141.3 only; 20H392 match unverified | Open |
| Entry state | Required exception level, execution state, CPU register assumptions | Not yet verified against selected XNU revision | Open |
| Boot arguments | Required boot-argument structure, version, flags, and memory location | Generic XNU source consumers need review | Open |
| Device tree | Format, version, root properties, required nodes and properties | Consumer-name inventory only; target values unknown | Open |
| Memory map | Usable memory, reserved regions, alignment, ownership and lifetime | No verified iPhone9,1 map | Open |
| CPU topology | CPU identities, startup method, per-CPU data and coherency assumptions | ARM64 source reviewed; target topology unverified | Open |
| Interrupts | Controller type, routing, affinity and interrupt descriptions | No verified target evidence | Open |
| Timers | Counter source, frequency metadata and interrupt integration | Generic property consumers identified; target values unknown | Open |
| Console/diagnostics | Safe early diagnostic channel and failure capture | Not designed | Open |
| Root device | Storage controller, media layout, root discovery and mount path | Not audited | Open |
| Display/HID | Minimum services for visible UI and input | Not audited for A10 | Open |
| Security services | Required platform security dependencies and policy | Not audited; do not weaken policy as a workaround | Open |

## Evidence rules

- Every target-specific value must cite an authoritative source and identify its revision.
- Separate facts read from XNU source from facts about iPhone9,1 hardware.
- Do not infer a device-tree value from a similarly named Qualcomm or virtual device.
- Do not treat a Linux loader's behavior as an XNU ABI.
- Keep the selected iPhone X 20H392 userland distinct from the iPhone 7 target board.
- A source checkout or generic compile is not evidence of boot compatibility.

## Gate

The project remains at source research and host-side validation. This checklist does
not authorize a device boot attempt or changes to boot components.
