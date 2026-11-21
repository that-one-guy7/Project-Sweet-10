# M1 hardware/source audit completion

## Milestone decision

**M1 — Hardware/source audit is complete within its stated exit criterion: an evidence-backed iPhone9,1 inventory.**

This is a documentation and static-evidence milestone. It is not a claim that iOS 16 boots on iPhone 7, that a T8010 kernel can be built from the selected XNU 8796 baseline, or that any proprietary driver is ABI-compatible with that baseline.

## Evidence assembled

| Area | Evidence now recorded | Boundary |
|---|---|---|
| Target identity and firmware reference | iPhone9,1 / D10AP / T8010; hash-verified iOS 15.8.8 (19H422) DeviceTree parsed as 227 nodes | Static stock reference, not the phone's live runtime tree |
| Target kernel inventory | 19H422 KernelCache identified as XNU 8020.241.44~1 / RELEASE_ARM64_T8010; 230 KEXT entries inventoried | Presence and metadata do not establish loading or function |
| Platform-management metadata | AppleT8010PMGR personality matches `pmgr1,t8010` on AppleARMIODevice; PMGR, SOCTuner, and CLPC dependency records name ApplePMGR | The concrete PMGR executable has not been inspected; no CPU-start implementation is proven |
| Interrupt/timer and DeviceTree mapping | Target AIC, timer, ARM-IO, CPU, and selected register-property evidence is cross-referenced with generic XNU consumers | Runtime clock values, IRQ routing, timer operation, and final boot-time properties remain open |
| Display and input inventory | Target-native display, MIPI-DSI, LCD, SPI, K1 HID transport, and backlight personalities have exact static compatible-string overlaps; multitouch plugin UUID linkage is documented | IOKit attachment, plugin loading, touch events, and panel operation are untested |
| PongoOS source inventory | Pinned PongoOS source has a registered T8010 HAL backend and T8010-specific source paths | No PongoOS session or hardware behavior has been tested |
| XNU generation history | XNU 7195 includes H9/T8010 board support; reviewed 8019/8796 public snapshots omit T8010 from the normal ARM64 machine allowlist | No exact 20H392 Apple source/build provenance or reproducible T8010 XNU 8796 build |
| CPU topology and handoff | XNU 8796 retains a legacy topology path relevant to pre-HAS_CLUSTER generations; generic IOPMGR retains the legacy core-enable fallback | The concrete T8010 PMGR implementation, firmware reset-vector state, and secondary-core startup remain unknown |

## Why M1 can close while other questions remain open

M1's exit criterion is an evidence-backed hardware/source inventory. The inventory now identifies the target board/SoC, static DeviceTree structure, target-native KernelCache/KEXT records, selected hardware match properties, PongoOS source support, and the relevant XNU source-generation boundary.

The absence of a T8010 machine profile from reviewed XNU 8796 is a major compatibility issue, but it belongs to **M2 — XNU baseline and reproducible build**. Likewise, concrete PMGR behavior and final runtime boot arguments are not required to claim that the inventory itself is assembled; they remain explicit unresolved gates and must not be silently treated as complete.

## Explicitly not claimed

- No iOS 16.7.16 / 20H392 boot on iPhone9,1.
- No T8010 XNU 8796 build or kernel binary.
- No private ApplePMGR/AppleT8010PMGR executable analysis.
- No proof that a donor iPhone10,3 KernelCache or userland is compatible with iPhone9,1.
- No runtime CPU bring-up, interrupt/timer operation, graphics, display, or touch operation.
- No SpringBoard milestone.
- No changes to the user's iPhone; it remains on iOS 12.1.4.

## Next milestone

Proceed to **M2 — XNU baseline** with the T8010 profile gap, exact donor source provenance, product build inputs, and reproducible host-build requirements as the central gates. The highest-value missing artifact for the CPU handoff sub-question is the extracted `AppleT8010PMGR` KEXT executable from the 19H422 target KernelCache (or the complete target KernelCache if the executable cannot be separately extracted). Static plist metadata alone cannot answer the concrete PMGR implementation question.
