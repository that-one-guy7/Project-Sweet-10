# Kernel and userland version matching

## Current decision
- Userland reference: iOS 16.7.16 build 20H392, iPhone X family.
- XNU source candidate: Apple xnu-8796.141.3, commit 1b191cb58250d0705d8a51287127505aa4bc0789.
- Exact kernel/userland match: UNVERIFIED.

ios-sweet documents using the xnu-8796 generation and an iPhone X 20H392 userland. That establishes a useful project-level reference, but does not establish that the specific public XNU tag xnu-8796.141.3 is the exact kernel revision shipped in that image.

## Evidence needed
1. Read the kernel version string and build metadata from the exact iPhone X 20H392 build manifest or kernel image metadata.
2. Record the Darwin kernel version, XNU source revision string, architecture/configuration, and build suffix exactly as reported.
3. Compare those fields with Apple's public XNU tags and commit metadata.
4. Classify the result as exact, same source family only, or unresolved.
5. Tie the result to the exact reference device/model variant.

## Current classification
| Question | Status |
|---|---|
| Does Apple identify 20H392 as iOS 16.7.16? | Confirmed |
| Does ios-sweet identify its userland as iPhone X 20H392? | Confirmed |
| Does ios-sweet identify its kernel family as xnu-8796? | Confirmed |
| Is xnu-8796.141.3 the exact kernel revision in that IPSW? | Not verified |
| Does this establish iPhone9,1 platform support? | No |
| Has Project Sweet-10 built XNU? | No |
| Has Project Sweet-10 booted on iPhone9,1? | No |

## References
- Apple release listing: https://developer.apple.com/news/releases/?id=05112026j
- Apple iOS 16 update history: https://support.apple.com/en-us/101566
- ios-sweet README: https://github.com/dipa-studio/ios-sweet/blob/main/README.md
- Apple XNU candidate tag: https://github.com/apple-oss-distributions/xnu/tree/xnu-8796.141.3
