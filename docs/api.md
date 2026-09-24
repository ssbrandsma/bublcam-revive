# OSC / Scarlet API

Bublcam implements an Open Spherical Camera-style API plus vendor extensions.

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
 "serialNumber":"f4b85e1a4e97",
 "firmwareVersion":"2.1.1",
 "_bublAtmelVersion":"1",
 "_bublAlteraVersion":512,
 "gps":false,
 "gyro":false
}
```

Do not assume `gyro:false` means no physical gyro; semantics remain unknown.

A later live `/osc/info` response on the same serial and firmware reported `_bublAtmelVersion: "2.2"`. This version field is time-dependent on the observed unit; do not treat either value as universal. The same live camera reported 56% battery, `sessionId: "0"`, and an empty `_bublCommands` array on `/osc/state`.

## Verified request shapes

All requests below require `X-XSRF-Protected: 1`. JSON POST requests use `Content-Type: application/json`. Bubl's [ScarletTests client](https://github.com/BublTechnology/ScarletTests/blob/master/OscClient.js) provides the method and payload shapes; the items marked live were also exercised on firmware 2.1.1.

| Operation | Request | Body | Evidence |
|---|---|---|---|
| Info | GET `/osc/info` | none | Original client and live 200 |
| State | POST `/osc/state` | `{}` | Original client and live 200 |
| Check for updates | POST `/osc/checkForUpdates` | `{"stateFingerprint":"...","waitTimeout":0}` | Original client; live empty-body validation error |
| Execute command | POST `/osc/commands/execute` | `{"name":"camera.listImages","parameters":{...}}` | Original client and live 200 |
| Command status | POST `/osc/commands/status` | `{"id":123}` | Original client; not tested live |
| Bubl command poll | POST `/osc/commands/_bublPoll` | `{"id":123,"fingerprint":"...","waitTimeout":0}` | Original client; not tested live |
| Bubl command stop | POST `/osc/commands/_bublStop` | `{"id":123}` | Original client; not tested live |
| Bubl image download | GET `/osc/_bublGetImage/{encoded-fileUri}` | none | Original client and live 200 JPEG |

For `camera.listImages`, a live request used `{"entryCount":100,"includeThumb":true,"maxSize":10000000}` and returned `state:"done"`, `totalEntries:545`, 100 entries, and `continuationToken:"100"`. Its first URI was `bublfile://dcim/100bublc/bubl0628.jpg`; the image downloaded at exactly 5,603,999 bytes. `camera.getMetadata` with `{"fileUri":"bublfile://dcim/100bublc/bubl0628.jpg"}` returned `_bublMultiplex` XMP projection and 3840×3840 dimensions. These are observations of one device's storage state, not fixed properties.

`camera.startSession` with `{"timeout":120}` returned `cameraInExclusiveUse` during this investigation, although `/osc/state` showed no active Bubl command. The cause is unresolved. No session id was guessed or closed. Consequently the commands requiring a session were not tested live. A successful start response is specified by ScarletTests to include `results.sessionId` and `results.timeout`.

The [ScarletTests option test](https://github.com/BublTechnology/ScarletTests/blob/master/server_tests/test/clientTests.js) requests these OSC1 option names: `captureMode`, `exposureProgram`, `iso`, `shutterSpeed`, `aperture`, `whiteBalance`, `exposureCompensation`, `fileFormat`, `exposureDelay`, `sleepDelay`, `offDelay`, `hdr`, `exposureBracket`, `gyro`, `gps`, `imageStabilization`, and `_bublVideoFileFormat`. These names come from source tests; values and support on this camera still need a successful `getOptions` call.

The [ScarletTests schema](https://github.com/BublTechnology/ScarletTests/blob/master/server_tests/lib/schema.js) requires `_bublStreamPort`, `_bublStreamEndpoint`, and `_bublAccelTilt` in an in-progress OSC1 stream response. Their actual values and transport protocol remain unobserved on this unit.

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
The original [osc-client](https://github.com/BublTechnology/osc-client) and ScarletTests client show OSC1 `takePicture`, `_bublCaptureVideo`, `_bublTimelapse`, and `_bublStream` use `{"sessionId":"..."}`. `getOptions` uses `{"sessionId":"...","optionNames":[...]}`. `listImages`, image download, and metadata were exercised without a session. Other command behavior should still be verified on the device before relying on it.

## Errors seen in logs
`CameraInExclusiveUse`, `InvalidParameterValue`, `Internal`, `StorageMissing`, `InsufficientStorage`.

## Scarlet
Later logs use `scarlet` and module names resembling `iron::iron`, `iron::response`, `scarlet_server::osc::api`, `scarlet_server::osc::commands`. A Rust/Iron implementation is a strong inference, not yet a formally proven fact.

## Safe research order
info → state → read-only update check → inspect official tests → session → getOptions → list/download existing image → one test photo → study/test stream → short video. Stop if a session is held by another client; do not guess or close its session id.
