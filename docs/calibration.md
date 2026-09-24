# Factory calibration

The THM contains literal `calibration=` followed by Base64 JSON. In the downloaded `bubl0628.jpg` and its exact list thumbnail, the same JSON also appears in each JPEG's EXIF MakerNote. The two decoded objects compare equal. A THM is therefore not the only possible source of calibration for this firmware/media pair.

Decoded structure includes per camera:
- `fov`
- `orientation.R` (3×3 matrix)
- normalized `centre.x`, `centre.y`

and global fields such as `version: "2015-04-15"` and `factory: true`.

The `bubl0628` calibration instead has `factory: false`. Both values are observed; the flag's precise meaning is unknown. The complete per-image object also includes `timestamp` and `uuid`. Keep the UUID and image metadata private unless the owner approves publication.

One real sample gave approximately:
| camera | FOV |
|---|---:|
| topLeft | 159.84° |
| topRight | 162.59° |
| bottomLeft | 159.73° |
| bottomRight | 158.45° |

In that sample `bottomRight` used identity `R`. Subsequent feature matching strongly supports treating it as the orientation reference in that calibration coordinate system; it does not establish the original proprietary convention. Example bottom-right centre: x≈0.474108, y≈0.492964.

White-balance metadata included values such as:
```text
wb_gain_r=1.453125
wb_gain_g=1.000000
wb_gain_b=1.027344
```

Do **not** hard-code these values; calibration is per device/capture.

## Geometry status

A separate investigation reported 545 matching JPG/THM pairs, three calibration UUIDs, and one UUID with two closely related variants. Calibration must therefore be read from the matching THM per image, never treated as one global setting. SIFT feature correspondences strongly support `R` as camera-to-world, `R.T` for inverse world-to-camera mapping, zero extra source quarter-turns, and equisolid-angle as the best of three tested simple lens models. See [stitching method and evidence](stitching.md).

The exact proprietary projection, focal scale/image-circle radius interpretation, higher-order distortion, and parallax correction remain unresolved. The working focal-scale rule uses the nearest quadrant border as an inferred radius, not a known calibration field. The separate feature-validation implementation was not yet available here for independent rerun.

Use `tools/calibration/extract_calibration.py`.
