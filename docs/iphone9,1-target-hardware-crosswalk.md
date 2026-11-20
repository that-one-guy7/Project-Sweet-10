# iPhone9,1 target-native hardware and service crosswalk

## Purpose

The donor-side 20H392 userland dependency inventory now covers the launchd
GUI chain, BackBoard services, framework-level graphics/I/O dependencies,
and the bounded FontServices/CoreText chain. The next task is to distinguish
which requirements have actual iPhone9,1 evidence from those known only on
the iPhone X donor.

This is a read-only host-side research plan. The iPhone 7 remains on its
existing iOS 12.1.4 installation. Do not restore, update, or change the
device to perform this inspection.

## Evidence sources and boundaries

Use target-native material only when it is specifically identified as
`iPhone9,1` / D10AP / A10-T8010. A useful first reference is an already
available stock iPhone 7 iOS 12.1.4 IPSW (or its extracted BuildManifest,
DeviceTree, kernel collection/kernelcache, and driver metadata).

Important distinctions:

- iOS 12.1.4 target artifacts are evidence of the iPhone 7's original
  hardware configuration and older software stack. They are not an iOS 16
  target system and do not prove that 20H392 userland can run on them.
- iPhone X 20H392 donor artifacts are evidence of the intended donor
  userland's frameworks and service metadata. They do not become target
  artifacts because they are ARM64 or share generic framework names.
- Public XNU source support for a T8010/H9 profile is not enough by itself:
  the exact iOS 16 XNU baseline, machine allowlist, board-specific values,
  dependencies, and kernel handoff contract remain separate questions.
- A framework depending on IOKit does not identify the concrete target
  driver, personality, matched service, DeviceTree node, or hardware resource.
- Keep each finding marked **target-confirmed**, **donor-only**,
  **missing**, or **unverified**.

## Crosswalk table to build

| Requirement / area | 20H392 donor evidence | iPhone9,1 target evidence | Status |
|---|---|---|---|
| Board identity / SoC | donor is iPhone X D22AP / A11-T8015 | exact D10AP / T8010 properties needed | unverified |
| Display controller / framebuffer | IOMobileFramebuffer and CoreGraphics loader records | target DeviceTree and driver identifiers needed | unverified |
| Touch input / HID | BackBoardHIDEventFoundation and Processors | target touch controller, HID provider, and driver identifiers needed | unverified |
| IOKit services | donor frameworks name IOKit | target personalities and matched services needed | unverified |
| BackBoard service layer | BackBoardServices, BoardServices, BaseBoard | target-compatible providers and board services needed | unverified |
| Font / graphics support | CoreGraphics, CoreText, FontServices donor chain | relevance to first SpringBoard milestone not yet established | unverified |
| Launch services | launchd inventory and donor MachServices names | target-side service/provider equivalents needed | unverified |
| Kernel baseline | pinned candidate XNU source; A10 profile issue documented | exact source mapping and target interfaces needed | unverified |

## Host-side inspection workflow

1. Locate an already-downloaded iPhone 7 iOS 12.1.4 IPSW or an extracted
   copy. Do not connect the phone or use a restore/update workflow.
2. Confirm its BuildManifest identifies `iPhone9,1` and the expected
   D10AP board configuration before treating any component as target evidence.
3. Record the exact component identifiers and paths for the target's
   DeviceTree and kernel-related artifacts. Preserve hashes and build
   identifiers in a local research log.
4. Inspect the DeviceTree statically for display, touch, interrupt, GPIO,
   clock, power, and IOMobileFramebuffer-related nodes. Record names and
   compatible strings only; do not infer register values or runtime support
   from a name alone.
5. Inventory the target's available kernel/driver identifiers using
   read-only extraction tools. Keep driver names, personalities, bundle IDs,
   and matching properties separate.
6. Map only concrete donor requirements to target evidence. Generic names
   such as IOKit, CoreFoundation, and Foundation are not enough to claim
   hardware compatibility.
7. Update the table above with source paths, hashes, and the exact evidence
   supporting each status.

## Required output

Produce a reviewed target/donor matrix with:

- IPSW build and product type;
- DeviceTree component name and SHA-256;
- target board and SoC identifiers;
- display and touch node identifiers;
- available driver/personality names;
- donor framework/service requirement;
- evidence status and unresolved gap.

Do not copy proprietary binaries, keys, personal data, or full firmware
images into the Git repository. Commit only sanitized names, hashes,
source references, and conclusions.

## Stop conditions and acceptance criteria

Do not call the target compatibility matrix complete until every claimed
match has an actual iPhone9,1 source artifact and the relevant interface
relationship is documented. A matching string is a lead, not proof.

This work does not make an iPhone 7 iOS 16 bootable and does not establish
SpringBoard readiness. M6 remains in progress; M7 has not started.

## References

- [20H392 FontServices and CoreText dependency results](20h392-fontservices-coretext-dependency-results.md)
- [20H392 IOKit and font-framework dependency results](20h392-iokit-font-framework-dependency-results.md)
- [Project Sweet-10 kernel implementation readiness](kernel-implementation-readiness.md)
- [Apple dyld PrebuiltLoader design](https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md)
