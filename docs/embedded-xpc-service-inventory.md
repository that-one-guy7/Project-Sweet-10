# Embedded XPC-service and app-extension inventory

## Purpose and status

This is the next bounded M6 metadata task after the target/donor comparison of
\`System/Library/xpc/launchd.plist\`. A LaunchDaemon entry describes a configured
job; an embedded \`.xpc\` or \`.appex\` bundle may carry additional service or
extension metadata outside that central plist. This inventory is intended to
record those bundle declarations without assuming that a service starts or is
used by SpringBoard.

The tool is \`tools/inspect_embedded_services.py\`. It uses Python's standard
library and reads only \`Info.plist\` or \`Contents/Info.plist\` within bundle
directories. By default it discovers directory names ending in \`.xpc\` or
\`.appex\`, including nested bundles beneath \`.app\` directories. It does not
inventory \`.app\` bundles themselves unless explicitly requested with
\`--suffix .app\`.

The first target/donor collection and path-level comparison are now recorded
in [the inventory results](embedded-xpc-service-results.md). The uploaded reports
contain 719 target candidates and 855 donor candidates, with four missing
Info.plists in each and no scan errors. The comparison preserves each bundle
path because many bundle identifiers occur in both installed-app and
AppPlaceholders locations. M6 remains in progress; the results are static
metadata and do not establish runtime service registration or SpringBoard.

## Input roots

The target reference is iPhone 7 \`iPhone9,1\` / D10AP / A10-T8010, iOS 15.8.8
build \`19H422\`. The donor reference is iPhone X \`iPhone10,3\` / D22AP /
A11-T8015, iOS 16.7.16 build \`20H392\`. The physical iPhone 7 remains on
iOS 12.1.4; neither reference image is installed on it.

The donor's OS root and SystemOS Cryptex are mounted separately. Pass both
filesystem roots as separate arguments so that bundle paths retain their
source-volume label in the output. For the target, pass the extracted or
mounted 19H422 root used by the existing launchd inventory. Do not combine
filesystem contents manually or classify a bundle absent from one volume as
absent from the complete system.

## Collection

From the repository root, set the path variables to the roots that are already
mounted and readable on the Ubuntu host:

\`\`\`sh
OUT="$HOME/sweet10-embedded-services"
mkdir -p "$OUT"

TARGET_ROOT="/path/to/19H422/target-root"
DONOR_OS_ROOT="/path/to/20H392/os-root"
DONOR_SYSTEMOS_ROOT="/path/to/20H392/systemos-root"

python3 tools/inspect_embedded_services.py "$TARGET_ROOT" \\
  > "$OUT/19H422-embedded-services.json"

python3 tools/inspect_embedded_services.py \\
  "$DONOR_OS_ROOT" "$DONOR_SYSTEMOS_ROOT" \\
  > "$OUT/20H392-embedded-services.json"
\`\`\`

The paths above are placeholders: use the mount roots that already exist on
the host. The tool does not mount, unmount, remount, change permissions, or
alter any source filesystem. It emits one JSON document to standard output;
redirect each build's report to a separate file.

To include other directory bundle types in a separate survey, repeat
\`--suffix\`, for example \`--suffix .xpc --suffix .appex --suffix .plugin\`.
Do not include \`.app\` in the initial comparison unless there is a specific
reason to inventory app roots as well as embedded XPC and extension bundles.

## Recorded fields

For each candidate bundle, the report records:

- source-root label and bundle-relative path;
- bundle suffix and Info.plist relative path;
- Info.plist SHA-256 and parse status;
- \`CFBundleIdentifier\`, \`CFBundleExecutable\`, package type, minimum OS
  version, and supported platforms when present;
- whether the declared executable filename is present as a regular file,
  symlink, another file type, or not found (a metadata/stat check only);
- declared \`MachServices\` names found at the top level or in \`XPCService\`;
- selected XPC service fields and \`NSExtension\` point/principal-class fields;
- a provider index for MachService names declared in the scanned bundles.

The report intentionally does not emit arbitrary Info.plist keys or values,
full executable paths outside the bundle, binary contents, environment values,
arguments, entitlements, or code-signing data. A malformed, missing, unreadable,
or symlinked Info.plist remains an explicit status instead of being silently
classified as a bundle with no metadata. Scan errors are listed separately;
check \`scan_errors\` before comparing inventories.

## Interpretation rules

1. A bundle declaration is static metadata. It does not prove an XPC service
   launches, registers its MachService, has clients, or remains available.
2. A declared \`CFBundleExecutable\` filename check does not validate a Mach-O,
   signature, entitlement, dyld closure, ABI, or loadability.
3. A service name repeated across bundles is recorded with each source-root
   and bundle path. It is not treated as an error or successful registration.
4. A missing bundle in the scanned roots is not proof of absence from every
   volume, Cryptex, shared cache, or runtime-loaded image.
5. The 19H422 target reference is one major iOS release older than the 20H392
   donor. Differences may be release-related as well as product-related; do
   not attribute them to the A10/A11 difference alone.
6. LaunchDaemon MachServices, bundle-declared services, executable presence,
   dyld loader records, IOKit personalities, and runtime process state are
   separate evidence classes and must not be conflated.

This tool and its tests are host-side static metadata work only. It does not
read or modify the physical device, firmware, partitions, security state, or
boot state. M6 remains in progress; M7/SpringBoard has not started.
