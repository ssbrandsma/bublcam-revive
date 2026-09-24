# Controlled live tests, 2026-09-24

These observations come from one original Bublcam running firmware 2.1.1. The media, full responses, dynamic stream URLs, serial-bearing metadata, and device calibration are retained in the private research directory, not this repository. No option, firmware, or network setting was changed; no media was deleted.

## Session and options

Starting from `/osc/state` with `sessionId:""` and no active commands, `camera.startSession` with `{"timeout":120}` returned `state:"done"`, `results.sessionId:"0"`, and `results.timeout:120`. Two `camera.getOptions` calls queried 41 non-sensitive names. Both succeeded; `wifiPassword` and `_bublCalibration` were excluded. Closing exactly the returned session ID succeeded, and `/osc/state` again reported an empty session ID.

The live default capture mode was `image`. Still format was 3840×3840 JPEG; video format was 1920×1920 MP4, with 1440×1440 also reported as supported. `captureModeSupport` included `image`, `_bublVideo`, `_bublHdr`, and `_bublTimelapse`, whereas the archived source fixture lists only the first two. `exposureDelaySupport` was `[0,1,2,3,4]`, versus `[4]` in the fixture. Other reported values included `whiteBalance:"auto"`, `imageStabilization:"off"`, `gps:false`, `gyro:false`, and `hdr:false`. The reported `gpsInfo` values were `65535`, apparently invalid sentinels; the camera's `dateTimeZone` was in 2018 and was not corrected.

## One still photo

One `camera.takePicture` request returned `state:"inProgress"` with string command ID `"1"`. A later `/osc/commands/status` call using that ID returned `state:"done"` and a `bublfile://` JPEG URI. The camera still showed the capture as its latest image. Its original download was 10,067,594 bytes and 3840×3840; the list thumbnail was 155,112 bytes. Metadata reported `_bublMultiplex` projection. The capture remains on the camera and both downloads remain private. No second photo was taken.

## Short RTSP stream

Three short `_bublStream` attempts were stopped with `_bublStop`. The first two ended before a useful RTSP handshake; their reported endpoints appeared after a short startup delay. On the third, the command-status response provided port `8554` and a dynamically generated endpoint. `OPTIONS` and `DESCRIBE` to `rtsp://192.168.0.100:8554/<returned-endpoint>` both returned RTSP 200. The SDP server header named GStreamer RTSP server; SDP advertised H.264 video and 16 kHz MP4A-LATM audio. Decoded SPS signaled 1440×1440 H.264 High profile, level 4.0. No RTP frames were captured or decoded, so delivered frame rate and actual stream imagery are not established.

`_bublStop` returned HTTP 200 with an empty body; polling the same string command ID reached `done`. The client closed its own session and checked idle state. Each attempt had a different endpoint; do not reuse a prior endpoint or assume port 8554 on all units.

## One short video

One `_bublCaptureVideo` request returned `inProgress` with string command ID `"5"`. After roughly three seconds the client sent `_bublStop` for that ID, then polled until `done` and received an MP4 `bublfile://` URI. The camera's session was closed and `/osc/state` showed no active command. The 741,306-byte MP4 was downloaded privately without deleting it from the camera.

The resulting clip duration was 1.73 seconds, shorter than the start-to-stop interval. It contains 1920×1920 H.264 High-profile video and 16 kHz mono AAC audio. A decoded frame visibly shows four fisheye views in 960×960 quadrants. The clip is too short to establish normal frame rate or recording stability. Its metadata includes device-specific material and must not be published verbatim.

## Boundaries

These tests establish that this unit can start and close a controlled session, query options, take a still, serve an RTSP SDP, and record a short video. They do not establish long-duration reliability, synchronized stitching, every option's set behavior, valid GPS, or universal settings across Bublcam units. No firmware update, delete, shutdown, reset, `setOptions`, or unknown-session close was attempted.
