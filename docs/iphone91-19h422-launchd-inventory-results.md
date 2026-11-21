# Exact iPhone10,3 / 20H392 versus iPhone9,1 / 19H422 launchd inventory comparison

## Scope and source identities

This is a read-only comparison of two outputs from the same
`tools/inspect_launchd_jobs.py` inventory schema. Both summarize the central
`System/Library/xpc/launchd.plist` LaunchDaemons dictionary and its advertised
MachServices.

- **Donor:** iPhone10,3 / D22AP / A11-T8015 / iOS 16.7.16 / build 20H392.
- **Target reference:** iPhone9,1 / D10AP / A10-T8010 / iOS 15.8.8 / build 19H422.

The target reference is one major iOS release older than the donor. Differences
may reflect OS-version changes as well as product/board differences; do not
attribute them to hardware alone. The 19H422 inventory is not an iOS 16
iPhone7 userland image.

Source plist SHA-256 values:

| Source | SHA-256 |
|---|---|
| 20H392 donor | `810070302b5c4d7c5f00bdc8df20aaea2dd33cd8342d2402fcdf7ff6397d374c` |
| 19H422 target reference | `34b6a174d2b948035afd71ad0a4fc2d3e4e85ea807a794ee69722054b09d6bbe` |

The physical iPhone 7 remains on iOS 12.1.4. All inputs were host-side
inventory JSON; no phone connection, firmware installation, boot operation,
or device modification was involved.

## Aggregate comparison

| Metric | 20H392 donor | 19H422 target | Difference (target - donor) |
|---|---:|---:|---:|
| LaunchDaemons entries | 532 | 475 | -57 |
| Unique job labels | 530 | 475 | -55 |
| MachService occurrences across jobs | 1,707 | 1,493 | -214 |
| Distinct MachService index names | 1,668 | 1,485 | -183 |
| Service names with multiple provider labels | 21 | 8 | -13 |
| Maximum provider labels for one service | 3 | 2 | -1 |

The donor inventory contains two repeated job labels:
`com.apple.CommCenter` (the regular and `-noncellular` plist entries) and
`com.apple.sysdiagnose` (the regular and `-darwinos` entries). The target
inventory has no repeated job labels. This is why donor LaunchDaemons entry
count (532) and unique job-label count (530) differ.

### Exact service-name set comparison

The provider index gives the following exact set counts:

| Set | Count |
|---|---:|
| Names present in both inventories | **1,451** |
| Donor-only names (20H392) | **217** |
| Target-only names (19H422) | **34** |

Set arithmetic was checked against the declared unique-name totals:
1,451 + 217 = 1,668 donor names; 1,451 + 34 = 1,485 target names.
The names below are retained exactly as the inspector emitted them, including
non-`com.apple.*` keys.

### Donor-only service names (217)

```text
HostSpecialPort
Interactive
_ExperimentalNonLaunching
com.apple.AccessibilityUIServer
com.apple.AuthenticationServices.AutoFill
com.apple.BTLELoggingManager.xpc
com.apple.CarPlayApp.punch-through-service
com.apple.ClockAngel.mach
com.apple.DeviceAccess.xpc
com.apple.DiskArbitration.diskarbitrationd
com.apple.MTLAssetUpgraderD
com.apple.ManagedSettingsAgent.publisher
com.apple.MediaGroups.daemon
com.apple.OSIntelligence.charging
com.apple.PassbookUISceneService.remote-ui
com.apple.ProximityControl.HandoffViewServiceHost
com.apple.RemoteManagementAgent
com.apple.RemoteManagementAgent.store
com.apple.ReplayKitAngel.mach
com.apple.SafetyKit
com.apple.ScreenTimeAgent.downtime
com.apple.StatusKit.presence
com.apple.SystemConfiguration.configd.watchdog
com.apple.UIKit.OverlayUI.services
com.apple.VideoSubscriberAccount.AnalyticsService
com.apple.aa.usernotifications.xpc
com.apple.accessibility.AXSwitchControlServer
com.apple.accessibility.axAuditDaemon.deviceservice.lockdown
com.apple.accessibility.axAuditDaemon.deviceservice.xpc
com.apple.accessoryupdater.uarp.standaloneCommandListener
com.apple.activityawardsd
com.apple.adid.xpc
com.apple.ak.puffin.xpc
com.apple.amfi.lockdown
com.apple.amfi.xpc
com.apple.anomalydetectiond.kappa
com.apple.anomalydetectiond.trigger
com.apple.ap.promotedcontent.signing
com.apple.applecamerad
com.apple.aps.ActivitySharing.push
com.apple.aps.UsageTrackingAgent
com.apple.aps.family
com.apple.aps.financed
com.apple.aps.financed.store
com.apple.aps.homekit
com.apple.aps.imagent
com.apple.aps.itunescloudd
com.apple.aps.mobileassetd
com.apple.aps.safetyalerts
com.apple.aps.sessioncore.PushNotifications
com.apple.aps.sessioncore.PushNotifications.dev
com.apple.aps.storekitservice
com.apple.aps.transparencyd
com.apple.aps.watchlistd
com.apple.aps.watchlistd.dev
com.apple.aps.weather
com.apple.aps.webkit.webpushd.incoming-push
com.apple.avconference.xpc
com.apple.backgroundassets.lockdownservice
com.apple.backgroundassets.system
com.apple.backgroundassets.user
com.apple.biome.ContextSync
com.apple.biome.access.system
com.apple.biome.access.user
com.apple.biomed.sensorActivation
com.apple.biomesyncd.realTimeSession
com.apple.bluetoothuser.xpc
com.apple.callkit.service
com.apple.carkit.layer-metadata
com.apple.carkit.pairing.service
com.apple.cfprefsd.daemon.system
com.apple.chrono.event-service.gamed
com.apple.commcenter.mobile-helper-xpc
com.apple.commcenter.root-helper-xpc
com.apple.containermanagerd.system
com.apple.coreidvd.digital-presentment.xpc
com.apple.coreidvd.identity-proofing-data-sharing.xpc
com.apple.coremedia.bytestream.xpc
com.apple.coremedia.figcontentkeyboss.xpc
com.apple.coremedia.figvirtualcapturecard.xpc
com.apple.coremedia.mediaparserd.formatreader.xpc
com.apple.coremedia.mediaparserd.manifold.xpc
com.apple.coremedia.mediaparserd.mutablemovie.xpc
com.apple.coremedia.mediaparserd.playlistfileparser.xpc
com.apple.coremedia.mediaparserd.streamplaylistparser.xpc
com.apple.coremedia.mediaparserd.utilities
com.apple.corespeech.corespeechd.rchandling.service
com.apple.corespeech.corespeechd.uaapservice
com.apple.corespotlight.daemon.calendar
com.apple.countryd.update
com.apple.cvhwa.xpc
com.apple.donotdisturb.appconfiguration.service
com.apple.dropin.xpc
com.apple.dt.previewsd.agentpipeservice.host-to-sim
com.apple.dt.previewsd.previewservice.host-to-sim
com.apple.dt.remotepairingdeviced.lockdown
com.apple.fairplaydeviceidentityd
com.apple.family.notifier
com.apple.financed.service.coredatastore
com.apple.financed.service.financestore
com.apple.financed.service.store
com.apple.fitnesscoachingd
com.apple.griddatad.registration
com.apple.icloud.searchpartyd.beaconmanager.simplebeacon
com.apple.icloud.searchpartyd.beaconsharingservice
com.apple.inboxupdaterd
com.apple.inputanalytics.testAppRelay
com.apple.inputservice.input-ui-host
com.apple.inputservice.keyboardui
com.apple.inputservice.teletype
com.apple.instruments.deviceservice.lockdown.secure
com.apple.instruments.deviceservice.xpc
com.apple.intelligenceplatform.Coordination
com.apple.intelligenceplatform.EntityResolution
com.apple.intelligenceplatform.Internal
com.apple.intelligenceplatform.Knosis
com.apple.intelligenceplatform.KnowledgeConstruction
com.apple.intelligenceplatform.Lighthouse
com.apple.intelligenceplatform.View
com.apple.internal.addressbooksync.testcontrol
com.apple.internal.eventkitsync.testcontrol
com.apple.keychainsharingmessagingd
com.apple.linkd.autoShortcut
com.apple.linkd.cliSupport
com.apple.linkd.extension
com.apple.linkd.registry
com.apple.linkd.suggestions
com.apple.linkd.transcript
com.apple.locationd.gathering
com.apple.lockdown.mobilebackup2
com.apple.lsd.rebuild
com.apple.lsd.system.mapdb
com.apple.lsd.system.modifydb
com.apple.lsd.system.rebuild
com.apple.mDNSResponder.control
com.apple.matter.framework.xpc
com.apple.matter.support.xpc
com.apple.mediaexperience.xctest.xpc
com.apple.mediaremoteui.services
com.apple.mobileasset.autoasset
com.apple.mobileassetd.push-notifications
com.apple.momentsd
com.apple.nanotimekit.devicelibraryserver
com.apple.naturallanguaged
com.apple.networkserviceproxy.fetch-token
com.apple.paperboard.services
com.apple.pearld
com.apple.posterboardservices.services
com.apple.powerd.coresmartpowernap
com.apple.powerd.smartpowernap
com.apple.powerui.bdcdata
com.apple.private.alloy.contextsync-idswake
com.apple.private.alloy.dropin.communication-idswake
com.apple.private.alloy.dropin.setup-idswake
com.apple.private.alloy.healthapp.messaging
com.apple.private.alloy.kappa-idswake
com.apple.private.alloy.kcsharing.invite-idswake
com.apple.private.alloy.keytransparency.accountkey.pinning-idswake
com.apple.private.alloy.sessionkit-idswake
com.apple.private.alloy.usagetracking-idswake
com.apple.proactive.FaceSuggestions.xpc
com.apple.proactive.SuggestedPages
com.apple.proactive.UserEducationSuggestion.client-listener.xpc
com.apple.proactive.UserEducationSuggestion.server-listener.xpc
com.apple.proactive.sleepSchedule
com.apple.purplebuddy.budd.proximityautomateddeviceenrollment.target.xpc
com.apple.rapport.StatusUpdates
com.apple.remoted.compute-platform
com.apple.remotepairingdevice.pairingmanagement
com.apple.remotepairingdevice.tunnelmanagement
com.apple.safetyalerts
com.apple.searchparty.BeaconScanningSession
com.apple.searchparty.managedperipheral
com.apple.security.cryptex.xpc
com.apple.seserviced.session
com.apple.sessionservices
com.apple.sharing.airdropui.services
com.apple.sharing.collaborationuserdefaults
com.apple.shazamd.events
com.apple.shazamd.shop
com.apple.shazamd.ui
com.apple.shortcuts.view-service
com.apple.siri.shared_flow_plugin_service
com.apple.sirisuggestions
com.apple.sirittsd
com.apple.softposreaderd
com.apple.softwareupdateservicesui.controller
com.apple.sos.status
com.apple.sportsd.session.xpc
com.apple.storagekitd
com.apple.storekitd
com.apple.synapse.notes-activation-service
com.apple.telephonyutilities.callservicesdaemon.callhistorycontroller
com.apple.telephonyutilities.callservicesdaemon.conversationprovidermanager
com.apple.telephonyutilities.callservicesdaemon.ptt
com.apple.thermalMonitor.siriEnabledNote
com.apple.timed.accessory-timesync
com.apple.timesync.expositor
com.apple.timesync.manager
com.apple.timesync.ptp.manager
com.apple.translation.text
com.apple.transparencyd.ids
com.apple.transparencyd.ids-support
com.apple.usernotifications.delegate.com.apple.AppleMediaServicesUI.engagement.notifications.macOS
com.apple.usernotifications.delegate.com.apple.MobileSMS
com.apple.usernotifications.delegate.com.apple.NDO.FollowUp
com.apple.usernotifications.delegate.com.apple.Sharing.AirDropUIRemoteNotifications
com.apple.usernotifications.delegate.com.apple.UserNotifications.DeviceDiscoveryUIAgent
com.apple.usernotifications.delegate.com.apple.commandandcontrol
com.apple.usernotifications.delegate.com.apple.crossdevicearbitration.feedback.notification
com.apple.usernotifications.delegate.com.apple.identityservicesd.firewall
com.apple.usernotifications.delegate.com.apple.powerlog.proactivenotifications
com.apple.usernotifications.delegate.com.apple.proactive.EvaluationNotifications
com.apple.usernotifications.delegate.com.apple.sosd.usernotification
com.apple.usernotifications.delegate.com.apple.tccd
com.apple.watchpresenced
com.apple.webkit.webpushd.service
```

### Target-only service names (34)

```text
com.apple.ActivitySharing.push
com.apple.MobileTimer.sleepmodeserver
com.apple.addressbooksync.statusreporter
com.apple.adprivacyd.pfl
com.apple.aps.biome.mapreduce
com.apple.assistant.cdmsetup
com.apple.biometrickitd
com.apple.carkit.layers
com.apple.coreduetd
com.apple.coreduetd.batterysaver
com.apple.coreidvd.identity-management.xpc
com.apple.coreidvd.identity-sharing-ui.xpc
com.apple.coreidvd.identity-sharing.xpc
com.apple.coremedia.endpointpicker.xpc
com.apple.eventkitsync.statusreporter
com.apple.idcredd.payload-builder.xpc
com.apple.imagent.aps
com.apple.itunescloudd.aps
com.apple.mobile.usermanagerd.synchronous.xpc
com.apple.mobiletimersync.pairedsync
com.apple.multimodalsearch.SearchService
com.apple.nsurlsessiond.NSURLSessionProxyService
com.apple.pommes.DebugService
com.apple.security.cryptexd.sessions
com.apple.security.tribeca
com.apple.siriknowledged.SiriSessionService
com.apple.syncdefaultsd
com.apple.syncdefaultsd.push
com.apple.usernotifications.delegate.com.apple.NanoAlarm
com.apple.usernotifications.delegate.com.apple.private.NanoTimer
com.apple.voicememod.datastore.EncryptedCloud
com.apple.voicememod.datastore.Local
com.apple.watchlistd.aps
com.apple.watchlistd.aps.dev
```

## Provider-label changes for names present in both (21)

These names exist in both service-name sets, but their provider-label lists
differ. The labels are static provider declarations, not observations of
successful registration.

| Service name | 20H392 providers | 19H422 providers |
|---|---|---|
| `PurpleSystemAppPort` | `com.apple.ClarityBoard`, `com.apple.SpringBoard`, `com.apple.checkerboard` | `com.apple.SpringBoard`, `com.apple.checkerboard` |
| `com.apple.DragUI.druid.system` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.SBUserNotification` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.UIKit.KeyboardManagement.hosted` | `com.apple.ClarityBoard`, `com.apple.SpringBoard`, `com.apple.checkerboard` | `com.apple.SpringBoard`, `com.apple.checkerboard` |
| `com.apple.aps.remotemanagementd.http.apns-dev` | `com.apple.RemoteManagementAgent`, `com.apple.remotemanagementd` | `com.apple.remotemanagementd` |
| `com.apple.aps.remotemanagementd.http.apns-prod` | `com.apple.RemoteManagementAgent`, `com.apple.remotemanagementd` | `com.apple.remotemanagementd` |
| `com.apple.biome.PublicStreamAccessService` | `com.apple.biomed` | `com.apple.contextstored` |
| `com.apple.bulletinboard.dataproviderconnection` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.bulletinboard.observerconnection` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.bulletinboard.serverconduitconnection` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.bulletinboard.settingsconnection` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.frontboard.systemappservices` | `com.apple.ClarityBoard`, `com.apple.SpringBoard`, `com.apple.checkerboard` | `com.apple.SpringBoard`, `com.apple.checkerboard` |
| `com.apple.frontboard.workspace` | `com.apple.ClarityBoard`, `com.apple.checkerboard` | `com.apple.checkerboard` |
| `com.apple.mobile.keybagd.UserManager.xpc` | `com.apple.mobile.usermanagerd` | `com.apple.mobile.keybagd` |
| `com.apple.mobile.usermanagerd.xpc` | `com.apple.mobile.usermanagerd` | `com.apple.mobile.keybagd` |
| `com.apple.storekit.configuration.xpc` | `com.apple.storekitd` | `com.apple.appstored` |
| `com.apple.system.libinfo.muser` | `com.apple.mobile.usermanagerd` | `com.apple.mobile.keybagd` |
| `com.apple.usernotifications.usernotificationservice` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.usernotifications.usernotificationsettingsservice` | `com.apple.ClarityBoard`, `com.apple.SpringBoard` | `com.apple.SpringBoard` |
| `com.apple.videoconference.avconference` | `com.apple.avconferenced`, `com.apple.mediaserverd` | `com.apple.mediaserverd` |
| `com.apple.videoconference.camera` | `com.apple.avconferenced`, `com.apple.mediaserverd` | `com.apple.mediaserverd` |

The donor has 21 service names with multiple provider labels; the target has
8. The target multi-provider list is the subset remaining after the provider
changes above: `PurpleSystemAppPort`,
`com.apple.UIKit.KeyboardManagement.hosted`,
`com.apple.UIKit.statusbarserver`,
`com.apple.frontboard.systemappservices`, the three `com.apple.iap2d.*`
services, and `com.apple.proactive.HomeScreenSuggestion.xpc`.

## LaunchDaemon job-label comparison

Comparing the set of job-label strings (not plist file paths) gives:

| Set | Count |
|---|---:|
| Labels present in both | 471 |
| Donor-only labels | 59 |
| Target-only labels | 4 |

Two donor labels are repeated across separate plist entries as noted above.
The exact LaunchDaemon plist path distinguishes the two CommCenter entries.
The donor has a `com.apple.CommCenter-noncellular.plist` job entry that is
absent from the target inventory.

Target-only labels:
- `com.apple.atc.atwakeup`
- `com.apple.biometrickitd.mesa`
- `com.apple.coreparsec.silhouette`
- `com.apple.multimodalsearchd`

The count of donor-only labels is preserved here; the focus of this audit is
the exact MachService set, not a per-label inventory of every unrelated
LaunchDaemon.

## Selected GUI and platform job comparison

For each common job below, program paths match exactly. The `RunAtLoad` and
`KeepAlive` summaries shown are also the same on both sides for the matching
plist path; null is preserved as null.

| Job | Donor services | Target services | Exact per-job difference |
|---|---:|---:|---|
| `backboardd` | 18 | 18 | Identical service-name sets |
| `runningboardd` | 3 | 3 | Identical service-name sets |
| `SpringBoard` | 33 | 32 | Donor-only: `com.apple.proactive.UserEducationSuggestion.client-listener.xpc` |
| `configd` | 9 | 8 | Donor-only: `com.apple.SystemConfiguration.configd.watchdog` |
| `notifyd` | 1 | 1 | Identical service-name sets |
| `mediaserverd` | 87 | 82 | Six donor-only and one target-only name (listed below) |
| `wifid` | 7 | 7 | Identical service-name sets |
| `bluetoothd` | 13 | 13 | Identical service-name sets |
| `mobileactivationd` | 2 | 2 | Identical service-name sets |

The selected paths and summarized launch policies are:

| Job | Executable path (both inventories) | RunAtLoad | KeepAlive |
|---|---|---|---|
| `backboardd` | `/usr/libexec/backboardd` | true | always |
| `runningboardd` | `/usr/libexec/runningboardd` | true | always |
| `SpringBoard` | `/System/Library/CoreServices/SpringBoard.app/SpringBoard` | true | always |
| `configd` | `/usr/libexec/configd` | null | always |
| `notifyd` | `/usr/sbin/notifyd` | null | unspecified |
| `mediaserverd` | `/usr/sbin/mediaserverd` | null | always |
| `wifid` | `/usr/sbin/wifid` | true | always |
| `bluetoothd` | `/usr/sbin/bluetoothd` | true | conditions: `SuccessfulExit` |
| `mobileactivationd` | `/usr/libexec/mobileactivationd` | null | unspecified |

For `mediaserverd`, 81 names are common. Donor-only names are
`com.apple.avconference.xpc`,
`com.apple.coremedia.bytestream.xpc`,
`com.apple.coremedia.figcontentkeyboss.xpc`,
`com.apple.coremedia.figvirtualcapturecard.xpc`,
`com.apple.cvhwa.xpc`, and
`com.apple.mediaexperience.xctest.xpc`. The target-only name is
`com.apple.coremedia.endpointpicker.xpc`.

### CommCenter and Setup Assistant entries

- The standard `com.apple.CommCenter.plist` exists on both sides with 12
  identical advertised services and the same program path and KeepAlive mode.
- The donor additionally has `com.apple.CommCenter-noncellular.plist`
  (same `com.apple.CommCenter` label; 11 services). There is no corresponding
  target plist entry in this inventory.
- `com.apple.CommCenterMobileHelper` has 4 donor services and 3 target
  services. Donor-only: `com.apple.commcenter.mobile-helper-xpc`.
- `com.apple.CommCenterRootHelper` has 4 donor services and 3 target
  services. Donor-only: `com.apple.commcenter.root-helper-xpc`.
- `com.apple.purplebuddy.budd` has 7 donor services and 6 target services.
  Donor-only: `com.apple.purplebuddy.budd.proximityautomateddeviceenrollment.target.xpc`.

The target `backboardd` advertises the touch-delivery, HID, display, and
IOHID event-system service names in its plist. Its service-name set is
identical to the donor's for this daemon. That observation is useful for the
static inventory but does not demonstrate target driver attachment, service
registration, or actual touch-event delivery.

## Interpretation and limits

This comparison establishes exact differences in the **static contents of the
provider index generated from two central launchd plists**. It does not
establish that any process starts, that a Mach service registers, which
clients use each endpoint, or that a target daemon's binary, frameworks,
entitlements, IOKit providers, or hardware are compatible.

The iOS versions and board identities differ. The 20H392 inventory is an
iPhone X donor reference, while 19H422 is a stock iPhone 7 target reference;
the latter is iOS 15.8.8, not the intended iOS 16 userland. Therefore, these
set differences are not a standalone compatibility verdict.

This report covers the central LaunchDaemons dictionary only. It does not
include LaunchAgents, embedded XPC bundle plists, executable contents, all
client dependencies, or runtime process state. The JSON reports intentionally
omit full ProgramArguments and environment-variable values. The full JSON
files are not committed.

**M6 remains in progress. M7/SpringBoard has not started.** This inventory
does not establish an iOS 16 launchd configuration for iPhone9,1 and does
not close readiness gate G9. The physical iPhone 7 remains on iOS 12.1.4.
