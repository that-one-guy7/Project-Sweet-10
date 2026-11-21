# XNU baseline build inputs: investigation checklist

## Goal

Reproduce an unmodified build of the pinned public XNU source before proposing any
Project Sweet-10 platform changes. This checklist deliberately does not prescribe a
device boot, firmware modification, or installation procedure.

## Required inputs to record

| Input | Why it matters | Current status |
|---|---|---|
| XNU tag and commit | Makes source identity reproducible | Candidate pinned: xnu-8796.141.3 / 1b191cb58250d0705d8a51287127505aa4bc0789 |
| Target userland build | Establishes the OS generation being studied | Selected: iOS 16.7.16 / 20H392, iPhone X family |
| Exact shipped Darwin/XNU version | Determines whether source revision matches userland | Donor KernelCache reports Darwin 22.6.0 and embedded label `8796.142.1.703.8~1`; this label is not an exact public Git tag or source commit |
| Host OS version | XNU build scripts and SDK tools are host-dependent | Not selected |
| Xcode and command-line tools | Compiler, linker, SDK, and IIG compatibility | Not pinned |
| SDK and platform | Selects headers, target macros, and platform build rules | Not verified |
| Architecture configuration | Selects architecture-level source/configuration | ARM64 is the research family; build selection unverified |
| Machine configuration | Selects machine-specific support | Pinned xnu-8796.141.3 normal ARM64 allowlist omits T8010; historical xnu-7195.121.3 list includes it |
| Kernel configuration | Release/development/debug options affect output | Not selected |
| Platform value | Required by MakeInc.kernel validation | Not selected |
| External headers and build dependencies | Public XNU source may require additional inputs | Not audited completely |
| Build result and logs | Distinguishes success from a merely configured tree | No build attempted |

## Build-system observations

The pinned XNU top-level Makefile establishes source, object, destination, and symbol
roots and includes the makedefs make fragments. The kernel make fragment validates
architecture, kernel configuration, machine configuration, and platform as separate
inputs. Therefore a successful ARM64 compiler invocation alone would not demonstrate
that a valid iPhoneOS machine configuration was selected.

The ios-sweet build workflow is useful historical evidence about one downstream build
environment, but its SWEET machine selection and Qualcomm platform patches are not a
Project Sweet-10 build configuration.

## Source identity CI

The repository's xnu-source-check.yml workflow is a read-only identity check, not a
kernel build. It reads commit_sha from xnu/BASELINE.lock.json, checks out that exact
public XNU revision, runs host-side metadata tests, and compares the checkout's HEAD
SHA with the lock. This avoids maintaining a second hard-coded source revision in
the workflow.

A passing result establishes only that the checked-out source matches the project lock.
It does not establish that the source matches 20H392 exactly, compiles with a selected
toolchain, supports iPhone9,1, or can boot on hardware.

## Reproducibility record template

For every baseline attempt, record:

- Repository URL and exact commit SHA.
- Host OS version and CPU architecture.
- Xcode version and active developer directory.
- SDK name and SDK build version.
- Compiler and linker versions.
- Architecture, machine, kernel configuration, and platform selections.
- External dependency revisions.
- Full build command and environment variables.
- Exit status and first actionable error.
- Hashes of resulting build artifacts, if a build succeeds.

Do not upload proprietary iOS binaries, full firmware images, device dumps, private
identifiers, or signing material into this repository.

## Stop conditions

Stop and document the blocker if:
- The source's supported machine configuration list cannot be established.
- The build depends on unavailable proprietary/internal headers or tools.
- The selected configuration is copied from another SoC without evidence.
- The exact 20H392 kernel revision remains unresolved and a claim of exact compatibility
  would otherwise be made.

A successful generic XNU build is only a source/build-system milestone. It is not proof
of A10 platform support, SpringBoard readiness, or a successful iPhone9,1 boot.


## Pinned-source configuration findings

The pinned xnu-8796.141.3 make files establish several separate build inputs:

- MakeInc.cmd resolves SDKROOT with xcrun, derives PLATFORMPATH and PLATFORM
  from that SDK, and locates Apple compiler and interface-generation tools
  through xcrun.
- MakeInc.cmd lists iPhoneOS among supported embedded platform names and
  derives the default device-map database path from the selected platform
  bundle: PLATFORMPATH/usr/local/standalone/firmware/device_map.db.
- MakeInc.top optionally queries the embedded device map for product types,
  kernel architecture, and KernelPlatform, then forms target-configuration
  tuples from kernel configuration, architecture, and machine configuration.
- MakeInc.def defines the normal ARM64 machine allowlist. For
  xnu-8796.141.3 it is BCM2837, T6000, T8101, T8103, and VMAPPLE; T8010 is absent.
- MakeInc.kernel validates the selected architecture, kernel configuration,
  machine configuration, and platform against their supported lists.

The embedded-device-map lookups are conditional on EMBEDDED_DEVICE_MAP being
provided. The project's standalone BuildManifest is not a substitute for that
SDK database, and it does not establish an iPhone9,1 target mapping or a
KernelPlatform value.

### Historical comparison

In xnu-7195.121.3, the normal ARM64 allowlist includes T8010. In
xnu-8019.80.24 and xnu-8796.141.3, it does not. This is consistent with the
historical T8010/H9 source-profile audit: earlier source had an A10-era SoC
configuration, while the selected iOS 16-era public source no longer offers
T8010 as a normal ARM64 machine configuration.

This does not identify the exact removal/refactor commit, prove that every
Apple internal build environment has the same allowlist, or show that merely
restoring the historical list would produce a functioning iPhone9,1 kernel.

## Current build conclusion

A reproducible generic or VMAPPLE build would not validate the missing iPhone7
configuration. Before a target-specific build can be selected, the project
needs authoritative evidence for the intended SDK/toolchain, the device-map
target record (if available), the kernel platform, and the source dependencies
needed for a complete T8010 port. No configuration override or copied
machine-selection value is approved by this checklist.
