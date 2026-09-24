# Early experimental stitcher scaffold

This included script predates the separately reported successful 545-image stitcher. It has not been replaced with that mature implementation; its current defaults and focal-scale rule do **not** represent the later [feature-supported geometry](../../docs/stitching.md). Use this scaffold for historical experiments only, not as the documented 545/545 batch method.

Reverse-engineering scaffold. It extracts calibration, inverse-projects equirectangular rays into each calibrated camera, supports equidistant/equisolid hypotheses and `R`/`R.T`, writes per-camera debug images and feather blends. Use Python 3.10 or newer.

```bash
python -m pip install -r tools/stitcher/requirements.txt
python tools/stitcher/bubl_stitch.py BUBL0001.JPG BUBL0001.THM -o pano.jpg --debug-dir debug
```

Try `--model equidistant|equisolid`, `--matrix R|RT`, and `--blend none|feather`. `--width` and `--height` set output size. The debug directory contains the four quadrants, four projected views, a coverage map, and both blend variants. A visually smooth result is not proof of correct lens geometry; compare overlapping source features before treating a stitch as accurate. No fixed per-camera rotations or offsets are imposed by the tool.

`--rotations 0,90,180,270` rotates the `topLeft`, `topRight`, `bottomLeft`, and `bottomRight` source quadrants clockwise by the corresponding number of degrees. The tool also transforms each quadrant's calibrated optical centre. The default is `0,0,0,0`. This control was useful when quadrant mapping was uncertain; later feature tests across nine frames support zero extra turns for the investigated collection.

See the [private-image experiment summary](../../research/stitching-bubl0628.md) for the four model/matrix tests and a systematic rotation sweep. The image and generated panoramas are not included in the repository.
