# OSC / Scarlet API

Bublcam implements an Open Spherical Camera-style API plus vendor extensions.

The read-only API is confirmed over Wi-Fi and was also reached over a verified USB/RNDIS route at `192.168.2.2` on this unit: `/osc/info` and `/osc/state` both succeeded on 2026-09-24. See [USB networking](usb-network.md). A later [interface-comparison attempt](../research/usb-wifi-comparison-2026-09-25.md) observed intermittent RNDIS resets, so USB API availability must not be confused with sustained USB link reliability. Verify the host route before probing the USB address.

## Advertised by live firmware 2.1.1
```text
/osc/info
/osc/state
/osc/checkForUpdates
/osc/_bublUpdate
/osc/_bublGetImage/:uri
/osc/commands/execute
/osc/commands/_bublStop
/osc/commands/_bublPoll
/osc/commands/status
```

Required header:
```text
X-XSRF-Protected: 1
```

Observed identity:
```json
{
 "manufacturer":"Bubl",
 "model":"bubl1",
 "serialNumber":"<redacted>",
 "firmwareVersion":"2.1.1",
 "_bublAtmelVersion":"1",
 "_bublAlteraVersion":512,
 "gps":false,
 "gyro":false
}
```

Do not assume `gyro:false` means no physical gyro; semantics remain unknown.

A later live `/osc/info` response on the same serial and firmware reported `_bublAtmelVersion: "2.2"`. It is not known whether the value changed or the earlier value was transcribed incorrectly; do not treat either as universal. The same live camera reported 56% battery, `sessionId: "0"`, and an empty `_bublCommands` array on `/osc/state`.

The first Atmel value came from a user-supplied JSON transcription; the later value came from a saved successful GET. The complete [evidence comparison](../research/atmel-version.md) leaves the reason for the difference unresolved.

## Verified request shapes

All requests below require `X-XSRF-Protected: 1`. JSON POST requests use `Content-Type: application/json`. Bubl's [ScarletTests client](https://github.com/BublTechnology/ScarletTests/blob/master/OscClient.js) provides the method and payload shapes; the items marked live were also exercised on firmware 2.1.1.

| Operation | Request | Body | Evidence |
|---|---|---|---|
| Info | GET `/osc/info` | none | Original client and live 200 |
| State | POST `/osc/state` | `{}` | Original client and live 200 |
| Check for updates | POST `/osc/checkForUpdates` | `{"stateFingerprint":"...","waitTimeout":0}` | Original client; live empty-body validation error |
| Execute command | POST `/osc/commands/execute` | `{"name":"camera.listImages","parameters":{...}}` | Original client and live 200 |
| Command status | POST `/osc/commands/status` | `{"id":"returned-id"}` | Original client and live 200; live IDs were strings |
| Bubl command poll | POST `/osc/commands/_bublPoll` | `{"id":123,"fingerprint":"...","waitTimeout":0}` | Original client; not tested live |
| Bubl command stop | POST `/osc/commands/_bublStop` | `{"id":"returned-id"}` | Original client and live 200 with empty body |
| Bubl image download | GET `/osc/_bublGetImage/{encoded-fileUri}` | none | Original client and live 200 JPEG |

For `camera.listImages`, a live request used `{"entryCount":100,"includeThumb":true,"maxSize":10000000}` and returned `state:"done"`, `totalEntries:545`, 100 entries, and `continuationToken:"100"`. Its first URI was `bublfile://dcim/100bublc/bubl0628.jpg`; the image downloaded at exactly 5,603,999 bytes. `camera.getMetadata` with `{"fileUri":"bublfile://dcim/100bublc/bubl0628.jpg"}` returned `_bublMultiplex` XMP projection and 3840×3840 dimensions. These are observations of one device's storage state, not fixed properties.

An earlier `camera.startSession` attempt returned `cameraInExclusiveUse` after a PowerShell client error. A later controlled attempt returned `results.sessionId:"0"` and `timeout:120`; the client closed its own returned session and verified idle state. This confirms `"0"` is a valid ID, but does not prove the cause of the earlier error. See [session analysis](../research/session-exclusive-use.md).

The [ScarletTests option test](https://github.com/BublTechnology/ScarletTests/blob/master/server_tests/test/clientTests.js) requests these OSC1 option names: `captureMode`, `exposureProgram`, `iso`, `shutterSpeed`, `aperture`, `whiteBalance`, `exposureCompensation`, `fileFormat`, `exposureDelay`, `sleepDelay`, `offDelay`, `hdr`, `exposureBracket`, `gyro`, `gps`, `imageStabilization`, and `_bublVideoFileFormat`. All were queried successfully on this unit.

### OSC1 `getOptions` inventory

The original [client UI](https://github.com/BublTechnology/ScarletTests/blob/master/client_ui/src/app/main/main.factory.js) lists the following 43 queryable names; the [bubl1 support fixture](https://github.com/BublTechnology/ScarletTests/blob/master/server_tests/defaults/bubl1_supports.json) supplies example values. These are **source fixture values**, not observations of the physical camera. `R/W` means the UI also exposes a `setOptions` control; `R/?` means write support was not established. `Support` fields are capability reports and read-only in the UI. Persistence is unverified for every writable setting; `status` and `capability` denote read-only current state or reported support, respectively. A successful OSC1 session is needed before querying any option.

| Option name | Read/write | Fixture value or support range | OSC/Bubl | Safe to query | Lifetime |
|---|---|---|---|---|---|
| `captureMode` | R/W | `image`, `_bublVideo` | OSC, Bubl value | Yes | Unknown |
| `captureModeSupport` | R | `image`, `_bublVideo` | OSC, Bubl value | Yes | Capability |
| `exposureProgram` | R/W | `2` | OSC | Yes | Unknown |
| `exposureProgramSupport` | R | `[2]` | OSC | Yes | Capability |
| `iso` | R/? | `0` | OSC | Yes | Unknown |
| `isoSupport` | R | `[]` | OSC | Yes | Capability |
| `shutterSpeed` | R/? | `0` | OSC | Yes | Unknown |
| `shutterSpeedSupport` | R | `[]` | OSC | Yes | Capability |
| `aperture` | R/? | `0` | OSC | Yes | Unknown |
| `apertureSupport` | R | `[]` | OSC | Yes | Capability |
| `whiteBalance` | R/W | `auto` | OSC | Yes | Unknown |
| `whiteBalanceSupport` | R | `[auto]` | OSC | Yes | Capability |
| `exposureCompensation` | R/? | `0` | OSC | Yes | Unknown |
| `exposureCompensationSupport` | R | `[]` | OSC | Yes | Capability |
| `fileFormat` | R/W | JPEG or raw, 3840×3840 | OSC | Yes | Unknown |
| `fileFormatSupport` | R | JPEG/raw, 3840×3840 | OSC | Yes | Capability |
| `exposureDelay` | R/W | Fixture `4`; UI offers `0`–`4` | OSC | Yes | Unknown |
| `exposureDelaySupport` | R | `[4]` in fixture | OSC | Yes | Capability |
| `sleepDelay` | R/W | Fixture `5` seconds | OSC | Yes | Unknown |
| `sleepDelaySupport` | R | `1,5,10,30,60,300,600,1200,2400,65535` | OSC | Yes | Capability |
| `offDelay` | R/W | Fixture `600` seconds | OSC | Yes | Unknown |
| `offDelaySupport` | R | Same list as `sleepDelaySupport` | OSC | Yes | Capability |
| `totalSpace` | R | Bytes; fixture 1 GiB | OSC | Yes | Status |
| `remainingSpace` | R | Bytes; fixture 1 GiB | OSC | Yes | Status |
| `remainingPictures` | R | Count; fixture `125` | OSC | Yes | Status |
| `gpsInfo` | R/? | `{lat,lng}`; fixture zeros | OSC | Yes | Status/unknown |
| `dateTimeZone` | R/? | `YYYY:MM:DD HH:MM:SS±HH:MM` | OSC | Yes | Status/unknown |
| `hdr` | R/W | Boolean | OSC | Yes | Unknown |
| `hdrSupport` | R | Boolean; fixture `true` | OSC | Yes | Capability |
| `exposureBracket` | R/W | `{autoMode:true}`; UI also offers 3 shots with increment 0.5–3.0 | OSC | Yes | Unknown |
| `exposureBracketSupport` | R | Fixture supports `{autoMode:true}` | OSC | Yes | Capability |
| `gyro` | R | Boolean; fixture `false` | OSC | Yes | Status |
| `gyroSupport` | R | Boolean; fixture `false` | OSC | Yes | Capability |
| `gps` | R | Boolean; fixture `false` | OSC | Yes | Status |
| `gpsSupport` | R | Boolean; fixture `false` | OSC | Yes | Capability |
| `imageStabilization` | R/W | `off` | OSC | Yes | Unknown |
| `imageStabilizationSupport` | R | `[off]` | OSC | Yes | Capability |
| `wifiPassword` | R/W | Masked in fixture | OSC | Sensitive; avoid in public logs | Unknown |
| `_bublVideoFileFormat` | R/W | MP4, 1920×1920 or 1440×1440 | Bubl | Yes | Unknown |
| `_bublVideoFileFormatSupport` | R | Both MP4 sizes in fixture | Bubl | Yes | Capability |
| `_bublCalibration` | R/W | String; fixture empty | Bubl | Sensitive; avoid in public logs | Unknown |
| `_bublTimelapse` | R/? | `{interval:5}` in fixture | Bubl | Yes | Unknown |
| `_bublCount` | R/? | `{count:[0,0],hdr:0,timelapse:0}` in fixture | Bubl | Yes | Status/unknown |

Two live `camera.getOptions` requests returned values for 41 non-sensitive names. `wifiPassword` and `_bublCalibration` were deliberately omitted; no `setOptions` call was made. The live camera reported `captureMode:"image"`, `fileFormat:{"type":"jpeg","width":3840,"height":3840}`, `_bublVideoFileFormat:{"type":"mp4","width":1920,"height":1920}`, and `exposureDelay:4`. Its `captureModeSupport` additionally included `_bublHdr` and `_bublTimelapse`, unlike the fixture; `exposureDelaySupport` was `[0,1,2,3,4]`, and video-format support included 1920×1920 and 1440×1440. `gpsInfo` returned sentinel-like `65535` coordinates, not a valid location. `dateTimeZone` reported a 2018 date on the 2026 test day, so the device clock should not be trusted. See [live test report](../research/live-capture-2026-09-24.md). The table above remains explicitly labeled as fixture data.

The [ScarletTests schema](https://github.com/BublTechnology/ScarletTests/blob/master/server_tests/lib/schema.js) requires `_bublStreamPort`, `_bublStreamEndpoint`, and `_bublAccelTilt` in an in-progress OSC1 stream response. A live test confirmed a dynamic RTSP endpoint on port 8554; see [streaming](streaming.md).

## Command names found in historical Bubl material
Standard:
```text
camera.startSession
camera.takePicture
camera.listImages
camera.delete
camera.getImage
camera.getMetadata
camera.setOptions
camera.getOptions
```
Bubl extensions:
```text
camera._bublCaptureVideo
camera._bublTimelapse
camera._bublStream
camera._bublShutdown
```
The original [osc-client](https://github.com/BublTechnology/osc-client) and ScarletTests client show OSC1 `takePicture`, `_bublCaptureVideo`, `_bublTimelapse`, and `_bublStream` use `{"sessionId":"..."}`. `getOptions` uses `{"sessionId":"...","optionNames":[...]}`. `takePicture`, `_bublCaptureVideo`, and `_bublStream` were exercised live in controlled tests; `_bublTimelapse` was not. `listImages`, image download, and metadata were exercised without a session. Other command behavior should still be verified on the device before relying on it.

## Errors seen in logs
`CameraInExclusiveUse`, `InvalidParameterValue`, `Internal`, `StorageMissing`, `InsufficientStorage`.

## Scarlet
Later logs use `scarlet` and module names resembling `iron::iron`, `iron::response`, `scarlet_server::osc::api`, `scarlet_server::osc::commands`. A Rust/Iron implementation is a strong inference, not yet a formally proven fact.

## Safe research order
info → state → read-only update check → inspect official tests → session → getOptions → list/download existing image → one test photo → study/test stream → short video. Stop if a session is held by another client; do not guess or close its session id.
