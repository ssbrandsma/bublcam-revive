# USB networking

Archived camera logs strongly evidence a Linux USB Ethernet gadget (`g_ether`) and `usb0` assigned `192.168.2.2`:
```text
camera: 192.168.2.2
host:   192.168.2.1
```
An older Scarlet log also records HTTP requests to `192.168.2.2:80` from `192.168.2.1`; the requests lacked `X-XSRF-Protected` and were rejected. This establishes historical reachability of the Scarlet HTTP server at the USB-side address, not a successful OSC call or a currently working Windows USB link.
On 2026-09-24, a controlled Windows before/unplug/reconnect diff with cable #3 identified one Bublcam-associated PnP node: `USB\VID_0525&PID_A4A2`, `USB Serial Device (COM4)`, class `Ports`, service `usbser`, bus-reported description `RNDIS/Ethernet Gadget`. It disappeared on unplug. Reconnection at the same hub port produced `Unknown USB Device (Device Descriptor Request Failed)`, Code 43, rather than COM4. The failure's `VID_0000&PID_0002` is a Windows placeholder, not the camera's real ID. No Bublcam network adapter, `192.168.2.1` host address, or USB route appeared in any snapshot. Product naming alone does **not** prove an active RNDIS/Ethernet link. USB ping/OSC/RTSP and targeted TCP ports were therefore **not** tested. See the [live investigation and reproducible diff](../research/usb-live-investigation-2026-09-24.md).

Next safe test, after resolving the unstable descriptor enumeration: compare Windows PnP devices before and after connection again. If an RNDIS/CDC Ethernet interface actually appears, identify its route; only then consider a host `192.168.2.1/24` address if necessary and explicitly authorized. After verifying that packets will traverse USB:
```bash
ping 192.168.2.2
curl -H "X-XSRF-Protected: 1" http://192.168.2.2/osc/info
```
If successful this avoids switching away from normal Wi-Fi.

Do not combine USB charging and bench battery emulation until the power path is understood.
