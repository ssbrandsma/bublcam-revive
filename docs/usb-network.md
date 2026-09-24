# USB networking

Logs suggest a USB Ethernet gadget (`g_ether`):
```text
camera: 192.168.2.2
host:   192.168.2.1
```
Not yet re-verified on the current unit.

Proposed test: boot normally, connect USB data, look for RNDIS/CDC Ethernet, configure host `192.168.2.1/24` if needed, then:
```bash
ping 192.168.2.2
curl -H "X-XSRF-Protected: 1" http://192.168.2.2/osc/info
```
If successful this avoids switching away from normal Wi-Fi.

Do not combine USB charging and bench battery emulation until the power path is understood.
