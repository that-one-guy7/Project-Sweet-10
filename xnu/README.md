# XNU work area

No XNU source is vendored yet.

1. Select the exact iOS 16-era XNU release after choosing the intended userland build.
2. Record upstream tag, commit SHA, license, and toolchain.
3. Establish an unmodified baseline build.
4. Keep A10-specific patches small and independently testable.

Do not copy the Qualcomm-specific SWEET machine configuration from ios-sweet.
