# Tests

These host-side checks validate project metadata, the pinned XNU and PongoOS source
locks, the historical T8010 source-profile transition, the read-only
source-verification workflow, and the exact iPhone9,1 / D10AP 19H422 BuildManifest
and IM4P artifact checks. They do not compile XNU, test a kernel, or interact with
a device.

Run the checks locally:

    python3 tools/check_project.py
    python3 -m unittest discover -s tests -p 'test_*.py' -v

The 19H422 artifact verifier uses only Python's standard library. It validates
published SHA-256 values, the D10AP BuildIdentity entries, the IM4P envelope,
and the SHA-384 value recorded by the manifest. The Apple DeviceTree inspector
uses only Python's standard library, bounds-checks the flattened property stream,
requires complete input consumption, and emits only allowlisted non-identifying
fields. Synthetic tests cover valid trees, malformed bounds, duplicate properties,
trailing bytes, and privacy filtering.

The XNU machine-history audit checks three pinned public source snapshots:
xnu-7195.121.3 contains the T8010/H9 machine profile, while xnu-8019.80.24 and
xnu-8796.141.3 omit it at the reviewed paths. Its synthetic tests exercise
missing and unexpectedly reintroduced profile elements. This is source-structure
validation, not an XNU build or device-compatibility test.

The GitHub Actions workflow reads the expected XNU and PongoOS commits from
xnu/BASELINE.lock.json, xnu/history/*.lock.json, and pongo/BASELINE.lock.json,
checks out those exact revisions, and verifies their local Git HEAD values.
Repository permissions are read-only.

The launchd inventory tool reads only the central
`System/Library/xpc/launchd.plist` below an extracted root. It emits job
labels, executable paths, MachServices provider names, selected KeepAlive and
scheduling metadata, and environment-variable names (not values). It does not
execute jobs or modify the root. Synthetic tests use generated plist fixtures;
they do not validate the actual 20H392 donor image.


The expanded `test_xnu_public_source_matrix.py` validates the pinned
six-snapshot public XNU matrix: historical T8010/H9 presence in
`xnu-7195.121.3`, absence in target-era public `xnu-8020.101.4`,
intermediate `xnu-8019.80.24`, early and selected `xnu-8796` snapshots,
and later `xnu-12377.1.9`. This is a synthetic, host-only source-structure
test; it does not compile XNU or establish device support.

The selected KEXT metadata comparator reads the 19H422 target and 20H392
donor `ipsw kernel kext` JSON exports. It compares exact top-level bundle
IDs, selected IOKit personality fields, and `os_bundle_libraries`
declarations. Synthetic tests verify exact-ID filtering, field comparisons,
duplicate rejection, malformed input handling, and that dependency mentions
are not misclassified as top-level bundles. It is a JSON metadata comparison,
not a KEXT loader, ABI validator, or device test.


The dyld export-log comparator reads only saved text output from
`ipsw dyld macho --symbols -V`. Synthetic tests cover export-section
parsing, missing/empty sections, target-only and donor-only names, printed
kind-category changes, resolver-address differences (without misclassifying them as kind changes), duplicate symbol rows, and cache-local address differences.
It does not read cache binaries, extract images, or establish ABI/runtime
compatibility.


The embedded XPC-service/app-extension inventory reads only Info.plist or
Contents/Info.plist inside .xpc and .appex bundles (or other explicitly
selected suffixes). It emits allowlisted bundle/service/extension fields and
plist hashes, skips symlinked bundle and plist entries, and never reads or
executes bundle binaries. Synthetic tests cover bundle discovery, multiple
roots, service/provider indexing, extension metadata, malformed/missing
plists, unsafe executable names, symlinks, and source-file preservation. This
is static bundle metadata, not evidence of runtime service registration.


The first supplied 19H422 target and 20H392 donor inventory run is summarized
in `docs/embedded-xpc-service-results.md`. These are actual sanitized plist
reports, separate from the synthetic fixtures used by the unit tests.


The embedded-service comparison tool reads the sanitized JSON outputs from
the .xpc/.appex inventory collector. It groups records by exact bundle
identifier, preserves duplicate occurrence counts and source-root paths,
compares selected metadata-value sets, and can write one CSV row per unique
identifier. It does not inspect or execute bundle binaries. Ten synthetic
tests cover target-only/donor-only/common identities, duplicate identifiers,
metadata differences, missing identifiers, CSV output, schema validation,
and MachServices declaration accounting. Results remain static metadata,
not runtime service availability or ABI evidence.


The embedded-service / launchd cross-check reads sanitized .xpc/.appex
inventory JSON and the matching central LaunchDaemons inventory JSON. It
joins bundle-declared MachServices strings to launchd provider-index names,
preserves repeated bundle occurrences, and reports provider labels when an
exact string is present. It does not infer clients, registration, or runtime
availability. Nine synthetic tests cover matches, unmatched names, duplicate
records, unparsed bundles, empty declaration sets, schema validation, and
malformed service-index entries.
