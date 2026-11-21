# iPhone9,1 / D10AP / 19H422 AIC and T8010 KEXT metadata

## Scope and provenance

This note records the user's read-only filter output from:

\`$HOME/19H422-kernel-inspect/analysis/kexts.json\`

The source is the iPhone 7 / iPhone9,1 / D10AP iOS 15.8.8 target-reference KernelCache for build 19H422. It is not the iPhone X / 20H392 iOS 16.7.16 donor KernelCache, and it is not firmware installed on the physical phone. The phone remains on iOS 12.1.4.

The user ran the filter with IPSW 3.1.749-derived KernelCache KEXT metadata. This report preserves only selected bundle and IOKit-personality fields actually printed in the supplied output. It does not include KernelCache or extracted KEXT binaries.

## Principal result: AppleInterruptController is present

The filtered target KEXT JSON contains:

| Field | Supplied value |
|---|---|
| Bundle identifier | \`com.apple.driver.AppleInterruptController\` |
| Name / executable | \`AppleInterruptController\` |
| Bundle path | \`/System/Library/Extensions/AppleInterruptController.kext\` |
| Package type | \`KEXT\` |
| Version | \`1.0.0d1\` |
| Short version | \`1.0.0\` |
| Minimum OS | \`15.8\` |
| SDK / SDK build | \`iphoneos15.8.internal\` / \`19H402\` |
| OS bundle required | \`Root\` |

The supplied \`io_kit_personalities/AppleInterruptController\` object contains:

| Personality field | Supplied value |
|---|---|
| \`IOClass\` | \`AppleInterruptController\` |
| \`IONameMatch\` | \`aic,1\` |
| \`IOProviderClass\` | \`AppleARMIODevice\` |
| \`IOPlatformActiveAction\` | \`0\` |
| \`IOPlatformQuiesceAction\` | \`0\` |

This is an exact static compatible-string match to the already parsed target DeviceTree node \`/arm-io/aic\`, whose \`compatible\` property is \`aic,1\`, whose \`device_type\` is \`interrupt-controller\`, and whose \`interrupt-controller\` property is \`master\`.

**Conclusion:** the initial question of whether the 19H422 target-reference KernelCache metadata contains an AppleInterruptController KEXT and an \`aic,1\` personality is resolved: **yes**. The static metadata does not prove that IOKit successfully instantiates or attaches the service, that the provider exists at runtime, or that interrupts are handled correctly.

The metadata's \`sdk_build\` / \`platform_build\` value \`19H402\` is preserved as reported. It is not substituted for the restore/build identity \`19H422\`.

## Additional T8010 platform KEXT personalities

The user's output also contains these target-native platform bundle/personality records:

| Bundle | Personality | \`IONameMatch\` | \`IOProviderClass\` |
|---|---|---|---|
| \`AppleT8010\` | \`AppleT8010IO\` | \`arm-io,t8010\` | \`IOPlatformDevice\` |
| \`AppleT8010\` | \`AppleT8010MemCacheController\` | \`mcc,t8010\` | \`AppleARMIODevice\` |
| \`AppleT8010\` | \`AppleT8010PlatformErrorHandler\` | \`error-handler,t8010\` | \`AppleARMIODevice\` |
| \`AppleT8010PMGR\` | \`AppleT8010PMGR\` | \`pmgr1,t8010\` | \`AppleARMIODevice\` |
| \`AppleT8010PCIe\` | \`AppleT8010PCIe\` | \`apcie,t8010\` | \`AppleARMIODevice\` |
| \`AppleT8010SOCTuner\` | \`AppleT8010SOCTuner\` | \`soc-tuner,t8010\` | \`ApplePMGRNub\` |
| \`AppleT8010CLPC\` | \`AppleT8010CLPC\` | \`clpc,t8010\` | \`ApplePMGRNub\` |

The filtered output also identifies \`AppleT8010SmartIO\` and \`AppleT8010PMPFirmware\` as KEXT bundles. The provided excerpt does not preserve a complete personality row for each of those two records, so no provider or match property is inferred here.

Several of the listed T8010 KEXT \`os_bundle_libraries\` records name \`AppleARMPlatform\`; the PMGR, SOCTuner, and CLPC records also name \`ApplePMGR\`. These are serialized dependency declarations, not proof of runtime load order or service attachment.

The output ends with \`Matching records: 129\`. The filter included the broad term \`AppleARMPlatform\`, which matched many \`os_bundle_libraries\` dependency dictionaries. Therefore 129 is **not** a count of unique T8010 KEXT bundles or of 129 drivers.

## Cross-reference to existing target DeviceTree evidence

The repository's [parsed 19H422 DeviceTree audit](iphone91-19h422-parsed-devicetree-audit.md) records:

- \`/arm-io\`: compatible \`arm-io,t8010\`.
- \`/arm-io/aic\`: compatible \`aic,1\`, master interrupt controller.
- \`/arm-io/aic-timebase\`: a separate \`device_type = timer\` node.
- The AIC and AIC-timebase register tuples are separate properties/windows in the parsed artifact.

The new \`AppleInterruptController\` personality makes the \`aic,1\` metadata relationship explicit. It does not identify the IRQ namespace, trigger modes, priorities, CPU affinity, routing, acknowledge/EOI behavior, or how the timer node is serviced. The separate timer node must not be treated as proof that the AIC KEXT implements the required timebase/decrementer callbacks.

## Compatibility and source boundary

The target KEXT metadata comes from the iOS 15.8.8 / 19H422 iPhone 7 KernelCache, whose embedded kernel identity is XNU \`8020.241.44~1/RELEASE_ARM64_T8010\`. The selected iOS 16.7.16 / 20H392 userland reference comes from an iPhone X donor and its KernelCache reports \`RELEASE_ARM64_T8015\`.

The 19H422 KEXT record is valuable target-native evidence, but it does **not** establish that this proprietary KEXT binary is compatible with public XNU 8796, that its KPI/IOKit ABI is unchanged, or that it can be substituted into the donor's iOS 16-generation kernel. The reviewed public XNU 8796 source still supplies generic ARM64 AIC helpers and IOKit interfaces, not the private implementation of this KEXT.

The public XNU source review and unresolved timer/interrupt contracts are documented in the [AIC source-availability audit](aic-controller-source-availability-audit.md) and [ARM64 interrupt/timer interface audit](interrupt-timer-interface-audit.md).

## What remains unresolved

- Runtime creation/attachment of the \`AppleARMIODevice\` provider and the \`AppleInterruptController\` service.
- Exact target interrupt-specifier encoding, IRQ namespace, trigger types, priority rules, CPU routing, and IPI behavior.
- Acknowledge/EOI implementation and the relationship between the AIC node and the separate AIC-timebase node.
- A verified non-zero runtime \`timebase-frequency\`, counter source, and XNU callback requirements.
- Exact KPI/IOKit compatibility between the 19H422 private KEXT and the selected XNU 8796 baseline.
- Exact Apple source/build provenance for the shipped 19H422 and 20H392 KernelCaches.

## Next bounded research step

Compare the same selected AIC/T8010 KEXT bundle and personality metadata against the iPhone X / 20H392 donor KernelCache. Keep the two KernelCaches' bundle versions, personalities, and dependencies separate. A donor-side match or absence will inform the cross-release compatibility matrix, but still will not prove binary ABI compatibility or runtime behavior.

Do not infer controller constants or register programming from generic public headers. No target-specific driver or kernel implementation is authorized by this metadata result alone. The current readiness gates remain in force.

No device, firmware, partition, or boot state was accessed or changed.
