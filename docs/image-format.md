# Raw image format

A locally available `BUBL0001.JPG` is 3840×3840 and visibly contains four 1920×1920 fisheye views:
```text
+-------------+-------------+
| topLeft     | topRight    |
+-------------+-------------+
| bottomLeft  | bottomRight |
+-------------+-------------+
```

A separate image listed and downloaded through firmware 2.1.1 was also 3840×3840. Its four-view layout has not yet been checked pixel by pixel. Earlier research reported a 2048×2048 four-view still (~1024×1024 views), but that file was not available for this repository validation. Do not assume one fixed capture resolution.

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
