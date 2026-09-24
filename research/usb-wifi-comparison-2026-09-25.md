# USB versus Wi-Fi comparison attempt (2026-09-25)

This is an **incomplete Wi-Fi-versus-USB feature comparison** on one original Bublcam. A full **USB-only TCP** port scan was subsequently completed, but no full Wi-Fi TCP inventory or feature-parity verdict is available. Only `192.168.0.100` (camera Wi-Fi) and `192.168.2.2` (camera USB) were targeted; no other hosts were scanned.

Before sending camera traffic, Windows route selection was checked. Once Wi-Fi DHCP completed, `192.168.0.100` used source `192.168.0.10` via `WiFi` / ifIndex 19 and on-link `192.168.0.0/24`. The Bublcam RNDIS adapter, `Ethernet 3` / ifIndex 69, had lost its prior ActiveStore-only address; `192.168.2.1/24` was temporarily re-added only to that adapter. `192.168.2.2` then selected source `192.168.2.1` and the USB on-link `192.168.2.0/24` route. Initial Wi-Fi ping: 10/10 replies, 7–126 ms, mean 49 ms. One short USB check after address restoration: 3/3 replies with displayed times below 1 ms. These tiny samples are not throughput or stability benchmarks.

A bounded-concurrency full TCP 1–65535 scan of those two IPs was **attempted but aborted early** when the Windows scan tool reported Winsock error 10053 on the USB address. There is no complete TCP result for either interface. The USB route/IP disappeared transiently afterward. After restoring the USB address, a gentler USB-only scan of TCP ports 1–100 at at most five connections per second completed: port 80 open; 99 ports reported closed/refused. The link still answered three pings immediately afterward. This result says nothing about ports 101–65535 or about Wi-Fi ports.

A later ordinary USB OSC state request timed out, and the USB ping/route again disappeared transiently, while Wi-Fi `/osc/state` continued to respond. Windows System logged `Microsoft-Windows-NDIS` event 10400 for `USB Ethernet/RNDIS Gadget`: the network driver reset the interface after detecting that the device stopped responding to commands. This is evidence of a driver–gadget communication stall; its root cause remains unknown. The earlier [USB investigation](../docs/usb-network.md) did successfully reach USB OSC and RTSP control on 2026-09-24, so this timeout is **not** proof of a USB-only API limitation.

The user later reported that the camera had entered sleep mode during the failed scan attempts. This is plausible but does not, by itself, prove the root cause of the Windows NDIS reset. After the camera was awake and the USB host address/route were restored, the full USB-only scan described below completed without a link drop.

## Completed full USB TCP scan, camera awake

With `USB\VID_0525&PID_A4A2` PnP OK, the RNDIS adapter Up, and `Find-NetRoute` selecting source `192.168.2.1` on the USB `192.168.2.0/24` route, a SYN-only Nmap scan of **all TCP ports 1–65535** on **only** `192.168.2.2` completed in 219.46 seconds. It used `-sS -Pn -n -p- --max-retries 0 --max-rtt-timeout 1000ms --initial-rtt-timeout 500ms --max-parallelism 8 --max-rate 300 --host-timeout 8m`; no version, vulnerability, or authentication scripts were run.

| TCP result while camera idle | Count |
|---|---:|
| Open: `80/tcp` | 1 |
| Closed (reset) on first pass | 65,529 |
| No response on first pass | 5 |

The five initially nonresponsive ports (`16848`, `23867`, `30909`, `33657`, `39887`) were separately rechecked with up to three retries at at most five probes per second. **All five returned closed.** Thus the completed scan found **only TCP/80 open at idle and 65,534 closed ports**. Nmap labeled 80 `http` by conventional port name; HTTP/OSC behavior was established separately, not by a version-detection probe. The USB route remained on the RNDIS adapter and two post-scan pings succeeded. Raw Nmap output is retained privately under `bubl_research/network_comparison_20260925/tcp-usb-full-awake.*` and `tcp-usb-five-recheck.*`; no camera MAC address is published.

This idle scan does **not** contradict the earlier successful RTSP `OPTIONS`/`DESCRIBE` on TCP/8554: that service was observed after a stream command started and was not expected to remain open while idle. The scan does not test UDP or prove that the same port states apply on Wi-Fi.

No UDP scan, session-parity test, same-image download comparison, cross-interface RTSP test, or RTP frame reception was completed in this comparison. No camera session, stream, capture, configuration change, or media deletion was initiated by the 2026-09-25 scans. USB's prior OSC/RTSP success establishes capability, but sustained feature parity and long-duration stability remain unverified.
