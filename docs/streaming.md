# Video / streaming

Firmware clues:
```text
/opt/bubl/scripts/video_capture.sh 1920x1920
FFmpeg 2.5.2
GStreamer 0.10
gstrtspserver
H.264 High Profile
1920×1920 @ 15 fps
YUV420p
AAC mono 16 kHz
```
TI HDVICP/h264enc messages indicate hardware encoding.

Known extension names:
```text
camera._bublCaptureVideo
camera._bublStream
/osc/commands/_bublStop
/osc/commands/_bublPoll
```

The [original ScarletTests client](https://github.com/BublTechnology/ScarletTests/blob/master/OscClient.js) sends `camera._bublStream` or `camera._bublCaptureVideo` to `/osc/commands/execute` with `{"sessionId":"..."}` on OSC1. The in-progress command id is stopped with `POST /osc/commands/_bublStop` and `{"id":123}`. The [test suite](https://github.com/BublTechnology/ScarletTests) confirms this pattern. Its schema specifies `_bublStreamPort`, `_bublStreamEndpoint`, and `_bublAccelTilt` in the in-progress stream response.

On 2026-09-24, three short stream-start/stop tests on firmware 2.1.1 returned port `8554` and a different eight-character endpoint each time. The endpoint sometimes appeared only in a subsequent command-status response. RTSP `OPTIONS` and `DESCRIBE` to the reported URL both returned 200; the server identified itself as GStreamer RTSP server. SDP advertised H.264 video and 16 kHz MP4A-LATM audio. Decoding the SDP H.264 SPS gives 1440×1440, High profile, level 4.0. No RTP frames were decoded, so frame rate and actual delivered image quality remain unverified. These are observations from one camera, not universal defaults.

`_bublStop` returned HTTP 200 with an empty body, followed by command status `done`. The client closed only its own session and `/osc/state` showed no active session or command. A dynamic endpoint must not be hard-coded. Prepare the stop path before starting a stream. Logs include an older error corresponding to "stream not stopped".

A separate one-shot `_bublCaptureVideo` test was stopped after about three seconds. The resulting MP4 was 1.73 seconds long, 1920×1920 H.264 High profile with 16 kHz mono AAC; its first decoded frame visibly contained four fisheye quadrants. The short clip's measured average frame rate is not evidence of nominal recording frame rate. The file remains on the camera and was downloaded only to private research storage. See the [live test report](../research/live-capture-2026-09-24.md).
