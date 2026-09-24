# Bublcam Revive

Bublcam was a four-lens consumer 360° camera. This project preserves knowledge about the original hardware and develops independent tools so owners can use their cameras as the original app and cloud age out. It is an independent preservation project, not an official Bubl release.

The current work is based on physical inspection of one Bublcam, local media and logs, live API responses from firmware 2.1.1, and [BublTechnology's public repositories](#original-bubl-sources). Measurements and calibration values are examples from that camera, not specifications for every unit.

## Current status

| Area | Status |
|---|---|
| Power and battery | Original pack inspected; one camera booted on a current-limited bench supply |
| Wi-Fi and OSC API | `/osc/info`, `/osc/state`, image list, metadata and download confirmed on firmware 2.1.1 |
| Still capture | Documented in original client; fresh capture on this unit still pending |
| Raw still and THM | Four-view JPEG layout and THM calibration decoded from local samples |
| Open-source stitcher | Experimental; lens model and orientation convention unresolved |
| Live streaming and video | Command formats documented; live protocol and capture unverified on this unit |
| USB networking | Suggested by logs; not verified on this unit |
| UART / I²C | Pads identified; voltage and access unverified |
| Root filesystem / FPGA | Filesystem not dumped; FPGA identified, bitstream not extracted |

## Start here

If you have a camera, read [battery and power](docs/battery.md) before replacing the battery and [networking](docs/network.md) before connecting. Once the camera is on its Wi-Fi network, this read-only request identifies it:

```sh
curl -H "X-XSRF-Protected: 1" http://192.168.0.100/osc/info
```

The included probe uses only documented read-only endpoints:

```sh
python tools/api/bubl_api.py info
python tools/api/bubl_api.py state
```

For a local `.THM` file, extract the embedded calibration JSON:

```sh
python tools/calibration/extract_calibration.py YOUR_FILE.THM -o calibration.json
```

For experimental stitching, install [the stitcher requirements](tools/stitcher/requirements.txt) and consult [its usage notes](tools/stitcher/README.md). No private sample media is bundled.

## Observed camera and media

| Item | Observation |
|---|---|
| Camera | Bubl `bubl1`, tested serial `f4b85e1a4e97` |
| Firmware | `2.1.1` |
| Wi-Fi API | `192.168.0.100:80`; `X-XSRF-Protected: 1` required |
| API component versions | `_bublAlteraVersion: 512`; `_bublAtmelVersion` was `"1"` in one supplied response and `"2.2"` in a later live response, so its meaning and change need investigation |
| Original battery label | JP 573442, 3.7 V, 1560 mAh, 5.78 Wh |
| Tested local raw still | `BUBL0001.JPG` is 3840×3840 with four 1920×1920 fisheye views |
| Earlier size report | A 2048×2048 four-view raw still was reported in earlier research, but that file was not available for this repository validation |
| Later camera image | API listed and downloaded a separate 3840×3840 JPEG; its layout has not been independently checked |
| THM | JPEG thumbnail carrying `calibration=` followed by Base64 JSON |

The original pack in the inspected camera consists of two LiPo pouches in parallel. With that pack disconnected, a 4.00 V supply limited to 0.5 A did not complete boot; a 1.0 A limit did. Running draw was approximately 0.6 A. These are observations from one setup; see [battery and power](docs/battery.md).

## Documentation

| Topic | Page |
|---|---|
| Hardware and disassembly | [Hardware](docs/hardware.md), [disassembly](docs/disassembly.md), [battery](docs/battery.md) |
| Protocol and connectivity | [Network](docs/network.md), [OSC API](docs/api.md), [streaming](docs/streaming.md), [USB networking](docs/usb-network.md) |
| Imaging | [Raw format](docs/image-format.md), [calibration](docs/calibration.md), [stitcher](tools/stitcher/README.md) |
| Firmware and debug | [Firmware](docs/firmware.md), [UART / I²C](docs/uart.md) |
| Project | [Findings and open questions](research/known-findings.md), [contributing](CONTRIBUTING.md) |

Findings in the docs use **Confirmed** for direct observations or verified source code, **Strongly evidenced** for conclusions supported by multiple clues, and **Hypothesis** for ideas that still need testing.

## Original Bubl sources

The original organization's [ScarletTests](https://github.com/BublTechnology/ScarletTests), [osc-client](https://github.com/BublTechnology/osc-client), and [spherical-metadata](https://github.com/BublTechnology/spherical-metadata) repositories are useful primary references for API shapes and media conventions. Their source remains in those repositories; this project does not vendor it.

## Preservation and rights

Keep a backup of your SD card and do not run firmware update, erase, reset, or undocumented write operations as discovery steps. Check UART voltage before attaching an adapter, and avoid disturbing lens alignment.

Repository code is [MIT licensed](LICENSE). Independently authored documentation is [CC BY 4.0](LICENSE-DOCS). Bubl firmware, software, photographs, trademarks, and third-party material retain their respective owners' rights. Do not publish personal captures, unique device credentials, or original firmware binaries here.
