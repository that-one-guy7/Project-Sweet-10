# iPhone9,1 19H422 / iPhone10,3 20H392 graphics dyld image inventory

## Scope and provenance

This report records the user-supplied filtered image-list outputs:

- `19H422-graphics-candidates.txt`: target iPhone 7 `iPhone9,1` / D10AP / A10-T8010, iOS 15.8.8 build `19H422`.
- `20H392-graphics-candidates.txt`: donor iPhone X `iPhone10,3` / D22AP / A11-T8015, iOS 16.7.16 build `20H392`.

The outputs were generated with the user's standalone (non-Snap) `ipsw` executable, version `3.1.749`, build commit `a7dfadbcaca8375b424c12a68dae40767e5e07c1`. The two full image-list commands reportedly exited with status 0. The uploaded candidate files are the output of a case-insensitive filter for:

```text
AGX|Metal|IOGPU|IOSurface|IOMobileFramebuffer|CoreGraphics|GPU
```

Reported artifact sizes:

| File | Size |
|---|---:|
| 19H422 full image list | 240,662 bytes |
| 20H392 full image list | 293,678 bytes |
| 19H422 graphics candidates | 3,844 bytes |
| 20H392 graphics candidates | 4,036 bytes |

The target full-list preview reports iOS 15.8, 2,407 images, and five subcaches. The inventory indexes printed in the candidate files are local to each cache and must not be compared as cross-cache identities.

This is a host-side dyld image-list comparison. The physical iPhone 7 remains on iOS 12.1.4. No device, firmware, partition, security state, or boot state was changed.

## Summary

The filtered outputs contain 36 target candidate rows and 38 donor candidate rows. Comparing exact install paths gives:

- 34 exact install paths present in both filtered candidate lists.
- Two target-only candidate paths.
- Four donor-only candidate paths.
- Of the 34 shared paths, 33 have different reported source-version strings; `/usr/lib/swift/libswiftMetalKit.dylib` has the same reported version `1.3.0.0.0` in both.

These are image-list observations only. A cache image's presence does not establish that it is a direct dependency of a selected loader, that it is loaded at runtime, or that it supports the target hardware.

## Shared exact install paths

| Image install path | Target 19H422 version | Donor 20H392 version |
|---|---:|---:|
| `/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics` | `1557.7.1.0.0` | `1690.8.1.0.0` |
| `/System/Library/Frameworks/Metal.framework/Metal` | `261.13.4.0.0` | `306.6.6.0.0` |
| `/System/Library/Frameworks/MetalKit.framework/MetalKit` | `153.0.0.0.0` | `165.1.1.0.0` |
| `/System/Library/Frameworks/IOSurface.framework/IOSurface` | `302.15.0.0.0` | `336.60.1.0.0` |
| `/System/Library/PrivateFrameworks/IOMobileFramebuffer.framework/IOMobileFramebuffer` | `255.6.1.1.0` | `291.6.4.0.0` |
| `/System/Library/PrivateFrameworks/IOGPU.framework/IOGPU` | `35.29.0.0.0` | `65.60.1.0.0` |
| `/System/Library/PrivateFrameworks/AGXCompilerCore.framework/AGXCompilerCore` | `190.23.2.0.0` | `227.6.5.0.0` |
| `/System/Library/PrivateFrameworks/AGXGPURawCounter.framework/AGXGPURawCounter` | `190.23.2.0.0` | `227.6.5.0.0` |
| `/System/Library/Extensions/AGXGPURawCounterBundle.bundle/AGXGPURawCounterBundle` | `190.23.2.0.0` | `227.6.5.0.0` |
| `/System/Library/Extensions/AppleMetalGLRenderer.bundle/AppleMetalGLRenderer` | `94.5.0.0.0` | `99.0.0.0.0` |
| `/System/Library/VideoProcessors/MetalFilter.bundle/MetalFilter` | `191.7.1.0.0` | `332.1.0.0.0` |
| `/System/Library/PrivateFrameworks/MetalTools.framework/MetalTools` | `261.13.4.0.0` | `306.6.6.0.0` |
| `/System/Library/PrivateFrameworks/IOSurfaceAccelerator.framework/IOSurfaceAccelerator` | `115.2.4.1.0` | `140.3.6.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/MetalPerformanceShaders` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/MetalPerformanceShadersGraph.framework/MetalPerformanceShadersGraph` | `2.4.8.0.0` | `3.4.3.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/Frameworks/MPSCore.framework/MPSCore` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/Frameworks/MPSFunctions.framework/MPSFunctions` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/Frameworks/MPSImage.framework/MPSImage` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/Frameworks/MPSMatrix.framework/MPSMatrix` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/Frameworks/MPSNDArray.framework/MPSNDArray` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/Frameworks/MPSNeuralNetwork.framework/MPSNeuralNetwork` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/Frameworks/MetalPerformanceShaders.framework/Frameworks/MPSRayIntersector.framework/MPSRayIntersector` | `125.5.0.1.0` | `126.4.1.0.0` |
| `/System/Library/PrivateFrameworks/AGXCompilerConnection-S2A8.framework/AGXCompilerConnection-S2A8` | `17.0.0.0.0` | `25.0.0.0.0` |
| `/System/Library/PrivateFrameworks/AGXCompilerCore-S2A8.framework/AGXCompilerCore-S2A8` | `17.0.0.0.0` | `25.0.0.0.0` |
| `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libComposeFilters.dylib` | `31001.518.0.0.0` | `31001.722.3.1.0` |
| `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libGPUCompiler.dylib` | `31001.518.0.0.0` | `31001.722.3.1.0` |
| `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libGPUCompilerImpl.dylib` | `31001.518.0.0.0` | `31001.722.3.1.0` |
| `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libGPUCompilerImplLazy.dylib` | `31001.518.0.0.0` | `31001.722.3.1.0` |
| `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libGPUCompilerUtils.dylib` | `31001.518.0.0.0` | `31001.722.3.1.0` |
| `/System/Library/PrivateFrameworks/GPURawCounter.framework/GPURawCounter` | `25.0.0.0.0` | `27.3.0.0.0` |
| `/System/Library/PrivateFrameworks/GPUSupport.framework/libGPUSupportMercury.dylib` | `19.4.4.0.0` | `20.5.2.0.0` |
| `/usr/lib/swift/libswiftCoreGraphics.dylib` | `3.0.0.0.0` | `15.0.0.0.0` |
| `/usr/lib/swift/libswiftMetal.dylib` | `261.13.4.0.0` | `306.6.6.0.0` |
| `/usr/lib/swift/libswiftMetalKit.dylib` | `1.3.0.0.0` | `1.3.0.0.0` |

## Target-only filtered candidates

| Install path | Target 19H422 version |
|---|---:|
| `/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10` | `190.23.2.0.0` |
| `/System/Library/PrivateFrameworks/GPUCompiler.framework/Libraries/libmetal_timestamp.dylib` | `31001.518.0.0.0` |

## Donor-only filtered candidates

| Install path | Donor 20H392 version |
|---|---:|
| `/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11` | `227.6.5.0.0` |
| `/System/Library/Frameworks/MetalFX.framework/MetalFX` | `18.14.0.0.0` |
| `/System/Library/PrivateFrameworks/GPUToolsTransport.framework/GPUToolsTransport` | `226.3.0.0.0` |
| `/System/Library/PrivateFrameworks/WebGPU.framework/WebGPU` | `615.8.1.10.3` |

## Interpretation

1. **The cache contains generation-specific AGX plugin image paths.** The target candidate list contains `AGXMetalA10`; the donor candidate list contains `AGXMetalA11`. This agrees with the earlier KEXT metadata distinction between target AGXG9P/T8010 and donor AGXG10P/T8015. The selected donor KEXT metadata also contains the label `AGXMetalG10A0` for one personality, but no image path with that name appears in the supplied donor candidate list. A KEXT personality's `MetalPluginName` value must not be treated as an observed dyld install path.
2. **The shared framework names do not mean the builds are equivalent.** The common Metal, CoreGraphics, IOGPU, IOSurface, framebuffer, AGX compiler, and MetalKit images report different source versions. These are version-string observations, not API or ABI compatibility results.
3. **Donor-only candidates are not automatically required by the target.** MetalFX, WebGPU, and GPUToolsTransport appear in the supplied donor candidate filter. Their presence does not make them target requirements.
4. **Target-only candidates are not automatically missing functionality in the donor.** `AGXMetalA10` and `libmetal_timestamp.dylib` appear in the target candidate filter. This does not establish that the donor lacks a substitute or that the target library is usable with donor userland.
5. **The filter is intentionally incomplete.** Its expression did not include `IOKit` or `IOAccelerator`. Their absence from these candidate files is therefore not an absence finding. Query the full image lists for those terms before selecting further loader paths.
6. **Cache indexes are local.** For example, the Metal image is index 193 in the target list and 7 in the donor list. That difference reflects per-cache ordering and is not a dependency relationship or compatibility signal.

## Next bounded static work

First expand the image-path discovery to include IOKit and IOAccelerator-related names:

```bash
OUT="$HOME/agx-metal-static-audit"

for LABEL in 19H422 20H392; do
  grep -Ei 'IOKit|IOAccelerator|AGX|Metal|IOGPU|IOSurface|IOMobileFramebuffer|CoreGraphics|GPU' \
    "$OUT/$LABEL-image-list.txt" > "$OUT/$LABEL-graphics-candidates-expanded.txt" || true
done

wc -l "$OUT/19H422-graphics-candidates-expanded.txt" \
      "$OUT/20H392-graphics-candidates-expanded.txt"
```

Then inspect PrebuiltLoaderSet metadata for exact install paths confirmed in both full image lists. Prioritize Metal, CoreGraphics, IOSurface, IOMobileFramebuffer, IOGPU, AGXCompilerCore, MetalKit, and AppleMetalGLRenderer. Query the generation-specific AGX plugin paths separately:

- Target: `/System/Library/Extensions/AGXMetalA10.bundle/AGXMetalA10`
- Donor: `/System/Library/Extensions/AGXMetalA11.bundle/AGXMetalA11`

Keep each query against its corresponding cache. Record exit status and stderr separately. Keep exact image install paths, loader dependency paths, and printed dependency kinds. Keep cache image-list indexes distinct from loader reference indexes. Do not infer loader dependencies from image-list membership alone.

This report does not assert that these images are loaded, that a prebuilt-loader dependency will succeed on the target hardware, or that Metal renders successfully. M6 remains in progress; M7/SpringBoard has not started.
