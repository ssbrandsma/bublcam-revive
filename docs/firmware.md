# Firmware

Investigated firmware 2.1.1 `WUPD.BIN`:
```text
SHA-256 75aeda39d0bc3e5997485ccbb6e6359427f3a8c3d5edfc6ea537869564e80bcb
```
Outer format: SquashFS 4.0 little-endian, zlib. Observed creation time: 2015-11-10 22:39:06.

Extracted:
```text
bubl_update.bin       20,144,128 bytes
bubl_update.bin.sig   256 bytes
bubl_version          160 bytes
mnt/
```
`bubl_version`:
```text
BublCameraV1: 59617ffe8d5547d21f269da02a132fa98ffb5310
Model: bubl1
SemVersion: 2.1.1
Built: 201511102238
Timestamp: 1447195144
```

`bubl_update.bin` is 16-byte aligned, has high measured entropy, and has no obvious SquashFS/UBI/uImage/ELF/TAR header. Encryption is a **hypothesis**. The `.sig` filename and 256-byte size suggest a signature, but neither a cryptographic algorithm nor verification behavior has been established. AES and RSA are **not proven**.

## OS evidence
```text
Linux 2.6.32.17-davinci1
BusyBox 1.22.1
GCC 4.7.4
```
Build paths indicate OpenEmbedded/Yocto-like builds for `dm368_bubl-oe-linux-gnueabi`.

Older logs heavily use `node`; later logs use `scarlet`. Capture clues:
```text
/opt/bubl/scripts/image_capture.sh
/opt/bubl/scripts/video_capture.sh
FFmpeg 2.5.2
GStreamer 0.10
gstrtspserver
```
TI HDVICP/h264enc is used. FPGA logs repeatedly say `bubl_fpga_update: Application image activated`.

Best next step: dump the already-decrypted running filesystem via a legitimate local debug interface rather than attacking update crypto first. Preserve `/proc/mtd`, UBI metadata, `/opt/bubl`, `/etc`, Scarlet binary, FPGA updater/bitstream and hashes.

Do not commit original firmware unless redistribution rights are established.
