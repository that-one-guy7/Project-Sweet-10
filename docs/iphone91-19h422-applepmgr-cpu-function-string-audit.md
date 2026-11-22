# iPhone9,1 19H422 generic ApplePMGR CPU-function string audit

## Scope and source identity

This note records a read-only inspection of user-supplied output from the generic
`com.apple.driver.ApplePMGR` prelinked KEXT in the iPhone9,1 / D10AP 19H422
KernelCache. It extends the segment map recorded in
[the generic ApplePMGR Mach-O audit](iphone91-19h422-applet8010pmgr-binary-audit.md).

The target KernelCache identity is:

- 19H422 / iOS 15.8.8
- Darwin 21.6.0 / XNU `8020.241.44~1`
- `RELEASE_ARM64_T8010`
- Size: 44,924,928 bytes
- SHA-256: `7b40304d4da951afb6c842477fdfe7ad141a304d32c25ade73d35eb14b238aee`

The generic ApplePMGR prelink header is UUID
`29A10C96-489B-3D22-8D81-974A570645C3`, source version
`939.140.3.0.0`, with `__TEXT_EXEC` VM address
`0xfffffff0065b6000`, inner Mach-O `LC_SEGMENT_64.fileoff` `0x00f4f280`, and size
`0x34a4c`. The header's symbol tables are stripped.

## CPU-related string evidence

The user searched the extracted `ApplePMGR.prelink-text.bin` with
`strings -a -n 5` and a case-insensitive filter for CPU-core, cluster,
idle, and ApplePMGR identifiers. The supplied output includes:

### Core-enable function identifier

- `ApplePMGRFunctionEnableCPUCore`
- `site.ApplePMGRFunctionEnableCPUCore`

These are function/type-name-style identifiers found in the generic
ApplePMGR prelink string region. They are not, by themselves, a named
C++ method definition or proof of a particular callback target.

### Cluster-control methods

- `virtual UInt8 ApplePMGR::getPhysicalClusterID(ApplePMGR::ClusterID)`
- `virtual void ApplePMGR::clearClusterInterruptStatus(ApplePMGR::ClusterID, UInt32)`
- `virtual ApplePMGR::PSLevel ApplePMGR::getClusterPowerState(ApplePMGR::ClusterID, UInt32)`
- `virtual void ApplePMGR::enableCluster(ApplePMGR::ClusterID, bool, bool, UInt32)`

### CPU-idle methods

- `void ApplePMGR::_cpuIdle(ApplePMGR::CPUCore *, bool, UInt64 *)`
- `void ApplePMGR::_cpuIdleTimer(ApplePMGR::CPUCore *, UInt64 *)`
- `void ApplePMGR::_cpuIdleInit(ml_processor_info_t *)`

The same output includes CPU-complex initialization, CPU performance
requests, performance-state accounting, and CPU energy/idle counters. This
places core-enable, cluster-power, and idle-management names in the same
generic PMGR image.

## Interpretation boundary

This is a meaningful lead for the unresolved A10 secondary-core path:

1. Public XNU 8796's `IOPMGR::enableCPUCore(cpu_id, entry_pa)` contract
   concerns releasing a secondary CPU from reset and enabling external IRQ
   delivery; its base fallback reaches an unimplemented panic, as documented
   in the prior audit.
2. The target 19H422 generic ApplePMGR string region names
   `ApplePMGRFunctionEnableCPUCore`.
3. The same region names generic PMGR cluster-control and CPU-idle methods.

However, no supplied evidence yet shows that
`ApplePMGRFunctionEnableCPUCore` is registered or instantiated for the
D10AP target, which method it dispatches to, whether the concrete
`ApplePMGR`/ `AppleT8010PMGR` class satisfies the XNU interface, or whether
the operation performs the required hardware/firmware reset release. The
string filter did not produce a scoped method named
`ApplePMGR::enableCPUCore`; absence from this string output is not proof
that such an implementation is absent.

The separate `AppleT8010PMGR` personality and its declared dependency on
`com.apple.driver.ApplePMGR` remain bundle-level metadata. They do not
establish C++ inheritance or runtime provider matching.

## Executable-segment extraction anomaly

The user extracted the reported `__TEXT_EXEC` range from the local KernelCache:

| Field | Value |
|---|---|
| Inner Mach-O `LC_SEGMENT_64.fileoff` | `0x00f4f280` (not an outer-KernelCache offset) |
| Reported size | `0x34a4c` / 215,628 bytes |
| Extracted size | 215,628 bytes |
| SHA-256 | `355a6e2728742cf65d6d0fe5138b702ee898b3d74a631627de03e584b6a62b99` |
| `file` output | `data` |

The supplied AArch64 objdump begins at VM
`0xfffffff0065b6000`, but its first bytes render as readable diagnostic
strings rather than an identifiable instruction sequence. The full-container
mapping checks now explain the discrepancy:

| Check | Result |
|---|---|
| `ipsw macho a2o "$KC" 0xfffffff0065b6000` | offset `0x01c42000`, section `__text`, segment `__PLK_TEXT_EXEC` |
| `ipsw macho o2a "$KC" 0x00f4f280` | address `0xfffffff0058c3280`, section `__text`, segment `__PRELINK_TEXT` |

Therefore the 215,628-byte artifact extracted at `0x00f4f280` is **not**
the outer-KernelCache bytes backing ApplePMGR's `__TEXT_EXEC` start address.
Its SHA-256 (`355a6e2728742cf65d6d0fe5138b702ee898b3d74a631627de03e584b6a62b99`)
is retained only to identify that mistaken extraction; its diagnostic strings
and disassembly must not be attributed to ApplePMGR executable code. The
correct mapped outer-container offset for the segment's starting virtual
address is `0x01c42000`. The inner KEXT's `LC_SEGMENT_64.fileoff` values are
not absolute outer-KernelCache offsets.

The user tested `ipsw kernel extract` and received
`kernelcache type is not MH_FILESET (KEXT extraction not supported yet)`.
This is expected for the legacy prelinked 19H422 KernelCache: IPSW documents
KEXT extraction for modern `MH_FILESET` images only ([kernel guide](https://blacktop.github.io/ipsw/docs/guides/kernel/)).
Do not repeat that command for this target.

The verified outer-container mapping places the `__TEXT_EXEC` start VA at
`0x01c42000`. Before extraction, map the section boundary addresses
`0xfffffff0065ea583`, `0xfffffff0065ea584`, and the last segment byte
`0xfffffff0065eaa4b` using `ipsw macho a2o "$KC" <address>`. Once the
four address mappings confirm one contiguous executable region, use
`ipsw macho dump "$KC" 0xfffffff0065b6000 --size 215628 --output
"$HOME/ApplePMGR.text-exec.bin"` to dump by virtual address instead of
manually treating the inner load-command fileoff as a container offset.
The [Mach-O dump reference](https://blacktop.github.io/ipsw/docs/cli/ipsw/macho/dump/)
documents address-based dumping to a file. Keep the artifact local.

## Milestone impact

- **M1:** adds target-native PMGR string inventory only.
- **M2 / G1-G3:** unchanged; exact 20H392 XNU source provenance and a
  reproducible target-compatible baseline build remain open.
- **M4 / CPU early initialization:** narrows a candidate PMGR function path,
  but does not close the secondary-core release contract.
- **M7 / SpringBoard:** not started.

This note records static strings and a host-side extraction discrepancy only.
No Apple binary is committed, no runtime behavior is claimed, and no device,
firmware, partition, or boot state was accessed or changed. The physical
iPhone 7 remains on iOS 12.1.4.
