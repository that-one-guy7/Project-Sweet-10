# ios-sweet patch-series triage

Reviewed against the public patch filenames and the source of selected platform patches
at the recorded upstream revision. This is a classification aid, not a patch port.

Reference: https://github.com/dipa-studio/ios-sweet/tree/main/xnu/patches

## Categories

| Upstream patch area | SWEET purpose evidenced by source | Project Sweet-10 decision |
|---|---|---|
| 0001–0002 compiler compatibility | Clang build compatibility and UIO_STACKBUF backport | Re-evaluate independently against the pinned XNU and toolchain |
| 0003, 0010–0012 framebuffer/debug | SWEET framebuffer console, memory layout, and debug output | Do not port hardware addresses or framebuffer code; generic logging ideas only |
| 0004, 0006 machine configuration | Adds SWEET machine config, compiler flags, and ARM behavior | Do not port; A10 requires its own verified machine configuration |
| 0005 pointer-auth build fixes | Build compatibility for SWEET's plain arm64 target | Reassess against actual A10 build target; do not assume same CPU feature set |
| 0007–0009, 0013–0015 runtime/build stubs | Fills build/runtime gaps for that experimental environment | Review one by one only after baseline build; preserve security semantics where possible |
| 0016 platform expert | Matches `xiaomi,sweet` and publishes SWEET device-tree nodes | Not portable; board identity and ADT are different |
| 0017 timer/interrupt changes | Reads SWEET virtual-timer INTID and handles its interrupt path | Not portable; interrupt controller and routing must be evidenced for iPhone9,1 |
| 0018 boot CPU driver | Implements a SWEET-specific CPU provider and single-CPU initialization | Not portable; CPU topology/startup contract is different |
| 0019–0027 pthread, crypto, ramdisk, HFS staging | Makes selected dependencies available to SWEET's build/root setup | Analyze dependencies separately; do not adopt root/security bypass behavior |
| 0028–0037 UFS/root volume | SWEET-specific storage and root-volume integration | Not portable; storage path and filesystem must be independently investigated |
| 0038–0057 security, watchdog, crash/debug, surface | SWEET runtime adaptation and observability | Treat security-affecting changes as out of scope; diagnostics only after review |
| 0058–0065 HID, identity, touch, power, SMP | Goodix/GENI/SPMI and Qualcomm CPU/power support | Not portable; iPhone7 has different input, button, power, and CPU platform |
| 0066–0081 fault, display, USB, SMP, network | SWEET-specific diagnostics and Qualcomm peripherals | Not portable; use only as examples of subsystem separation |

## Concrete source observations

- Patch 0004 adds `SWEET` to supported ARM64 machine configurations and adds a
  Qualcomm-oriented CPU target flag. Its IRQ and TrustZone comments describe the
  SWEET board, not A10.
- Patch 0016 matches the compatible string `xiaomi,sweet` and supplies a
  `SweetPlatformExpert` with a SWEET product identity.
- Patch 0017 obtains a timer interrupt ID from SWEET's device tree and uses it in
  SWEET's interrupt path.
- Patch 0018 identifies its CPU as Kryo 470 and explicitly limits its initial CPU
  implementation. Neither its CPU identity nor its startup assumptions apply to A10.

These are decisive reasons not to copy the SWEET machine config, platform expert,
interrupt patch, or CPU driver into Project Sweet-10.

## Safe reuse rule

Only reuse a concept after identifying the exact upstream source change, its dependencies,
the hardware assumptions it encodes, and a test that applies to the new platform. Keep
original upstream patch files in the upstream repository; this repository records analysis
rather than republishing their full copyrighted contents.
