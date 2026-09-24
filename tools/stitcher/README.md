# Bublcam panorama stitcher

`bubl_stitch.py` converts one Bublcam four-fisheye JPEG and its matching THM
into a 2:1 equirectangular JPEG. It reads the factory calibration from **each**
THM; no example calibration values are built into the program.

This is an independently reconstructed geometric stitcher, not the original Bubl algorithm. Keep private photos and calibration outside this public repository.

## Install and run

```powershell
python -m pip install -r tools/stitcher/requirements.txt
python tools/stitcher/bubl_stitch.py PATH/TO/BUBL0001.JPG PATH/TO/BUBL0001.THM `
  -o PATH/TO/PRIVATE_OUTPUT/BUBL0001_equirect.jpg --turns 0,0,0,0
```

Run these commands from the repository root. Omit `--turns` to infer turns from SIFT matches; explicit zero turns are the tested default for the investigated collection and avoid the extra matching step. `--debug-dir` writes image-derived diagnostics, and `--verbose` prints full calibration, so keep both outputs private.

The default output is 4096×2048. Use `--width` and `--height` for another 2:1
size. `--blend none` selects the camera with the strongest centre weight at
each pixel; `--blend feather` (the default) blends overlapping samples.
`--model equidistant`, `--model equisolid`, and `--model stereographic` permit
projection comparisons. `--verbose` prints the decoded calibration. Use
`--turns 0,0,0,0` to set source orientations explicitly; otherwise matched
image features infer the four quarter-turns.

## View the panorama

Open [viewer.html](viewer.html) in a browser and use **Open panorama** to choose a local stitched image. It attempts to load `BUBL0001_equirect.jpg` from the viewer's folder by default, but no private image is bundled. Drag to look around,
scroll to zoom, or use **Open panorama** to choose another 2:1 image. The
viewer uses local WebGL and does not load external libraries or upload images.

If the browser restricts loading images from a `file:` page, serve this folder
locally:

```powershell
python -m http.server 8765 --bind 127.0.0.1 --directory tools/stitcher
```

Then open <http://127.0.0.1:8765/viewer.html>.

To stitch the entire `sd_contents/dcim` folder, run:

```powershell
python tools/stitcher/stitch_all.py --input-dir PATH/TO/DCIM --output-dir PATH/TO/PRIVATE_OUTPUT
```

This writes one 4096×2048 JPEG per JPG/THM pair to the selected output directory and records
every source and result in `batch_report.csv` there. Reruns skip existing
outputs. The batch uses three workers by default; `--workers`, `--width`,
`--height`, `--input-dir`, and `--output-dir` can be set. The batch reads each
THM separately and uses the equisolid, camera-to-world, zero-turn geometry
validated across the three calibration IDs in this collection.

## Format and geometry

The JPEG is a square 2×2 mosaic ordered `topLeft`, `topRight`, `bottomLeft`,
`bottomRight`. Each quadrant is one fisheye image. The supplied BUBL0001.JPG
is **3840×3840**, with 1920×1920 quadrants, despite the 2048×2048 size in the
initial description. Quadrant size is determined from the actual JPEG.

The THM is a JPEG thumbnail containing `calibration=` followed by Base64 JSON
in its binary metadata. The parser scans raw bytes for that marker, decodes
the Base64 value, and validates that all four cameras are present. Each camera
provides full FOV, normalized optical centre, and a 3×3 orientation matrix.

For each output direction, inverse mapping rotates the world ray into each
camera, computes the angle `theta` from its optical axis, and maps it to the
source quadrant. FOV is interpreted as the **full angular diameter**. Its
half-angle corresponds to a circle whose radius is the distance from the
calibrated optical centre to the nearest quadrant border. This radius rule is
an inferred scale because the metadata has no independent focal length or
image-circle radius.

The default equisolid model uses `r = 2 f sin(theta/2)`, with `f` chosen so
`theta = FOV/2` reaches that radius. Equidistant uses `r = f theta` with the
same boundary condition. Sampling is bilinear through OpenCV `remap`.
Directions outside a camera's FOV or image bounds receive no contribution.

`R` is interpreted as **camera-to-world**: `world = R × camera`, hence inverse
projection uses `camera = R.T × world`. The bottomRight matrix is identity and
its optical axis points toward the zenith in the selected world coordinates.
The panorama uses longitude around the vertical world axis and latitude from
the equator. On the supplied images, source quadrant pixel axes need **zero
quarter-turns**. `--convention world-to-camera` is available to reproduce the
alternative interpretation.

Feather weight is `(1 - (theta / (FOV/2))²)²` inside each camera. Weighted
samples are normalized per output pixel. This gives central image regions
greater weight and smoothly reduces camera contributions near the lens edge.

## Diagnostics and findings

`--debug-dir debug` writes `quadrants.jpg`, `coverage.png`, each
`camera_<name>.png`, `panorama_no_blend.jpg`, `panorama_feather.jpg`, and
`settings.json`. Coverage colors add together when cameras overlap. Black
means no camera covers that direction. Each single-camera projection is black
outside its coverage.

Source turns were checked by matching SIFT features between raw quadrants.
Each matched source point was unprojected into a 3D ray under all four
quarter-turns; matching rays should differ by only a few degrees, allowing
for parallax. On BUBL0001, all four zero-turn orientations maximize feature
agreement. With a 5° acceptance threshold plus a smaller bonus within 2°,
the agreement scores were:

| Model | `R` camera-to-world | `R` world-to-camera |
| --- | ---: | ---: |
| Equidistant | 163.75 | 112.00 |
| Equisolid | **266.25** | 138.50 |
| Stereographic | 6.25 | 11.50 |

To reproduce the six model/convention scores for a local pair without writing an image:

```powershell
python tools/stitcher/research/validate_geometry.py PATH/TO/BUBL0001.JPG PATH/TO/BUBL0001.THM
```

The tool prints inferred quarter-turns and scores, not source pixels or calibration. Scores depend on SIFT/OpenCV behavior and the particular image.

This supports equisolid and camera-to-world for the supplied calibration.
The generated BUBL0001 panorama was visually inspected: people and the
building are upright, the awning and table connect plausibly across views,
and the sky is continuous. BUBL0002 independently inferred zero turns and
also produced a coherent indoor panorama. Visible double images remain near
close objects, especially cups and people near overlap areas; the four lens
centres are physically separated, so one rotation-only spherical mapping
cannot align every depth. Unknown lens distortion beyond the simple fisheye
model may also contribute. The FOV-to-radius interpretation remains an
assumption because no distortion or focal-length fields were found in this
THM calibration.

## Full-folder batch result

The separately investigated collection contained 545 JPEG mosaics, all 3840×3840, each with a
matching THM. There are three camera calibration UUIDs; one UUID has two
closely related camera calibration variants. Nine sample frames spanning the
three IDs all inferred zero source quarter-turns. Panoramas from all three
groups were visually checked (BUBL0001, BUBL0014, BUBL0275).

The separate project's `stitch_all.py` run reportedly rendered all 545 files at 4096×2048 into its private output directory.
The final report records 545 successes and no failures. A separate verification
confirmed every source stem has one output and every output JPEG is readable
at the expected dimensions. The stitched JPEGs use about 1.03 GiB total.
