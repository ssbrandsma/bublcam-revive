# Experimental stitching of `bubl0628.jpg`

All media and generated panoramas in this experiment remain in the private local `bubl_research/downloads/` directory. Nothing in this repository includes the source photograph, thumbnail, decoded UUID, or visual output.

## Inputs and method

- Original 3840×3840 JPEG, split into four 1920×1920 quadrants.
- Exact 960×960 thumbnail decoded from the preserved `camera.listImages` response. Its calibration JSON matches the original JPEG's calibration.
- Existing experimental `tools/stitcher/bubl_stitch.py`, output size 1024×512, with per-camera projections, coverage map, no-blend and feather-blended outputs for every tested combination.
- Four initial combinations: `equidistant/R`, `equidistant/R.T`, `equisolid/R`, `equisolid/R.T`, all with `--rotations 0,0,0,0`.

The script now accepts `--rotations` as four clockwise angles for the named source quadrants (0, 90, 180, or 270 degrees) and transforms the corresponding optical centres. This exposes the orientation uncertainty without imposing one correction as fact.

## Four initial combinations

| Model / matrix | Approximate output coverage | Visual observation |
|---|---:|---|
| Equidistant / `R` | 67.9% | Large black uncovered region; repeated/misaligned ground and people |
| Equidistant / `R.T` | 100% | No empty region, but people and horizon appear in conflicting orientations and overlap badly |
| Equisolid / `R` | 67.8% | Same major gap and overlap failure as equidistant/`R` |
| Equisolid / `R.T` | 100% | Similar coverage to equidistant/`R.T`; source features still fail to align |

Coverage is the fraction of output pixels marked valid by at least one calibrated projection. It does not imply that those pixels form a correct panorama; dark source borders may also remain inside a valid projection.

## Systematic 90-degree rotation sweep

An offline diagnostic script evaluated all `4^4 = 256` quadrant-rotation assignments for each model/matrix combination: 1,024 candidates total at 512×256. For each pair of overlapping projected views, it computed mean absolute grayscale disagreement after removing a median brightness offset, plus half the mean absolute edge-strength disagreement. It weighted pair scores by overlap pixel count. This is an exploratory ranking, not a calibrated accuracy metric: sky can match sky cheaply, exposure/parallax differ, and the assumed camera-to-quadrant assignment may itself be wrong.

| Model / matrix | Lowest-score rotations (topLeft, topRight, bottomLeft, bottomRight) | Score, unrotated → candidate | Candidate coverage |
|---|---|---:|---:|
| Equidistant / `R` | `90,270,270,270` | 0.2064 → 0.1585 | 68.3% |
| Equidistant / `R.T` | `90,180,270,270` | 0.1662 → 0.1418 | 100% |
| Equisolid / `R` | `90,270,270,270` | 0.2076 → 0.1600 | 68.3% |
| Equisolid / `R.T` | `270,90,90,180` | 0.1649 → 0.1423 | 100% |

Full diagnostic scores and the top candidate's projections, coverage, and both blend modes are retained locally. A close alternative for equisolid/`R.T` (`90,180,270,270`, score 0.1433) was also rendered. Visual inspection shows that none of these candidates aligns the same bench, people, road, and horizon consistently across overlaps. The `R` candidates still have large holes; `R.T` candidates retain obvious seam and orientation errors. No rotations or offsets have been hard-coded as a default.

## Open geometry questions

The raster positions may not map directly to calibration keys; `R` may require an additional coordinate-frame transform; per-camera pixel handedness, 90-degree orientation, lens projection, and distortion may differ from the scaffold's assumptions. A useful next experiment is to mark matched features in adjacent raw quadrants, test camera-key permutations and coordinate conventions, then compare reprojection error on those correspondences. A smooth blended image alone is insufficient evidence of correct geometry.
