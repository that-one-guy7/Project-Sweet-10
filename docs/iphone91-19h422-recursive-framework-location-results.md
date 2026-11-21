# iPhone9,1 19H422 recursive GUI framework location results

## Summary

The user-run recursive scan completed successfully over the supplied mounted target OS tree:

- Target: iPhone9,1 / D10AP / iOS 15.8.8 / 19H422.
- Root: `$HOME/19H422-full-fs-mount/root`.
- Directories scanned: **104,017**.
- Entries visited: **382,833**.
- Walk errors: **0**.
- Matching-entry stat errors: **0**.
- Candidate names checked: **18**.

The scan therefore completed without reported traversal or permission failures **within this one supplied tree**.

## Correct interpretation of the ExtensionFoundation result

The original scanner reported two candidates as `match-found`, but the sole matched filesystem entry was:

```
System/Library/PrivateFrameworks/ExtensionFoundation.framework
```

Its entry type was `directory`, and the match kind was `framework-bundle-name`. The file named `ExtensionFoundation` was **not** found. Both candidate IDs (the donor Frameworks path and target PrivateFrameworks alternate) were associated with that same one directory match.

Therefore the reviewed classification is **bundle-directory-only**, not “binary found”. The match does not prove that the donor's `/System/Library/Frameworks` install path exists, nor that the executable exists in the bundle.

## Candidate results

| Candidate group | Count | Result |
|---|---:|---|
| ExtensionFoundation install-path variants | 2 | One shared bundle directory found; executable not found |
| Other selected GUI dependencies | 16 | No matching binary or framework-directory basename in the scanned tree |
| **Total** | **18** | **One matching directory entry** |

The 16 no-match candidates are PrivacyDisclosureCore, SystemAperture, ActivityKit, ActivityUIServices, PosterBoardUI, BacklightServices, BacklightServicesHost, PosterBoardServices, PosterKit, CoverSheetKit, SessionAssertion, BiomeLibrary, PointerUISystemServices, PaperBoardUI, SystemStatusUI and SystemApertureUI.

## Relationship to dyld cache evidence

The target 19H422 dyld inventory separately contains an ExtensionFoundation cache image-list record at index 1093, with the PrivateFrameworks install name. That is distinct from the filesystem result above. A cache image record and a standalone executable file are different evidence categories.

For the other 16 candidates, this scan confirms no matching bundle or executable names in the selected OS filesystem tree. It does not by itself prove absence from every possible volume or cache. The next comparison should preserve three independent fields: standalone filesystem name/path presence, target dyld cache image-list membership, and PrebuiltLoader dependency metadata.

## Evidence limits

This recursive search used the supplied target OS root only. It did not search another mounted image, Cryptex, APFS snapshot, or the internals of the dyld shared-cache file. It did not open, hash, parse or execute any framework binary.

A filename match is not Mach-O validation, code-signature validation, dyld resolution, ABI compatibility, service startup, hardware operation, kernel boot or SpringBoard readiness.

The complete reviewed machine-readable summary is preserved at
[`research/iphone91-19h422-gui-framework-location-inventory-results.json`](../research/iphone91-19h422-gui-framework-location-inventory-results.json).

M6 remains in progress; M7/SpringBoard has not started. The physical iPhone 7 remains on iOS 12.1.4.
