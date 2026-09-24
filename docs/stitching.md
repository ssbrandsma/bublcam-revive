# Independent geometric stitching

The included [independently developed stitcher](../tools/stitcher/README.md) produces usable 2:1 equirectangular panoramas from Bublcam multiplex JPEGs using each image's matching THM calibration. This is **not** a recovery or bit-exact recreation of Bubl's proprietary stitching algorithm. The separate project's full 545-image run has not been independently repeated in this workspace; the integrated code was verified here on the local `BUBL0001` pair, including a 4096×2048 output and a one-pair batch smoke test.

## Input and calibration

The reported SD-card collection contains 545 JPG/THM pairs. All 545 JPGs were measured as 3840×3840, each split into four 1920×1920 fisheye views in top-left, top-right, bottom-left, bottom-right raster order. This confirms the format for that collection, not every possible firmware mode. Implementations should derive quadrant dimensions from the actual input image.

Each THM is a JPEG thumbnail containing `calibration=` followed by Base64 JSON in binary metadata. Each camera entry supplies normalized optical `centre.x`/`centre.y`, `fov`, and a 3×3 `orientation.R`. Read the matching THM for **each** JPG: the reported collection has three calibration UUIDs, one with two closely related variants. At least some original JPGs also carry matching calibration in EXIF MakerNote. Do not hard-code sample centres, FOVs, matrices, or one calibration for the whole collection.

## Geometric interpretation

Feature-correspondence tests strongly support treating `R` as camera-to-world, so inverse mapping uses `camera_ray = R.T × world_ray`. In the investigated calibration, `bottomRight` has identity `R` and acts as its orientation reference. SIFT matching on nine frames spanning all three calibration IDs supported **zero extra quarter-turns** for all four raster quadrants. These are independently validated interpretations of the metadata, not claims found in original Bubl source.

Three simple fisheye models were compared by unprojecting matched SIFT points and scoring their angular agreement in a common world frame. For `BUBL0001`, the reported scores were:

| Model | Camera-to-world `R` | World-to-camera `R` |
|---|---:|---:|
| Equidistant | 163.75 | 112.00 |
| Equisolid-angle | 266.25 | 138.50 |
| Stereographic | 6.25 | 11.50 |

Higher scores indicated better agreement, including a preference for matched rays within about 5° and then 2°. The integrated [validation tool](../tools/stitcher/research/validate_geometry.py) reproduced all six reported scores on the local `BUBL0001` pair; it wraps the stitcher's SIFT scoring method. Equisolid-angle is the best **tested simple approximation**, not a proven exact lens law. Its radial model is `r = 2f sin(θ/2)`.

The working implementation interprets stored FOV as full angular diameter, with `θmax = FOV/2`, and estimates focal scale by setting the image-circle radius to the distance from optical centre to the nearest quadrant border: `f = radius / (2 sin(θmax/2))`. This radius rule is an **inferred assumption**, not a measured image-circle boundary. It is a leading candidate for residual geometry error.

## Projection and blending

For each output equirectangular pixel, the stitcher constructs a world ray; for each camera it applies `R.T`, rejects rays beyond `FOV/2`, maps the angle through the selected fisheye law, adds the calibrated optical centre, and bilinearly samples the corresponding source quadrant. The normal output is 4096×2048, though other dimensions are possible. Default feather blending weights a camera at angle `θ` by `w = (1 - (θ/θmax)^2)^2` inside its FOV, then normalizes all contributing weights. A no-blend mode exposes geometric seams for diagnosis.

The reported batch run produced 545 panoramas, 545 successes and zero failures, each verified readable at 4096×2048; total output was about 1.03 GiB. Samples from all three calibration groups, including around `BUBL0001`, `BUBL0014`, and `BUBL0275`, were visually coherent. This verifies the separate project's batch outcome as reported, not its exact geometry or absence of artifacts.

## Limits and next validation

Four physically separated lenses do not share an optical centre. Nearby people, cups, and tables can therefore double in overlaps even with correct rotational calibration. Feather blending softens seams but cannot remove depth-dependent parallax. Residual mismatch may also reflect the inferred focal scale or non-ideal radial distortion. A small empirical correction such as `r_corrected = r(1 + k1 r² + k2 r⁴)` is a research option; no coefficients have been measured or adopted.

The useful next tests are feature-based optimization of FOV-to-radius scale, cross-image/cross-calibration validation of any radial correction, and separation of parallax from optical-model error. Seam optimization or optical flow could then improve close-object rendering. Further brute-force quarter-turn searches are low priority unless new evidence contradicts the nine-frame result. Preserve the simple equisolid model as a reproducible baseline.

The earlier [single-image exploratory sweep](../research/stitching-bubl0628.md) used a different pixel-disagreement score and an older scaffold; it did not establish geometry. Its apparent preference for rotated candidates is superseded by direct matched-feature evidence, but remains useful as a record of why visual/pixel similarity alone can mislead.

## Included implementation and verification

`tools/stitcher/` now contains the separate project's mature `bubl_stitch.py`, `stitch_all.py`, `requirements.txt`, `viewer.html`, and adapted README. The stitcher processes output in row strips, uses OpenCV bilinear remapping, and supports selectable lens models, matrix conventions, turns, blend modes, sizes, and debug views. The batch runner pairs uppercase `.JPG`/`.THM` files and writes `batch_report.csv`; its default is equisolid, camera-to-world, zero-turn geometry. The local WebGL viewer has no external library or upload. A small [validation wrapper](../tools/stitcher/research/validate_geometry.py) prints six geometry scores without writing media.

In this workspace, the integrated code rendered the local `BUBL0001` pair at 4096×2048, inferred `0/0/0/0` turns with score 266.25, and completed a one-pair 1024×512 batch run with `ok` in the CSV. The output was visually coherent but had close-object double images. No private photograph, thumbnail, full calibration, or generated panorama was copied into Git. The complete 545-image dataset was not available here to rerun the full batch claim.
