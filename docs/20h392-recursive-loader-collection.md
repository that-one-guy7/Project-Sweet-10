# 20H392 recursive dyld loader-record collection

## Purpose and scope

The M6 audit now has the user-supplied PrebuiltLoader records for backboardd,
runningboardd, and the SpringBoard executable. The next unresolved layer is
the framework dependency graph beneath those processes.

This note describes a repeatable host-only, read-only collection pass for the
iPhone X iOS 16.7.16 (20H392) donor SystemOS cache. The physical project
target remains iPhone 7, iPhone9,1 / D10AP / A10-T8010. Nothing collected from
the donor becomes target evidence without an independent iPhone9,1 match.

Apple's dyld4 design describes PrebuiltLoaders as read-only records containing
dependent dylibs and precomputed bind targets; a loader's dependent records
are recursively loaded to form a dependency graph. The ipsw dyld guide documents
the command form ipsw dyld image <cache> <image> for inspecting a selected
image. See the Apple dyld4 design at
https://github.com/apple-oss-distributions/dyld/blob/main/doc/dyld4.md,
the Apple PrebuiltLoaderSet policy at
https://github.com/apple-oss-distributions/dyld/blob/main/doc/PrebuiltLoaderSet_Policy.md,
and the ipsw dyld guide at https://blacktop.github.io/ipsw/docs/guides/dyld/.

## Priority images

The collector's default list follows the actual donor backboardd and
SpringBoard records already reviewed in 20h392-prebuilt-loader-audit.md.

| Priority group | Images | Why inspect them |
|---|---|---|
| HID/display path | BackBoardHIDEventFoundation, BackBoardHIDEventProcessors, BackBoardServices, IOMobileFramebuffer, IOKit, IOSurface | These are the most direct framework edges associated with event delivery, framebuffer access, and display surfaces |
| Graphics path | QuartzCore, CoreGraphics, Metal | These are direct display/graphics dependencies in the donor backboardd record |
| Process/UI coordination | RunningBoard, RunningBoardServices, SpringBoard.framework, BoardServices, BaseBoard | These connect process lifecycle, frontboard/backboard services, and the SpringBoard framework |
| Core runtime | Foundation, CoreFoundation | These form common runtime dependencies for the selected GUI services |

This is a prioritization for inspection, not an assertion that all entries are
equally required on iPhone9,1 or that the table is a complete launch closure.

## Host-side command

The user already has the separate SystemOS cache mounted at:

    $HOME/20H392/systemos-mnt/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64

From the local Project Sweet-10 checkout, run:

    CACHE="$HOME/20H392/systemos-mnt/root/System/Library/Caches/com.apple.dyld/dyld_shared_cache_arm64"
    python3 tools/capture_dyld_loader_records.py \
      --cache "$CACHE" \
      --output-dir "$HOME/20H392/loader-records"

The default run asks the local ipsw executable to inspect each priority
framework and stores each raw output as a separate text file, together with
stderr files and capture-manifest.json. A failed lookup is recorded with its
exit status; it is not silently classified as a missing library. The collector
refuses to overwrite matching outputs unless --overwrite is supplied.

To inspect only one or two selected images, pass --image once per absolute
install path. Supplying --image replaces the default list.

The collector reads the cache; it writes only to the selected output directory.
It does not execute any iOS executable, change the cache or Cryptex, connect to
a phone, or issue device commands. Do not upload the entire mounted image or
the raw cache to the repository.

## How to interpret the output

For each successfully captured image, record:

- its full install path;
- the ordered Dependents list, preserving regular and weak-link entries separately;
- any BindTargets and the exact loader paths they reference;
- whether the image is listed in the selected donor cache or is supplied from
  another donor volume/app bundle;
- parser warnings or malformed-looking fields, kept separate from trusted data.

Build edges from a parent image to each dependent image. Deduplicate nodes by
full install path, but preserve each parent's edge and the order reported by
the tool. A repeated library is one node with multiple incoming edges, not a
reason to discard a parent relationship.

Use these classifications:

- cache-listed: path appears in the selected SystemOS shared-cache image list;
- rootfs-file: path resolves in the separately mounted donor OS root filesystem;
- app-bundle: path resolves inside a donor application bundle;
- weak-link: loader explicitly identifies a weak dependency;
- unresolved: no reliable location or install-name resolution is established;
- parser-unverified: output fields are suspect and require another parser.

Do not call a path missing merely because it is absent from the root filesystem
mount: the OS root and SystemOS Cryptex are separate. Do not equate a cache image
list entry with a successfully validated executable mapping or a running
service. Do not infer IOKit client/provider relationships from dylib
dependencies; those require separate personality and service-registration
evidence.

The unusual Swift/Objective-C section offsets already observed in the three
executable records remain excluded. This collector stores raw output and does
not attempt to parse or repair those fields.

## Synthetic validation

Run:

    python3 -m unittest discover -s tests -p 'test_capture_dyld_loader_records.py' -v

or the complete project suite:

    python3 -m unittest discover -s tests -p 'test_*.py' -v

The tests use a synthetic cache placeholder and mocked ipsw subprocess results.
They verify output capture, failure recording, hashes, path validation, and
overwrite protection. They do not validate a real dyld cache or the ipsw parser.

## Exit criteria for this subtask

This collection task is complete only after the actual command output is
reviewed and the dependency edges are transcribed with unresolved items left
explicit. It does not complete M6 by itself. Remaining work includes embedded
XPC services, IOKit personality/provider matching, target-side comparison, and
service compatibility classification.

M6 remains in progress. M7 (SpringBoard on iPhone9,1) remains not started.
The user's iPhone 7 remains on iOS 12.1.4; this workflow makes no device changes.
