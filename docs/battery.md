# Battery and power

Original pack:
```text
JP 573442
3.7V
1560mAh
5.78Wh
2015/05/16
```
Measured envelope: ~33×43×10 mm. It consists of **two LiPo pouches in parallel**, plausibly ~780 mAh each.

Observed failing-pack behavior: around 3.76 V initially, dropping to ~3.50 V during a boot attempt, followed by shutdown.

## Bench-supply confirmation
Old pack disconnected; USB disconnected:
```text
Supply voltage: 4.00 V
0.5 A limit: boot fails/incomplete
1.0 A limit: successful boot, green LED
running: ~0.6 A at 4.0 V
```
This strongly confirms inadequate current delivery from the aged pack.

## Replacement principles
Use a normal **1S LiPo**:
- 3.7 V nominal
- 4.2 V normal maximum charge
- not a 4.35 V LiHV unless charger compatibility is proven
- adequate discharge current
- correct polarity
- suitable protection
- physical expansion clearance

A single suitable cell may replace the original parallel pair. A ~1500 mAh `103040`-class cell is a form-factor lead, not a guaranteed exact replacement.

## Bench-supply safety
Verify polarity twice, keep <=4.2 V, use current limiting, and avoid simultaneous USB charging until the power-path topology is understood.
