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

The [original ScarletTests client](https://github.com/BublTechnology/ScarletTests/blob/master/OscClient.js) sends `camera._bublStream` or `camera._bublCaptureVideo` to `/osc/commands/execute` with `{"sessionId":"..."}` on OSC1. The in-progress command id is stopped with `POST /osc/commands/_bublStop` and `{"id":123}`. The [test suite](https://github.com/BublTechnology/ScarletTests) confirms this pattern. Its schema specifies `_bublStreamPort`, `_bublStreamEndpoint`, and `_bublAccelTilt` in the in-progress stream response. Their values and the transport protocol have **not** been observed on this unit, so RTSP remains a hypothesis suggested by logs. Do not start a stream until the stop path is ready; then record the returned endpoint/port and stop it cleanly. Logs include an error corresponding to "stream not stopped".
