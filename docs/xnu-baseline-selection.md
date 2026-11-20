# XNU baseline selection

## Selected source candidate

For source review, Project Sweet-10 now pins Apple's public XNU tag:

- Tag: `xnu-8796.141.3`
- Commit: `1b191cb58250d0705d8a51287127505aa4bc0789`
- Annotated tag object: `f625db25f47631424dc62ac1c3414b6e530f7e8a`
- Tag object signature status reported by GitHub: unsigned
- Lock record: `xnu/BASELINE.lock.json`

The exact commit and annotated tag object were read from Apple's GitHub API. The tag is
not cryptographically signed according to the GitHub tag metadata, so the SHA is the
integrity pin; do not describe the tag as signed or verified.

## Why this candidate

The ios-sweet project documents that its macOS 13.5 build path fetches the xnu-8796
generation, and its XNU README describes that family as the iOS 16 generation. A
version mapping for macOS 13.5 identifies xnu-8796.141.3. This makes it a sensible
candidate for source-level study.

This is not proof that the exact kernel build matches iOS 16.7.16 on any target device,
and it does not imply iPhone9,1 platform support. Before any kernel build configuration
is chosen, record the target userland build and verify the corresponding kernel version
from authoritative build metadata.

## Build environment observations from ios-sweet

Its current workflow:
- Uses macOS 14 runners.
- Pins blacktop/darwin-xnu-build at commit
  `663906528d1cd5ea8fde7de6f16de73db9511549`.
- Uses Xcode 15-era tooling because its notes say Xcode 16's IIG output is incompatible
  with that XNU generation.
- Selects the SWEET machine configuration and changes build architecture flags.
- Applies its own patch series in order.

Those settings are evidence about the SWEET build, not a ready-made Project Sweet-10
build configuration. We should initially reproduce an unmodified baseline, then isolate
toolchain compatibility from platform code.

## Next validation gates

1. Confirm the exact target iOS 16 userland build we intend to study.
2. Confirm its reported Darwin/XNU version using public metadata or a user-supplied
   build manifest; do not infer it solely from the marketing version.
3. Reproduce a source checkout at the locked SHA.
4. Record toolchain versions and a clean baseline build result.
5. Only then begin a separately reviewed iPhone9,1 platform design.

No physical-device boot or installation is part of this phase.
