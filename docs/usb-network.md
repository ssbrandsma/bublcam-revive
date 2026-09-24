# USB networking

Archived camera logs strongly evidence a Linux USB Ethernet gadget (`g_ether`) and `usb0` assigned `192.168.2.2`:
```text
camera: 192.168.2.2
host:   192.168.2.1
```
An older Scarlet log also records HTTP requests to `192.168.2.2:80` from `192.168.2.1`; the requests lacked `X-XSRF-Protected` and were rejected. This establishes historical reachability of the Scarlet HTTP server at the USB-side address, not a successful OSC call or a currently working Windows USB link.
On 2026-09-24, with the camera reported connected by USB to a Windows laptop, no present USB device, COM port, or network adapter could be attributed to the camera. The host had no `192.168.2.1` address and no route to `192.168.2.2` through USB. The camera remained reachable over Wi-Fi, but USB ping/OSC/RTSP and targeted USB TCP ports were **not** tested because traffic would not have used a verified USB link. Exact Bublcam USB VID/PID and interface descriptors remain unknown. See the [live investigation and reproducible checks](../research/usb-live-investigation-2026-09-24.md).

Next safe test: confirm a data-capable cable and camera data port, then compare Windows PnP devices before and after connection. If an RNDIS/CDC Ethernet interface actually appears, identify its VID/PID and route; only then consider a host `192.168.2.1/24` address if necessary and explicitly authorized. After verifying that packets will traverse USB:
```bash
ping 192.168.2.2
curl -H "X-XSRF-Protected: 1" http://192.168.2.2/osc/info
```
If successful this avoids switching away from normal Wi-Fi.

Do not combine USB charging and bench battery emulation until the power path is understood.
