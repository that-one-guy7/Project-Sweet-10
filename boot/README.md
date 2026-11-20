# Boot interface research

No loader, payload, boot command, or device-writing script is included.

Start with:
- [Conceptual boot architecture](../docs/boot-architecture.md)
- [XNU handoff requirements checklist](HANDOFF_REQUIREMENTS.md)
- [Project Sandcastle loader source review](../docs/sandcastle-loader-review.md)

Sandcastle's public loader is described as loading a Linux kernel and device tree via
PongoOS. It is a reference for the separation between host transport, boot environment,
kernel image, and device-tree input. It is not an XNU loader and its protocol is not
an XNU boot contract.

All XNU entry requirements and iPhone9,1 hardware values remain evidence gaps. This
directory intentionally contains no operational boot procedure or target-specific
payload.
