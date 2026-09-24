# Raw image format

A locally available `BUBL0001.JPG` is 3840×3840 and visibly contains four 1920×1920 fisheye views:
```text
+-------------+-------------+
| topLeft     | topRight    |
+-------------+-------------+
| bottomLeft  | bottomRight |
+-------------+-------------+
```

A separate image (`bubl0628.jpg`) listed and downloaded through firmware 2.1.1 is also 3840×3840. Visual inspection confirms four circular fisheye views in a 2×2 layout; the exact raster split is 1920×1920 per quadrant. The source's calibration JSON uses names `topLeft`, `topRight`, `bottomLeft`, and `bottomRight`, but the three inspected Bubl source repositories do not explicitly establish that those names correspond to the four raster positions. Earlier research reported a 2048×2048 four-view still (~1024×1024 views), but that file was not available for this repository validation. Do not assume one fixed capture resolution.

## Observed still metadata

**Confirmed on the downloaded `bubl0628.jpg`:** EXIF includes Make `Bubl`, Model `bubl1`, a body serial number, 3840×3840 pixel dimensions, ISO 137, f/2, 1.2 mm focal length, exposure time, white balance, and capture time. The EXIF MakerNote begins with `BUBL1` and contains `calibration=` followed by Base64 JSON. It also contains `wb_gain_r=1.500000`, `wb_gain_g=1.000000`, `wb_gain_b=1.003906`, `accel_x=61`, `accel_y=6`, `accel_z=47`, and `accel_tilt=134`. The accelerometer units and `accel_tilt` encoding are unknown. EXIF `Orientation` is `1`; the per-camera orientation matrices are separate calibration data.

The saved `camera.listImages` response included a Base64 `thumbnail` for this entry. Decoding it without conversion produced a 76,041-byte, 960×960 JPEG. Its `calibration=` JSON is identical to the original JPEG's decoded calibration. The two image files and their metadata reports remain in the private local research directory; no photograph or thumbnail is in this repository.

The decoded JSON has top-level keys `cameras`, `factory`, `timestamp`, `uuid`, and `version`. Each of four camera objects has `centre: {x, y}`, `fov`, and `orientation: {R: [[...], [...], [...]]}`. In this sample `factory` is `false` and `version` is `2015-04-15`; the meaning of `factory:false` is not established. Example FOVs from this one file are topLeft 162.907°, topRight 162.776°, bottomLeft 161.290°, and bottomRight 158.570°. These values are not universal constants. The complete calibration, including UUID and matrix values, is retained only in the private local research directory.

**API metadata versus embedded XMP:** `camera.getMetadata` reported an XMP-like object with `ProjectionType: "_bublMultiplex"`, `UsePanoramaViewer: true`, full/cropped dimensions 3840×3840, and zero crop offsets. No embedded XMP packet marker was found in the JPEG bytes. The projection label is therefore an API observation, not an XMP string extracted from this file.

## Meaning of `_bublMultiplex`

**Strong inference:** for this 3840×3840 still, the label identifies Bubl's unstitched four-view mosaic rather than a finished equirectangular panorama. That inference rests on the returned metadata and the visible 2×2 source layout. A search of [ScarletTests](https://github.com/BublTechnology/ScarletTests), [osc-client](https://github.com/BublTechnology/osc-client), and [spherical-metadata](https://github.com/BublTechnology/spherical-metadata) found no definition of `_bublMultiplex` or `bublMultiplex`; `spherical-metadata` only uses generic projection fields. The exact intended format contract, quadrant naming, lens model, and viewer behavior remain undocumented.

The matching `.THM` is itself a JPEG thumbnail (one sample: 960×960) with strings/metadata including:
```text
Bubl
bubl1
BUBL1
serial
wb_gain_r
wb_gain_g
wb_gain_b
calibration=
```

Video logs show 1920×1920 H.264 capture; it is strongly suspected to be the same four-view mosaic concept, but this needs confirmation from an actual original video.
