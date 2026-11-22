# iPhone9,1 19H422 AppleT8010PMGR prelinked KEXT static audit

## Scope and conclusion

This note records a read-only inspection of the target-native
`com.apple.driver.AppleT8010PMGR` record and its prelinked Mach-O segments
from the iPhone 7 / iPhone9,1 / D10AP iOS 15.8.8 (19H422) KernelCache.

The inspection adds concrete evidence that the target KernelCache contains a
T8010-specific PMGR subclass with CPU performance-state, voltage/PLL,
wakeup-source, energy-accounting, ACC-register, and AOP-register interfaces.
It does **not** establish the driver's runtime behavior, the exact implementation
of XNU's secondary-core release path, or binary compatibility with the iOS 16
20H392 donor kernel.

The project target remains iPhone 7 / `iPhone9,1`; iPhone X / `iPhone10,3`
20H392 remains the donor userland reference. The physical iPhone remains on
iOS 12.1.4. All inspection described here was host-side and read-only.

## Source artifact identity

| Field | Recorded value |
|---|---|
| Target IPSW build | iOS 15.8.8 / 19H422 |
| Product / board | iPhone9,1 / D10AP |
| KernelCache SHA-256 | `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee` |
| KernelCache size | 44,924,928 bytes |
| Kernel identity | Darwin 21.6.0 / XNU `8020.241.44~1` |
| Kernel configuration | `RELEASE_ARM64_T8010` |
| KEXT inventory | 230 records |

This is target-native iOS 15 kernel evidence, not the iPhone X / 20H392
iOS 16 donor KernelCache. The two kernel generations must not be conflated.

## Prelink metadata record

The `ipsw kernel kexts --json` record identifies:

| Field | Value |
|---|---|
| `CFBundleIdentifier` | `com.apple.driver.AppleT8010PMGR` |
| `CFBundleName` | `AppleT8010PMGR` |
| `CFBundleExecutable` | `AppleT8010PMGR` |
| Version | `1` / `1.0` |
| Minimum OS | `15.8` |
| Platform | `iPhoneOS` |
| Embedded SDK | `iphoneos15.8.internal` |
| Embedded SDK/platform build | `19H402` |
| Personality | `AppleT8010PMGR` |
| `IOClass` | `AppleT8010PMGR` |
| `IONameMatch` | `pmgr1,t8010` |
| `IOProviderClass` | `AppleARMIODevice` |

The metadata lists these required bundle libraries:

- `com.apple.driver.AppleARMPlatform` version `1.0.0`
- `com.apple.driver.ApplePMGR` version `1.0`
- `com.apple.kec.Libm` version `1.0.0`
- `com.apple.kpi.bsd`, `iokit`, `libkern`, `mach`, `private`, and `unsupported`

The `IOPlatform*Action` fields in this personality are all recorded as
zero. This is metadata, not proof that sleep, wake, halt, or restart actions
are implemented as no-ops; interpretation requires the matching IOKit
framework contract and runtime path.

## Mach-O header and prelinked segments

The prelink record reports:

| Field | Value |
|---|---|
| `_PrelinkExecutableLoadAddr` | `0xfffffff00584f300` |
| `_PrelinkExecutableSize` | `0x11fb` / 4,603 bytes |
| `_PrelinkKmodInfo` | `0xfffffff007b03580` |
| KernelCache file offset for the `__TEXT` start | `0x00edb300` |

The `ipsw macho a2o` result independently mapped the `__TEXT` load
address to file offset `0xedb300`, in `__PRELINK_TEXT`. The user extracted
that 4,603-byte region and reported SHA-256:

```text
c903d96cb70e04cd7f8d48a096800af2853504e480e23e9bd87a1faef3303221
```

The extracted header parses as a 64-bit ARM64 Mach-O with:

- Magic `0xfeedfacf` (`MH_MAGIC_64`).
- CPU type `0x0100000c` (`CPU_TYPE_ARM64`).
- File type `11` (`MH_KEXT_BUNDLE`).
- Ten load commands.
- UUID `899848A2-F91F-3D46-B6CE-25A8A5E58637`.
- An empty `LC_SYMTAB` (zero symbol entries) and empty dysymbol table.

The extracted `__TEXT` header is **not a self-contained standalone KEXT**:
its load commands describe additional segments whose file offsets refer to
locations in the original prelinked KernelCache. The separate code segment
therefore had to be extracted from the original KernelCache as well.

### Executable segment

The Mach-O segment inspection recorded:

| Segment / section | Virtual address | Size | Inner Mach-O LC fileoff (outer-container mapping not yet checked) |
|---|---:|---:|---:|
| `__TEXT_EXEC` | `0xfffffff0068ac000` | `0x3a88` | `0x0105cd00` |
| `__TEXT_EXEC.__text` | `0xfffffff0068ac000` | `0x38b4` | `0x0105cd00` |
| `__TEXT_EXEC.__stubs` | `0xfffffff0068af8b4` | `0x1d4` | `0x010605b4` |

An earlier host extraction treated the reported inner Mach-O `fileoff` as
an absolute offset in the outer KernelCache. The resulting 14,984-byte file
was instruction-decodable, but the virtual-address-to-container-offset
mapping for this T8010 segment has not been independently verified. Until
that address/file mapping is checked against the full 19H422 KernelCache,
the extracted bytes should not be treated as confirmed AppleT8010PMGR code.

## Static method-name and diagnostic-string inventory

The extracted `__TEXT` string table contains the following method-name
strings. These are evidence that the prelinked image includes metadata or
diagnostic strings for these methods; they do not by themselves prove the
precise control flow or runtime effect of each method.

### Initialization, clocking, and voltage

- `AppleT8010PMGR::initDriver(IOService *)`
- `AppleT8010PMGR::getCPUVoltageRailIDS(UInt32)`
- `AppleT8010PMGR::getISPRefClockFrequency(UInt32, UInt32, UInt32)`
- `AppleT8010PMGR::setPLLOffMode(ApplePMGR::RegMap, UInt32, UInt32, UInt32)`
- `AppleT8010PMGR::enableAPSC(ApplePMGR::VoltageRail, bool)`
- `AppleT8010PMGR::enableDVMR(ApplePMGR::VoltageRail, bool)`
- `AppleT8010PMGR::_setSocHotDivider(UInt32)`

### CPU performance and energy accounting

- `AppleT8010PMGR::translateCPUStateToPerf(...)`
- `AppleT8010PMGR::_translateCPUPerfToState(UInt32, bool)`
- `AppleT8010PMGR::getPerfStatePower(...)`
- `AppleT8010PMGR::setPerfStateCPU(ApplePMGR::PerfState, bool, bool)`
- `AppleT8010PMGR::setPerfState(...)`
- `AppleT8010PMGR::perfStateChangePending(...)`
- `AppleT8010PMGR::getPerfStateTableIndex(...)`
- `AppleT8010PMGR::enableCPUPerfCounters(UInt32, bool)`
- `AppleT8010PMGR::enableCPUEnergyAccumulators(UInt32, bool)`
- `AppleT8010PMGR::setCPUCoreEnergyAccumulator(UInt32, UInt64)`
- `AppleT8010PMGR::getCPUCoreEnergyAccumulator(UInt32)`
- `AppleT8010PMGR::calculateCPUEnergyAccumulatorsTuning()`

### Wakeup and register access

- `AppleT8010PMGR::setAPWakeupSources(UInt32 *)`
- `AppleT8010PMGR::readACCReg32(UInt32)`
- `AppleT8010PMGR::writeACCReg32(UInt32, UInt32)`
- `AppleT8010PMGR::readACCReg64(UInt32)`
- `AppleT8010PMGR::writeACCReg64(UInt32, UInt64)`
- `AppleT8010PMGR::readAOPGlobalReg(UInt32)`
- `AppleT8010PMGR::writeAOPGlobalReg(UInt32, UInt32)`

Other strings include performance-domain labels such as
`e-overlap-low`, `p-overlap-high`, `ecore-static-vvfc`, and
`pcore-static-vvfc`, along with assertions concerning PLL indexes,
voltage rails, performance-state tables, wakeup masks, and ACC register
ranges.

This inventory supports a target-specific PMGR role in CPU performance,
voltage, clock, wakeup, and energy management. It does not establish that
the driver itself implements the secondary-core release method
`IOPMGR::enableCPUCore`.

## CPU-start interpretation

The earlier XNU source comparison documented this generic path:

1. `cpu_start()` prepares per-CPU state.
2. `PE_cpu_start()` calls the platform SMP hook.
3. `AppleARMSMP::PE_cpu_start()` invokes `IOPMGR::enableCPUCore()`.
4. The concrete platform power manager and firmware/reset-vector state must
   provide the compatible release behavior.

The new `AppleT8010PMGR` string inventory does not expose a named
`enableCPUCore` method. That is **not proof that the target PMGR cannot
start a secondary CPU**: the method may be implemented in the generic
`ApplePMGR` base class, another platform component, through a non-string
symbol, or through a different call path. The extracted KEXT has no ordinary
symbol-table entries, so method-name strings alone cannot settle the
override/inheritance question.

The most useful next static comparison is the target's generic
`com.apple.driver.ApplePMGR` implementation and its interface relationship
to `AppleT8010PMGR`, cross-referenced with the exact XNU 7195/8796
`IOPMGR::enableCPUCore` overloads already audited in PR #142. Do not
conclude that the CPU-start path works or fails from this PMGR subclass
inventory alone.

## Follow-up: generic ApplePMGR bundle metadata

A separate target 19H422 `ipsw kernel kexts --json` record was inspected for
`com.apple.driver.ApplePMGR`, which the `AppleT8010PMGR` record declares
as a required bundle library at version `1.0`.

The generic/base bundle metadata reports:

| Field | Value |
|---|---|
| Bundle identifier | `com.apple.driver.ApplePMGR` |
| Bundle executable | `ApplePMGR` |
| Version | `1` |
| Bundle path | `/System/Library/Extensions/ApplePMGR.kext` |
| `_PrelinkExecutableLoadAddr` | `0xfffffff005666d80` |
| `_PrelinkExecutableSize` | `49,023` bytes (`0xbf7f`) |
| `_PrelinkKmodInfo` | `0xfffffff007ae12c0` |

Its serialized IOKit personality is distinct from the T8010 subclass
personality:

| Field | ApplePMGR record |
|---|---|
| Personality key | `AppleBringUpPMGR` |
| `IOClass` | `AppleBringUpPMGR` |
| `IOProviderClass` | `AppleARMIODevice` |
| `IONameMatch` | `pmgr1,bring-up` |
| `IOPlatformQuiesceAction` | `90000` |
| `IOPlatformWakeAction` | `600` |
| Halt/restart, active, and sleep action fields | `null` in the serialized JSON |


### Generic ApplePMGR Mach-O header and segment map

The extracted 49,023-byte prelink `__TEXT` region was parsed as a 64-bit
ARM64 `MH_KEXT_BUNDLE` with 10 load commands. The user-supplied
`ipsw macho info --loads` output reports:

| Field / segment | Value |
|---|---|
| `LC_UUID` | `29A10C96-489B-3D22-8D81-974A570645C3` |
| `LC_SOURCE_VERSION` | `939.140.3.0.0` |
| `__TEXT` | VM `0xfffffff005666d80`; size `0xbf7f`; extracted header starts at file offset `0` |
| `__TEXT.__const` | size `0x300`; header-relative offset `0x660` |
| `__TEXT.__cstring` | size `0xb61f`; header-relative offset `0x960` |
| `__TEXT_EXEC` | VM `0xfffffff0065b6000`; LC fileoff `0x00f4f280`; size `0x34a4c` |
| `__TEXT_EXEC.__text` | size `0x34584`; LC fileoff `0x00f4f280` |
| `__TEXT_EXEC.__stubs` | size `0x4c8`; LC fileoff `0x00f83804` |
| `__DATA` | VM `0xfffffff007ae12c0`; LC fileoff `0x0247a540`; size `0x4d0` |
| `__DATA_CONST` | VM `0xfffffff006f18e80`; LC fileoff `0x018b2100`; size `0x6c88` |
| `__LINKEDIT` | zero file size in the reported load command |

### Outer-KernelCache address mapping correction

The user verified the segment address against the full 19H422 KernelCache
using the bidirectional `ipsw macho` mapping commands:

| Check | Result |
|---|---|
| `ipsw macho a2o "$KC" 0xfffffff0065b6000` | offset `0x01c42000`, section `__text`, segment `__PLK_TEXT_EXEC` |
| `ipsw macho o2a "$KC" 0x00f4f280` | address `0xfffffff0058c3280`, section `__text`, segment `__PRELINK_TEXT` |

The two results prove that the inner KEXT load-command value `0x00f4f280`
is **not** the absolute file offset in the outer KernelCache for virtual
address `0xfffffff0065b6000`. The correct outer-container offset reported
for that starting virtual address is `0x01c42000`. The earlier table's
`KernelCache offset` label was therefore incorrect and has been replaced
with `LC fileoff`. The previous `ApplePMGR.text-exec.bin` extraction at
`0x00f4f280` came from a different mapped address and must not be treated as
ApplePMGR executable code. The `__text`/`__stubs` boundary mappings are now independently confirmed:
all four tested virtual addresses map into `__PLK_TEXT_EXEC` at outer offsets
`0x01c42000`, `0x01c76583`, `0x01c76584`, and `0x01c76a4b`. The last
`__text` byte and first `__stubs` byte map to consecutive file offsets,
and the final byte agrees with the full `0x34a4c` segment size. The `__DATA`
and `__DATA_CONST` inner `fileoff` values remain unmapped to outer-container
offsets.

The fileset-aware extraction route is not supported by this target. The user
tried `ipsw kernel extract` and received:

```text
kernelcache type is not MH_FILESET (KEXT extraction not supported yet)
```

This matches IPSW's documented limitation: `ipsw kernel extract` works on
modern `MH_FILESET` KernelCaches, whereas this 19H422 image is an older
prelinked Mach-O using `__PRELINK_*` regions. Do not retry that command on
this same KernelCache. See the [IPSW kernel guide](https://blacktop.github.io/ipsw/docs/guides/kernel/).

For this legacy layout, continue with the outer-KernelCache virtual-address
mapper and `ipsw macho dump`. The user has now mapped the segment start,
last `__text` byte, first `__stubs` byte, and last segment byte. The verified
results demonstrate one contiguous executable range.

The `__DATA_CONST` segment contains `__got` (`0x400` bytes),
`__mod_init_func` (`0x18`), `__mod_term_func` (`0x18`),
`__const` (`0x57a8`), `__kalloc_type` (`0x5c0`), and
`__kalloc_var` (`0xaf0`). These are useful candidates for later
class/registration metadata inspection, but their presence alone does not
identify a vtable, initializer, or CPU-start implementation.

The `__DATA` start address exactly matches the previously recorded
`_PrelinkKmodInfo` address. The reported `LC_SYMTAB` is stripped and the
dysymbol table has zero local, external, and undefined symbol entries. The
zero-sized `__LINKEDIT` and stripped symbol tables mean the code cannot be
resolved by ordinary symbol names from this extracted KEXT header.

The values printed as `off=` in these embedded KEXT load commands are inner
Mach-O `fileoff` fields. They must not be relabelled as absolute offsets in
the outer KernelCache unless independently verified with the full-container
address mapper. The `__TEXT_EXEC` mapping above demonstrates this distinction.
The executable segment is also separate from, and not contiguous with, the
49,023-byte extracted `__TEXT` header artifact.

By comparison, the T8010-specific bundle record advertises
`IOClass=AppleT8010PMGR` and `IONameMatch=pmgr1,t8010`. Both personality
records name `AppleARMIODevice` as the provider class, but they match
different compatible strings. The T8010 bundle's declared dependency on
`com.apple.driver.ApplePMGR` is positive metadata evidence of a bundle-level
relationship; it does not by itself prove C++ inheritance, which provider
actually instantiates each class on the target DeviceTree, or the implementation
of `IOPMGR::enableCPUCore`.

The action values `90000` and `600` are recorded verbatim. Their units,
call-site interpretation, and runtime effects have not been established and
must not be labelled milliseconds or treated as measured delays.

### Pinned XNU 8796 IOPMGR interface contract

The public `xnu-8796.141.3` source makes the unresolved CPU-start question
more specific:

- `IOPMGR.h` describes `IOPMGR` as the base class for power managers such
  as `ApplePMGR`.
- Its two-argument `enableCPUCore(cpu_id, entry_pa)` contract is to release
  a secondary CPU from reset and enable external IRQ delivery. The physical
  reset-vector argument is not necessarily honored by every platform.
- The older one-argument overload is deprecated.
- In `IOPMGR.cpp`, the default two-argument implementation falls back to
  the one-argument overload; the base one-argument implementation panics
  with "enableCPUCore is unimplemented".

Pinned source references:
[`IOPMGR.h`](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/IOKit/IOPMGR.h#L38-L63)
and
[`IOPMGR.cpp`](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/Kernel/IOPMGR.cpp#L33-L46).

This describes the public 8796 interface and default fallback, not the
private implementation in the 19H422 ApplePMGR/AppleT8010PMGR binaries.
The target binary audit must still determine which concrete class supplies
the required overrides. The source contract also does not prove that the
20H392 donor kernel uses the same exact ApplePMGR implementation.

### Next static check

The user has confirmed that the target KernelCache is 44,924,928 bytes
with SHA-256
`7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`.
The four user-supplied `ipsw macho a2o` results are:

| Purpose | Virtual address | Outer KernelCache offset |
|---|---|---|
| First byte of `__TEXT_EXEC` / `__text` | `0xfffffff0065b6000` | `0x01c42000` |
| Last byte of `__text` | `0xfffffff0065ea583` | `0x01c76583` |
| First byte of `__stubs` | `0xfffffff0065ea584` | `0x01c76584` |
| Last byte of `__TEXT_EXEC` | `0xfffffff0065eaa4b` | `0x01c76a4b` |

All four map to `__PLK_TEXT_EXEC`. The `__text` and `__stubs` sections
are contiguous: `0x01c76583` is immediately followed by `0x01c76584`.
The mapped range is `0x34a4c` bytes, matching the load-command size.

The next command uses IPSW's documented virtual-address-based Mach-O dump;
it avoids treating the embedded KEXT's inner `LC_SEGMENT_64.fileoff` as an
outer-container offset:

```sh
ipsw macho dump "$KC" 0xfffffff0065b6000 \\
  --size 215628 \\
  --output "$HOME/ApplePMGR.text-exec.bin"

stat -c 'Size: %s bytes' "$HOME/ApplePMGR.text-exec.bin"
sha256sum "$HOME/ApplePMGR.text-exec.bin"
file "$HOME/ApplePMGR.text-exec.bin"

# Only after confirming the file is exactly 215,628 bytes:
aarch64-linux-gnu-objdump -D -b binary -m aarch64 \\
  --adjust-vma=0xfffffff0065b6000 \\
  "$HOME/ApplePMGR.text-exec.bin" | sed -n '1,100p'
```

The `macho dump` command accepts a virtual address and writes the selected
bytes to a file; see the [IPSW Mach-O dump reference](https://blacktop.github.io/ipsw/docs/cli/ipsw/macho/dump/).
Keep any extracted Apple binary local; do not add it to the repository.
The expected size is 215,628 bytes. Stripped symbols, indirect calls, and
class metadata still require careful interpretation. A missing string is
not proof a method is absent.

## Relationship to project milestones

- **M1:** adds detail to the already-completed static hardware/KEXT inventory.
- **M2 / G1-G3:** does not identify the exact 20H392 Apple source revision,
  supply private XNU build inputs, or establish a reproducible XNU 8796 build.
- **M4 / CPU early initialization:** narrows the target PMGR responsibilities
  but does not establish CPU release, reset-vector handling, timer operation,
  or early-kernel execution.
- **M5:** adds target-native static evidence for the PMGR/power-management
  subsystem; runtime attachment and hardware behavior remain unverified.
- **M6 / M7:** no userland, launchd, SpringBoard, or iOS 16 boot conclusion.

## Reproducibility and artifact handling

The source KernelCache identity, KEXT record, segment addresses, sizes, and
user-reported first extraction SHA-256 are recorded above. The raw extracted
binary files are analysis artifacts, not project source. The repository
README already says not to commit proprietary iOS binaries, firmware, or
device dumps. Keep derived metadata, hashes, and concise analysis in Git;
prefer removing the extracted binary files from the public repository after
the audit record is retained. Removing a file from the latest tree does not
remove copies from Git history.

This is static host-side analysis only. No binary was executed, no code was
modified, and no device, firmware, partition, or boot state was accessed or
changed. The iPhone 7 remains on iOS 12.1.4.
