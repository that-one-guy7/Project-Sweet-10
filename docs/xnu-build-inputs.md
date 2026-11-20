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
| Exact shipped Darwin/XNU version | Determines whether source revision matches userland | Unknown |
| Host OS version | XNU build scripts and SDK tools are host-dependent | Not selected |
| Xcode and command-line tools | Compiler, linker, SDK, and IIG compatibility | Not pinned |
| SDK and platform | Selects headers, target macros, and platform build rules | Not verified |
| Architecture configuration | Selects architecture-level source/configuration | ARM64 is the research family; build selection unverified |
| Machine configuration | Selects machine-specific support | No verified T8010 configuration identified |
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
