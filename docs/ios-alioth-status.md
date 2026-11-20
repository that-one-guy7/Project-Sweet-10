# ios-alioth: status and source-boundary review

## Scope

This note reviews the public [furretmaster290/ios-alioth](https://github.com/furretmaster290/ios-alioth) repository README. The repository identifies itself as a work in progress and as a fork of JopangJovan/ios-sm8250. This is a documentation review only.

## What the README currently says

The README describes an iOS 16 / XNU 8796 project targeting the POCO F3 (`alioth`, Qualcomm SM8250). It says the broader source lineage also covers the Redmi Note 10 Pro (`sweet`, SM7150) and Xiaomi Mi 10 (`umi`, SM8250).

Its current status statement says the alioth target reaches the iOS 16 lock screen and identifies touch as the next missing milestone. The README separately describes the sweet board as reaching the iOS home screen with touch, buttons, and display support. It explicitly warns that the detailed tested results apply to sweet, while umi is an unverified bring-up port.

The README reports iPhone X iOS 16.7.16 (20H392) userland for the project family. These are upstream-reported states and have not been independently reproduced by Project Sweet-10.

## Why this reference matters

The repository demonstrates that a shared XNU/userland lineage can require distinct board configurations and that a port's status must be reported per board. It is a useful example of separating common kernel work from board-specific device-tree, shim, and peripheral work.

It also shows why README summaries must be read carefully: results for one board must not be attributed to another board merely because they share a repository or codebase.

## Portability boundary

The POCO F3 and related Xiaomi targets use Qualcomm SoCs and associated platform components. Their CPU topology, memory layout, interrupt/timer configuration, PMIC, storage controller, display, touch, and device-tree values are not evidence for Apple's A10/T8010 platform. Project Sweet-10 must not import those values or treat the Qualcomm machine configuration as a template that can be renamed to iPhone9,1.

## Project decision

Use ios-alioth as:
- a per-board status-reporting example;
- a reference for separating common XNU work from board-specific changes;
- a checklist source for the categories that require independent A10 evidence.

Do not treat it as an A10 driver source, a verified iPhone9,1 boot design, or proof that the selected iPhone X userland works on iPhone 7.

## Next evidence gate

Before platform implementation, Project Sweet-10 still needs revision-matched XNU/kernel metadata and authoritative iPhone9,1 evidence for boot handoff, device tree, memory map, CPU lifecycle, interrupt/timer interfaces, storage, display, HID, and power.

No device interaction, firmware modification, boot attempt, or partition write was performed for this review.
