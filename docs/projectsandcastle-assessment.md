# Project Sandcastle: what it contributes to Project Sweet-10

## What the upstream project says

The Corellium `projectsandcastle` README describes Android/Linux for iPhone. It lists
utilities including a loader that loads a kernel and device tree via PongoOS, plus
configuration and peripheral tools. It points to a Linux kernel fork and a Buildroot
customization tree.

The public `loader/load-linux.c` source is a host-side libusb program. Its documented
purpose and implementation are specific to transferring a Linux kernel and device tree
through the Sandcastle/PongoOS interface.

## Useful research concepts

- A separate host-side loader and target-side boot environment.
- Explicit kernel and device-tree artifacts.
- A clear boundary between the boot environment and the operating-system kernel.
- Reproducible host tooling and source review.
- A place to study how Apple-device boot research has been organized.

## What must not be assumed

- Sandcastle's loader is not an XNU loader.
- Its Linux boot protocol is not an XNU boot-argument ABI.
- A Linux device tree is not automatically an Apple Device Tree suitable for XNU.
- Linux driver support does not imply matching IOKit/XNU driver support.
- The existence of a PongoOS-based workflow does not prove that a particular iPhone7
  boot environment, security state, or XNU handoff is supported.

## Project Sweet-10 integration boundary

For this repository, Sandcastle is a **reference for boot-environment architecture only**.
Keep any future PongoOS investigation separate from XNU platform code. First document
the target's existing boot environment and public interfaces; then specify, on paper,
what an XNU handoff would need to provide. Do not adapt or execute the Sandcastle Linux
loader against a device as a substitute for that analysis.

## References

- [Project Sandcastle README](https://github.com/corellium/projectsandcastle)
- [Sandcastle loader source](https://github.com/corellium/projectsandcastle/blob/master/loader/load-linux.c)
- [Sandcastle Linux kernel fork](https://github.com/corellium/linux-sandcastle)
- [Sandcastle Buildroot fork](https://github.com/corellium/sandcastle-buildroot)
