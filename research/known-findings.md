# Findings / backlog

## Confirmed live
- Firmware 2.1.1; model bubl1.
- API at 192.168.0.100:80.
- `X-XSRF-Protected: 1` works.
- Altera version 512 reported. Atmel version was `"1"` in one supplied response and `"2.2"` in a later live response; why it changed is unknown.
- Firmware 2.1.1 listed 545 files on the tested storage and served one 3840×3840 JPEG through the Bubl image endpoint.
- The downloaded JPEG is visibly four 1920×1920 fisheye quadrants; its EXIF MakerNote and 960×960 list thumbnail contain identical calibration JSON.
- `camera.getMetadata` reports `_bublMultiplex`; no embedded JPEG XMP packet was found.
- A controlled session returned ID `"0"`; the client closed that same ID and confirmed idle state. Live `getOptions` returned values for 41 non-sensitive names.
- One new 3840×3840 JPEG and one short 1920×1920 MP4 were captured; both show a 2×2 four-fisheye layout. The MP4 contains H.264 and 16 kHz mono AAC.
- `_bublStream` returned a dynamic RTSP endpoint on port 8554. RTSP `OPTIONS` and `DESCRIBE` succeeded; SDP announced H.264 video and MP4A-LATM audio. The stream was stopped and reached `done`.
- Stable boot at 4.00 V / >=1 A limit; ~0.6 A running.
- The local `BUBL0001.JPG` is a 3840×3840 four-fisheye 2×2 mosaic. The integrated stitcher rendered it at 4096×2048, reproduced the 266.25 equisolid/camera-to-world SIFT score and zero turns, and completed a one-pair batch smoke test. A separate investigation reports all 545 JPGs in its SD-card collection are 3840×3840 with matching THMs and 545 readable 4096×2048 panoramas. The complete batch has not been independently rerun here.
- The reported collection contains three calibration UUIDs, one with two closely related variants; use the matching THM for each image.
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
- Archived logs explicitly show `g_ether` ready and Avahi on `usb0` at `192.168.2.2`; another historical log records Scarlet HTTP requests from `192.168.2.1` to `.2.2:80` rejected for missing the required header. The live Windows attachment on 2026-09-24 showed no camera-attributable USB device or USB route. USB networking remains unverified live.
- FFmpeg in firmware logs; the live RTSP server identifies itself as GStreamer.
- Matched-feature tests reported across nine frames strongly favor camera-to-world `R`, zero extra quadrant turns, and equisolid-angle over equidistant or stereographic. See [stitching findings](../docs/stitching.md).

## Open
- Exact sensors, Atmel MCU, RAM/flash, Wi-Fi chip, charger/protection IC.
- UART voltage/baud/bootloader/root access.
- Whether the earlier failed PowerShell client actually opened the session; its response was not captured.
- Live RTP frame decoding, nominal stream frame rate, and long-duration stability.
- Meaning of `_bublMultiplex`, calibration `factory:false`, and quadrant-name mapping.
- Exact proprietary fisheye law and original Bubl stitching algorithm; focal-scale/image-circle assumption; residual radial distortion and depth-dependent parallax correction.
- Rootfs `/opt/bubl`, Scarlet binary, FPGA bitstream.
- Update verification/decryption mechanism.
- Open standalone controller and production-quality still/video stitcher.
