# Findings / backlog

## Confirmed live
- Firmware 2.1.1; model bubl1.
- API at 192.168.0.100:80.
- `X-XSRF-Protected: 1` works.
- Altera version 512 reported. Atmel version was `"1"` in one supplied response and `"2.2"` in a later live response; why it changed is unknown.
- Firmware 2.1.1 listed 545 files on the tested storage and served one 3840×3840 JPEG through the Bubl image endpoint.
- The downloaded JPEG is visibly four 1920×1920 fisheye quadrants; its EXIF MakerNote and 960×960 list thumbnail contain identical calibration JSON.
- `camera.getMetadata` reports `_bublMultiplex`; no embedded JPEG XMP packet was found.
- Stable boot at 4.00 V / >=1 A limit; ~0.6 A running.
- The local `BUBL0001.JPG` is a 3840×3840 four-fisheye 2×2 mosaic. An earlier 2048×2048 still was reported but was not available for this repository validation.
- THM = JPEG with Base64 factory calibration.
- Mechanical hinge pins can be removed without disturbing camera carriers.

## Strong evidence
- DM368; Linux 2.6.32.17-davinci1; BusyBox 1.22.1.
- OpenEmbedded/Yocto-like build.
- NAND/MTD/UBI.
- TI HDVICP video encode.
- FPGA configured at boot.
- older Node.js and later Scarlet generation.
- USB Ethernet gadget.
- GStreamer/RTSP and FFmpeg.

## Open
- Exact sensors, Atmel MCU, RAM/flash, Wi-Fi chip, charger/protection IC.
- UART voltage/baud/bootloader/root access.
- Successful session behavior on this unit (`cameraInExclusiveUse` followed a client-side failure that may have hidden a successful first start), options response, stream URI/protocol, and live capture behavior.
- Meaning of `_bublMultiplex`, calibration `factory:false`, and quadrant-name mapping.
- Exact fisheye model, matrix convention and quadrant rotation.
- Rootfs `/opt/bubl`, Scarlet binary, FPGA bitstream.
- Update verification/decryption mechanism.
- Open standalone controller and production-quality still/video stitcher.
