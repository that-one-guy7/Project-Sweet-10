# Historical XNU T8010 machine-profile verification

## Purpose

This record turns the documented T8010/H9 source transition into a repeatable,
read-only CI check. It compares three public Apple XNU snapshots and verifies
the source structures that distinguish the historical A10-era profile from
the later machine lists. It does not create or enable a T8010 configuration.

## Pinned public source snapshots

| Role | XNU tag | Commit SHA | Tag object SHA | Recorded signature state |
|---|---|---|---|---|
| Historical T8010 reference | `xnu-7195.121.3` | `2a647cb3489890a0948eb7ee3a118307d39bb574` | `f3fc7232a1920ad0937107ef105912edf37d0d8d` | Unsigned |
| Intermediate transition reference | `xnu-8019.80.24` | `a325d9c4a84054e40bbe985afedcb50ab80993ea` | `7f6c2829cea348b0ed561ef71afdda2c73ff7604` | Unsigned |
| Selected iOS 16-era candidate | `xnu-8796.141.3` | `1b191cb58250d0705d8a51287127505aa4bc0789` | `f625db25f47631424dc62ac1c3414b6e530f7e8a` | Unsigned |

The annotated tag object and peeled commit are pinned separately. The GitHub
tag metadata reports all three tags as unsigned; the locks do not claim a
cryptographic signature. The two historical comparison locks live under
`xnu/history/`; the selected source candidate remains in
`xnu/BASELINE.lock.json`.

## Expected source transition

The audit checks three aligned parts of the historical implementation:

1. In `xnu-7195.121.3`, the normal ARM64 machine allowlist includes `T8010`
   and `MakeInc.def` supplies `MACHINE_FLAGS_ARM64_T8010` with
   `-DARM64_BOARD_CONFIG_T8010 -mcpu=hurricane`.
2. Its ARM64 `board_config.h` defines the `ARM64_BOARD_CONFIG_T8010` block,
   includes `H9.h`, and the historical `H9.h` declares `APPLEHURRICANE`.
3. In both `xnu-8019.80.24` and `xnu-8796.141.3`, the normal ARM64 allowlist
   omits `T8010`; the T8010 machine flag, board block, and H9 header are absent
   at the audited paths.

All three versions retain the `MakeInc.kernel` check that rejects a machine
configuration not present in the corresponding supported-machine list. This
shows why reintroducing only a machine name or bypassing the validation would
not recreate the removed CPU/board implementation.

## CI behavior

The read-only workflow checks out each XNU revision by its pinned full commit
SHA, verifies each checkout against its lock, and runs
`tools/audit_xnu_machine_history.py`. The audit checks the allowlist,
compiler/board flag, board configuration block, H9 header, and the machine
selection guard. Synthetic tests also check that the validator rejects
missing or unexpectedly reintroduced T8010 elements.

Run the structural test suite locally:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The script itself accepts the three already-checked-out source directories:

```sh
python3 tools/audit_xnu_machine_history.py \
  xnu/historical-7195 xnu/transition-8019 xnu/upstream
```

## Interpretation and limits

This CI check verifies public source identity and a small set of structural
facts at pinned paths. It does not explain Apple's engineering rationale for
the transition, prove that no alternate/private/downstream implementation
exists, establish a complete historical H9 dependency graph, compile XNU,
inspect an SDK's private or local `device_map.db`, or establish that a
particular 20H392 KernelCache maps to the pinned tag.

It also does not establish iPhone9,1 runtime compatibility. Target-specific
CPU, memory, clock, interrupt, peripheral, DeviceTree, security, and boot
handoff requirements remain separate readiness gates. The result must not be
interpreted as approval to copy H9 wholesale or to select T8010 in XNU 8796.

## Source references

- [XNU 7195.121.3 MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/makedefs/MakeInc.def)
- [XNU 7195.121.3 ARM64 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/board_config.h)
- [XNU 7195.121.3 H9.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-7195.121.3/pexpert/pexpert/arm64/H9.h)
- [XNU 8019.80.24 MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-8019.80.24/makedefs/MakeInc.def)
- [XNU 8019.80.24 ARM64 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8019.80.24/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 MakeInc.def](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/makedefs/MakeInc.def)
- [XNU 8796.141.3 ARM64 board_config.h](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/pexpert/pexpert/arm64/board_config.h)
- [XNU 8796.141.3 MakeInc.kernel](https://github.com/apple-oss-distributions/xnu/blob/xnu-8796.141.3/makedefs/MakeInc.kernel)


## Expanded six-snapshot public-source matrix

The original three-tree check established the first visible T8010/H9 source
transition. The expanded check now includes six immutable public snapshots:

| Role | Tag | T8010/H9 at audited paths? | Lock file |
|---|---|---:|---|
| Historical A10 reference | `xnu-7195.121.3` | Yes | `xnu/history/xnu-7195.121.3.lock.json` |
| Target-era public reference | `xnu-8020.101.4` | No | `xnu/history/xnu-8020.101.4.lock.json` |
| Intermediate transition | `xnu-8019.80.24` | No | `xnu/history/xnu-8019.80.24.lock.json` |
| Early Darwin 22 reference | `xnu-8796.101.5` | No | `xnu/history/xnu-8796.101.5.lock.json` |
| Selected iOS 16-generation candidate | `xnu-8796.141.3` | No | `xnu/BASELINE.lock.json` |
| Later public reference | `xnu-12377.1.9` | No | `xnu/history/xnu-12377.1.9.lock.json` |

The additional public comparisons are deliberately references, not proposed
baselines. In particular, the 19H422 target KernelCache reports
`8020.241.44~1/RELEASE_ARM64_T8010`, which is not an exact match for public
tag `xnu-8020.101.4`; the 20H392 donor reports
`8796.142.1.703.8~1/RELEASE_ARM64_T8015`, which is not an exact match for
public tag `xnu-8796.141.3`. Neither tag is an Apple source-to-binary
attestation. Product-specific build inputs and exact source revisions remain
unresolved.

The new `tools/audit_xnu_public_source_matrix.py` checks all six trees using
the same structural criteria as the existing three-tree audit: normal ARM64
machine allowlist, T8010 compiler/board flag, board_config block, H9 header,
and machine-selection rejection guard. Synthetic tests cover the expected
matrix, unexpected T8010 reintroduction, missing guards, and incorrect
snapshot counts. A dedicated GitHub Actions workflow checks out the pinned
commits read-only and runs the matrix.

A passing source matrix does not compile XNU, explain Apple's internal
product-specific build inputs, or establish iPhone9,1 compatibility.
