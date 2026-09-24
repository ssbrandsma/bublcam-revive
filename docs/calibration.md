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

In that sample `bottomRight` used identity `R`. It may be the orientation reference, but that interpretation still needs experimental validation. Example bottom-right centre: x≈0.474108, y≈0.492964.

White-balance metadata included values such as:
```text
wb_gain_r=1.453125
wb_gain_g=1.000000
wb_gain_b=1.027344
```

Do **not** hard-code these values; calibration is per device/capture.

## Open geometry questions
- exact fisheye projection (equidistant/equisolid/other)
- whether `R` or `R.T` maps world→camera
- coordinate axis/sign convention
- 90/180/270° rotation/mirroring of source quadrants
- whether additional distortion calibration exists

Use `tools/calibration/extract_calibration.py`.
