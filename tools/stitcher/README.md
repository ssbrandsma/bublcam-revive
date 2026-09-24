# Experimental stitcher

Reverse-engineering scaffold. It extracts calibration, inverse-projects equirectangular rays into each calibrated camera, supports equidistant/equisolid hypotheses and `R`/`R.T`, writes per-camera debug images and feather blends. Use Python 3.10 or newer.

```bash
python -m pip install -r tools/stitcher/requirements.txt
python tools/stitcher/bubl_stitch.py BUBL0001.JPG BUBL0001.THM -o pano.jpg --debug-dir debug
```

Try `--model equidistant|equisolid`, `--matrix R|RT`, and `--blend none|feather`. `--width` and `--height` set output size. The debug directory contains the four quadrants, four projected views, a coverage map, and both blend variants. A visually smooth result is not proof of correct lens geometry; compare overlapping source features before treating a stitch as accurate. No fixed per-camera rotations or offsets are imposed by the tool.
