# Read-only BuildManifest inspector

## Purpose

`tools/inspect_buildmanifest.py` reads the root `BuildManifest.plist` from a
local IPSW ZIP archive and emits a JSON metadata report. It does not extract
archive members, execute archive contents, alter the IPSW, or choose a
BuildIdentity automatically.

The tool is intended to populate the evidence record in
[the BuildManifest checklist](buildmanifest-evidence-checklist.md). It is a
host-side metadata aid, not a firmware installer, boot tool, or compatibility
test.

## Requirements

- Python 3.10 or newer
- A local IPSW archive that contains `BuildManifest.plist` at its root

Only Python standard-library modules are used.

## Usage

From the repository root:

```sh
python3 tools/inspect_buildmanifest.py /path/to/candidate.ipsw
```

To also calculate a SHA-256 digest of the complete IPSW archive:

```sh
python3 tools/inspect_buildmanifest.py /path/to/candidate.ipsw --sha256
```

The report is written to standard output as JSON. Save it locally if desired:

```sh
python3 tools/inspect_buildmanifest.py /path/to/candidate.ipsw --sha256 > candidate-buildmanifest-report.json
```

The optional hash pass reads the full archive sequentially. It can take time
for large IPSWs; omit `--sha256` when only manifest metadata is needed.

## What the report contains

- Archive filename and byte size; archive SHA-256 only when requested
- `ProductVersion` and `ProductBuildVersion`
- Every `BuildIdentities` entry with its original zero-based index
- Identity information, including device class, supported product types,
  board ID, and chip ID when present
- KernelCache and DeviceTree paths and available digest/size metadata
- The complete component metadata dictionary, with binary plist values
  represented as hexadecimal strings

The inspector deliberately reports every identity. Do not assume the first
entry is the correct one. Review the device class, product types, board/chip
identifiers, and component metadata together, then record the evidence and
provenance in the project checklist. Missing fields remain missing; the tool
does not infer values from another device.

## Tests

Run the standard-library unit tests:

```sh
python3 -m unittest discover -s tests -v
```

The tests use synthetic plist fixtures in temporary ZIP files; they do not
require a real IPSW or a connected device.

## Interpretation limits

A 20H392 build-number match does not make a donor KernelCache suitable for
iPhone9,1. This report does not establish an Apple source-to-kernelcache
mapping, iPhone9,1/T8010 support, or boot compatibility. No checkm8, PongoOS,
restore, device connection, or firmware modification is part of this workflow.
