# iPhone9,1 19H422 EnableCPUCore callback and XNU contract cross-check

## Scope and evidence boundary

This note joins the target-native 19H422 static class-registration evidence
with public XNU source contracts and a historical A10 symbol inventory. It
is intended to sharpen the next read-only analysis question; it does not
claim that the private ApplePMGR implementation has been recovered.

Target artifact:

- Product: iPhone9,1 / D10AP / A10-T8010
- Build: iOS 15.8.8 / 19H422
- Kernel: Darwin 21.6.0 / XNU `8020.241.44~1`
- Configuration: `RELEASE_ARM64_T8010`
- KernelCache SHA-256:
  `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`

The intended iOS 16 userland reference remains 20H392 on iPhone10,3; it is
not the target KernelCache. The physical iPhone 7 remains on iOS 12.1.4.
This audit uses host-side source and static metadata only.

## Target 19H422 facts already established

The generic `com.apple.driver.ApplePMGR` prelinked KEXT contains the
`ApplePMGRFunctionEnableCPUCore` class-name string and a metaclass
registration sequence. The shared-prelink analysis confirms that this class
uses `AppleARMFunction` as its superclass. The corresponding
`AppleARMFunction` metaclass storage is
`0xfffffff0079e4dd0`.

The target generic ApplePMGR string inventory contains an explicit
`ApplePMGRFunctionCPUIdle::callFunction` signature, but the supplied
filter did not find a corresponding
`ApplePMGRFunctionEnableCPUCore::callFunction` signature. This is a
difference in the observed string inventory only; stripped symbols and
indirect dispatch mean the missing signature is not proof of a missing
override or callback.

The target also has a separate `com.apple.driver.AppleT8010PMGR`
personality with `IOClass=AppleT8010PMGR`,
`IONameMatch=pmgr1,t8010`, and a declared bundle dependency on generic
`com.apple.driver.ApplePMGR`. The generic bundle has a distinct
`AppleBringUpPMGR` / `pmgr1,bring-up` personality. These IOKit
personality and dependency records do not establish the C++ inheritance
chain, which service actually matches the target DeviceTree, or which
class provides the XNU CPU-start override.

The existing target-specific audit lists CPU-performance, voltage, clock,
wakeup, and energy-management strings in AppleT8010PMGR, but did not find
a named `enableCPUCore` implementation in that string inventory.
Again, string non-discovery does not prove the method is absent.

## Public XNU CPU-start contract across three source generations

The same public `IOPMGR` interface was checked at:

- `xnu-7195.121.3` — historical source containing the audited T8010/H9
  machine profile.
- `xnu-8796.141.3` — pinned public candidate used in the 20H392 donor
  baseline investigation.
- `xnu-8020.101.4` — an earlier public snapshot from the same XNU 8020
  line, but not the exact source revision for the target KernelCache's
  reported `8020.241.44~1` version.

Across all three checked tags, `IOPMGR.h` declares the same overloads:

- `enableCPUCore(unsigned int cpu_id, uint64_t entry_pa)`
- deprecated `enableCPUCore(unsigned int cpu_id)`

The two-argument method's documented purpose is to release a secondary
CPU from reset and enable external IRQ delivery. The `entry_pa` argument
is a physical reset-vector address; the interface documentation cautions
that some platforms do not use that argument.

Across the same three tags, the base `IOPMGR.cpp` implementation of the
two-argument method falls back to the one-argument overload. The base
one-argument implementation panics as unimplemented. Therefore a concrete
platform implementation must provide an appropriate override; merely
inheriting both base implementations is not a working CPU-start path.

The public `AppleARMSMP.cpp` path corroborates the relationship: in
`xnu-7195.121.3` and `xnu-8020.101.4`, `PE_cpu_start` routes
secondary CPU start through `gPMGR->enableCPUCore` and supplies the
physical address of `LowResetVectorBase`. The `xnu-8796.141.3`
version also routes through the PMGR interface, with a
`APPLEVIRTUALPLATFORM` conditional around reset-vector handling.

Pinned source locations:

| Source | 7195.121.3 | 8796.141.3 | 8020.101.4 |
|---|---|---|---|
| IOPMGR interface | [IOPMGR.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/iokit/IOKit/IOPMGR.h) | [IOPMGR.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/IOKit/IOPMGR.h) | [IOPMGR.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8020.101.4/iokit/IOKit/IOPMGR.h) |
| Default implementation | [IOPMGR.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/iokit/Kernel/IOPMGR.cpp) | [IOPMGR.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/Kernel/IOPMGR.cpp) | [IOPMGR.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-8020.101.4/iokit/Kernel/IOPMGR.cpp) |
| ARM SMP caller | [AppleARMSMP.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/iokit/Kernel/arm/AppleARMSMP.cpp) | [AppleARMSMP.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/iokit/Kernel/arm/AppleARMSMP.cpp) | [AppleARMSMP.cpp](https://github.com/apple-oss-distributions/xnu/blob/xnu-8020.101.4/iokit/Kernel/arm/AppleARMSMP.cpp) |

**Interpretation:** this establishes a stable public XNU interface contract
across the historical T8010 source, the 20H392 candidate baseline, and a
public XNU 8020 snapshot. It does not identify the private 19H422
ApplePMGR/AppleT8010PMGR override, and `xnu-8020.101.4` is not an
exact source attestation for `8020.241.44~1`.

## Historical A10 function-class symbol precedent

The third-party `iometa` symbol inventory for the iOS 12.0 A10 release
lists these methods under the base `AppleARMFunction` class:

- `initWithTargetDataAndSymbol(IOService*, OSData const*, OSSymbol const*)`
- `callFunction(void*, void*, void*)`

The same A10 inventory lists `ApplePMGRFunctionEnableCPUCore` as a
class name, and lists an `ApplePMGR::enableCPUCores(unsigned int, bool)`
method. The inventory does not list separate per-class method entries
under `ApplePMGRFunctionEnableCPUCore`.

Source:
[`iometa` iOS 12.0 A10-legacy symbol inventory](https://github.com/Siguza/iometa/blob/master/sym/release/iOS-12.0/A10-legacy.txt).

This is historical, third-party symbol data from iOS 12.0, not the
19H422 target. It supports a hypothesis that AppleARMFunction provides
generic target-data initialization and a generic `callFunction`
dispatch surface that subclasses can inherit. It does **not** prove that
the 19H422 EnableCPUCore class inherits that implementation unchanged,
that its callback invokes `ApplePMGR::enableCPUCores`, or that the
method maps to XNU's `IOPMGR::enableCPUCore`.

## Target 19H422 string-inventory follow-up (2026-11-22)

The user supplied a second read-only `strings -a -t x -n 5` scan of the
two extracted target KEXT `__TEXT` regions. The generic ApplePMGR
prelink-header artifact has SHA-256
`4764017feef6d87c1f8a524bf04ec1148817d61fd482639e252325fd0300f43f`.
The AppleT8010PMGR prelink-header artifact has SHA-256
`c903d96cb70e04cd7f8d48a096800af2853504e480e23e9bd87a1faef3303221`.

### Generic ApplePMGR

The output contains the following relevant class/function strings:

| Offset in extracted header | String |
|---:|---|
| `0xa4e6` | `ApplePMGRFunctionCPUIdle` |
| `0xa4ff` | `site.ApplePMGRFunctionCPUIdle` |
| `0xa51d` | `virtual IOReturn ApplePMGRFunctionCPUIdle::callFunction(void *, void *, void *)` |
| `0xa5ac` | `ApplePMGRFunctionEnableCPUCore` |
| `0xa5cb` | `site.ApplePMGRFunctionEnableCPUCore` |

The same scan returns explicit method-name signatures for other function
classes, including `ApplePMGRFunctionClockGate::callFunction`,
`ApplePMGRFunctionROSC::callFunction`,
`ApplePMGRFunctionEnableTouchClock::initWithTargetDataAndSymbol`,
`ApplePMGRFunctionISPRefClock::initWithTargetDataAndSymbol`,
`ApplePMGRFunctionVideoRefClock::initWithTargetDataAndSymbol`,
`ApplePMGRFunctionPLLOffMode::initWithTargetDataAndSymbol`, and
`ApplePMGRFunctionUSBClock::initWithTargetDataAndSymbol`.

The supplied filtered output did **not** include a matching
`ApplePMGRFunctionEnableCPUCore::callFunction`,
`ApplePMGRFunctionEnableCPUCore::initWithTargetDataAndSymbol`,
`AppleARMFunction::callFunction`,
`AppleARMFunction::initWithTargetDataAndSymbol`,
`ApplePMGR::enableCPUCore`, or
`ApplePMGR::enableCPUCores` string. This is a scoped string-inventory
non-match in the extracted generic ApplePMGR header. The base
`AppleARMFunction` implementation may be represented in a different
prelinked component; this scan does not include every KEXT. The result is
not proof that methods, inherited dispatch, or indirect call targets are
absent.

### AppleT8010PMGR

The supplied output includes explicit T8010 method strings for
initialization, voltage/clock control, CPU performance-state translation
and selection, performance counters, CPU energy accumulators, ACC
register access, and AOP global-register access. Representative entries
include:

- `AppleT8010PMGR::initDriver`
- `AppleT8010PMGR::setPerfStateCPU`
- `AppleT8010PMGR::setPerfState`
- `AppleT8010PMGR::enableCPUPerfCounters`
- `AppleT8010PMGR::enableCPUEnergyAccumulators`
- `AppleT8010PMGR::setCPUCoreEnergyAccumulator`
- `AppleT8010PMGR::getCPUCoreEnergyAccumulator`

The supplied filtered output did not contain a named
`AppleT8010PMGR::enableCPUCore`,
`AppleT8010PMGR::enableCPUCores`, or reset routine. This is again only
a method-name string non-match. It does not exclude an inherited method,
a differently named implementation, a function pointer, or code without
a retained diagnostic/signature string.

### Combined interpretation

The string evidence confirms that the EnableCPUCore function class is
named and registered in generic ApplePMGR, while the T8010-specific
string inventory prominently describes CPU performance and energy
management. It does not yet show which code path services the
EnableCPUCore function, nor which concrete class implements the XNU
`IOPMGR::enableCPUCore` virtual method.

The iOS 12.0 A10 symbol inventory's
`ApplePMGR::enableCPUCores(unsigned int, bool)` remains a historical
lead only. Its plural method name and two-argument signature are not
enough to equate it with the public XNU singular
`IOPMGR::enableCPUCore(unsigned int, uint64_t)` interface.

## What remains unproven

1. Whether `ApplePMGRFunctionEnableCPUCore` overrides or inherits
   `AppleARMFunction::callFunction` in 19H422.
2. What target-data structure or function symbol that callback consumes.
3. Whether the function's dispatch reaches a method on generic
   `ApplePMGR`, `AppleT8010PMGR`, another service, or a table-driven
   register operation.
4. Which concrete 19H422 class supplies the required
   `IOPMGR::enableCPUCore` overload.
5. Whether the `pmgr1,t8010` personality actually attaches and the
   CPU-start operation succeeds on the target.

## Next read-only host-side check

The generic and T8010 string scans above are complete. The next useful
target-native artifact is a correctly mapped disassembly of the
`AppleT8010PMGR` executable segment. Its embedded Mach-O header reports:

- `__TEXT_EXEC` base: `0xfffffff0068ac000`
- `__text` size: `0x38b4`
- `__stubs` start: `0xfffffff0068af8b4`
- `__TEXT_EXEC` total size: `0x3a88` (14,984 bytes)

The old extraction treated an inner Mach-O `LC_SEGMENT_64.fileoff` as
an outer KernelCache offset; the outer mapping has not been verified.
First, map the four boundary addresses against the full local 19H422
KernelCache:

~~~sh
ipsw macho a2o "$KC" 0xfffffff0068ac000
ipsw macho a2o "$KC" 0xfffffff0068af8b3
ipsw macho a2o "$KC" 0xfffffff0068af8b4
ipsw macho a2o "$KC" 0xfffffff0068afa87
~~~

Paste the mapping results before extracting or disassembling this
segment. Do not assume the embedded KEXT's inner `fileoff` values are
outer-container offsets. This is static host-side inspection only; leave
the physical iPhone on iOS 12.1.4.

All Apple binaries remain local analysis artifacts and are not included
in this document. No binary is executed, no device/firmware state is
accessed or changed, and the physical iPhone 7 remains on iOS 12.1.4.
