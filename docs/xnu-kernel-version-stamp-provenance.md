# Interpreting the 20H392 XNU version-stamp string

## Purpose

This note clarifies what can and cannot be inferred from the donor KernelCache's
embedded string:

`xnu-8796.142.1.703.8~1/RELEASE_ARM64_T8015`

The distinction matters because the project previously compared that string
directly with the public Git tag `xnu-8796.141.3`. They are visibly different
labels, but the embedded string is not necessarily a Git tag.

This is read-only analysis of public source and existing host-side artifact
metadata. It does not change a kernel, firmware, partition, boot state, or
device state.

## What public XNU source shows

In Apple's public `xnu-8796.141.3` tree:

- `config/version.c` contains the generated kernel version string template.
  The template includes `KERNEL_VERSION_LONG`, the build date, builder, and
  `KERNEL_BUILD_OBJROOT`.
- `config/newvers.pl` generates the version text. It reads
  `config/MasterVersion`, and its comments document the output fields.
- `config/MasterVersion` starts with `22.6.0`; this feeds the Darwin kernel
  version portion such as `Darwin Kernel Version 22.6.0`. It is not the
  same field as the `xnu-...` build-object-root label.
- When `RC_XBS` is defined, `newvers.pl` constructs
  `RC_STRING` from `RC_ProjectNameAndSourceVersion` plus
  `~` plus `RC_ProjectBuildVersion`.
- In the branch where the build object path is under `OBJROOT`, that
  `RC_STRING` is used as the leading build-object-root label.

Official source references:
- [XNU 8796.141.3 config/version.c](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/version.c)
- [XNU 8796.141.3 config/newvers.pl](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/newvers.pl)
- [XNU 8796.141.3 config/MasterVersion](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/config/MasterVersion)
- [XNU 8796.141.3 version header template](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/libkern/libkern/version.h.template)

## Bounded interpretation of the donor string

The donor KernelCache was previously inspected as reporting:

- Darwin version: `22.6.0`
- Embedded build-object-root label: `xnu-8796.142.1.703.8~1`
- Kernel build configuration: `RELEASE_ARM64_T8015`

The public version-stamping logic shows that an embedded label of this shape
can be an XBS project/source-version label with a build number appended. If
the donor was stamped through that `RC_XBS` branch, the string is consistent
with `RC_ProjectNameAndSourceVersion=xnu-8796.142.1.703.8` and
`RC_ProjectBuildVersion=1`.

That is a conditional interpretation, not a recovered Apple build record.
The kernel string alone does **not** reveal the exact source commit, prove the
source tree was a public Git tag, identify all product-specific build inputs,
or show which files differed from the public source drop.

The GitHub tag-ref query for the public Apple XNU repository prefix
`xnu-8796` returned `xnu-8796.101.5`, `xnu-8796.121.2`, and
`xnu-8796.141.3`; it did not return a public `xnu-8796.142.*` tag.
This is a statement about the repository's returned tag refs, not proof that
no private source revision or separate Apple build record exists.

## What remains unknown

The following are still needed to close source provenance:

1. An authoritative Apple build record linking the 20H392 donor KernelCache
   to a precise XNU source revision.
2. The matching source export or commit and its product-specific build
   configuration, including the inputs that select T8015.
3. A file-level comparison between that source export and the public
   `xnu-8796.141.3` snapshot.

Until then, `xnu-8796.141.3` remains a useful public research baseline, not a
proven byte-for-byte or source-for-source reproduction of the donor kernel.
The donor's T8015 build identity does not establish T8010 support.

## Project impact

This refines G1 (source identity) but does not close it. It does not change
the M2 status: exact source provenance, product-specific build inputs, and a
reproducible unmodified baseline build remain open.

Do not infer target compatibility from the build-string suffix, and do not
copy or re-enable a machine profile based on the string alone. The first
SpringBoard milestone remains unachieved; no successful iPhone9,1 iOS 16 boot
is claimed. The physical iPhone 7 remains on iOS 12.1.4.
