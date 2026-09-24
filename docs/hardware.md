# Hardware

## Strongly evidenced components
- TI DaVinci **DM368** application processor.
- Altera **Cyclone IV** FPGA.
- Four ~5 MP fisheye camera modules in a multi-direction geometry.
- Embedded NAND/MTD/UBI storage.
- Wi-Fi, microphone/audio path, microSD, 1/4"-20 tripod mount.

Live `/osc/info` reported `_bublAtmelVersion: "1"` in one supplied response and `"2.2"` in a later response from the same serial and firmware; `_bublAlteraVersion` was `512` in both. These are API component version fields. Exact Atmel part number and why the value changed are unknown.

## PCB markings
One observed board is marked approximately:
```text
03-0027-01-R3V0
COVELOZ CONSULTING INC.
```
Confirm spelling from sharper macro photography before treating it as definitive.

## Debug/test pads
Visible labels:
```text
RX TX GND
SDA SCL GND
3.3V 2.5V 1.8V 1.2V
```

## Flash evidence
Research from logs suggests:
- MTD3 `boot`: ~52 MiB
- MTD4 `userdata`: ~32 MiB
- NAND physical erase block: 128 KiB
- UBI logical erase block: ~124 KiB
- page size: 2048 bytes
- likely volumes: `ubootscr`, `kernel`, `root`, `userdata`

Confirm on live hardware with `cat /proc/mtd` and `ubinfo -a`.

## Mechanical
The four aluminium camera/lens frame pieces hinge on tiny spring/roll pins, approximately 0.8 mm on the inspected unit. Removing these lets the assembly unfold without disturbing calibrated camera carriers.

## Power
Successful bench test: 4.00 V, 1 A current limit; running current ~0.6 A. A 0.5 A limit was insufficient for boot.
