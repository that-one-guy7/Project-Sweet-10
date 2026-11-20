# Boot architecture research

This is a design checklist, not a boot procedure.

## Conceptual stages
1. Entry environment provides a controlled execution context.
2. A platform-specific handoff supplies XNU boot arguments, memory description,
   device tree, and CPU state.
3. Early kernel initializes CPU/platform, memory management, interrupts, timer, and console.
4. Kernel services and IOKit matching become available.
5. Root filesystem is discovered and mounted.
6. launchd and required userland services start.
7. backboardd, SpringBoard, and supporting services become stable.

## A10 questions to answer with evidence
- Which boot-argument ABI does the selected XNU revision require?
- Which Apple Device Tree nodes/properties are consumed?
- What CPU exception level and register state are expected at entry?
- Which memory regions are reserved by firmware and security components?
- Which interrupt controller and timer interfaces are used?
- Which display and HID services are needed for a first visible UI?

Do not copy hardware values from ios-sweet: its target is Qualcomm SM7150.
