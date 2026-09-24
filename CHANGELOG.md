# Changelog

## Unreleased
Recorded a passive COM4 attempt after the Bublcam USB node returned: Windows reported `MaxBaudRate: 115200`, but opening at 115200 8N1 with DTR/RTS off failed before any data transfer. Actual serial speed/function remains unknown.

Compared connected, unplugged, and reconnected Windows PnP snapshots for USB cable #3. Identified Bublcam `0525:A4A2` as a COM4/`usbser` binding with `RNDIS/Ethernet Gadget` bus string; reconnection produced descriptor failure Code 43. No USB network adapter or `192.168.2.x` route appeared.

Documented a non-destructive Windows USB attachment check: no camera-attributable USB interface or `192.168.2.x` route was present, so USB services were not probed. Correlated archived `g_ether`/`usb0` lines with historical Scarlet HTTP requests from `.2.1` to `.2.2:80`.

Integrated the separate project's geometric stitcher, batch runner, and local WebGL viewer; added a feature-score validation wrapper. Verified one full-size panorama, one-pair batch run, zero inferred turns, and all six reported model/convention scores on `BUBL0001` while keeping media private.

Documented the separately reported 545-image stitching result, per-image calibration variation, feature-supported geometry, and remaining focal-scale/parallax uncertainties.

Verified a controlled OSC1 session, 41 live non-sensitive option values, one new still capture, a stoppable RTSP stream, and one short MP4 recording on firmware 2.1.1. Captured media remains private.

Documented the downloaded four-view JPEG and exact list thumbnail, including matching calibration and the API-only `_bublMultiplex` label. Added an OSC1 option inventory, session/exclusive-use analysis, Atmel-version provenance, and a second-image stitching report. The experimental stitcher now accepts per-quadrant 90-degree rotations with optical-centre adjustment.

Initial preservation repository: hardware, disassembly, battery diagnosis, firmware analysis, OSC/network notes, calibration/image format, UART/USB/streaming notes, calibration extractor, safe API probe and experimental stitcher.
