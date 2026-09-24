# USB connection investigation, 2026-09-24

**Outcome:** The camera was reported connected to this Windows laptop by USB, but no present USB device or interface could be unambiguously attributed to the Bublcam. The laptop had no Bublcam USB network adapter, COM port, or route to the historical USB subnet. The camera itself remained reachable through its separate Wi-Fi connection. This is a negative observation for this host/cable/connection at this moment, **not** proof that the camera lacks USB gadget capability.

No USB driver, camera setting, Windows network setting, firmware, or gadget configuration was changed. No camera reboot, USB stream, photo, recording, credential attempt, or broad port scan occurred. Raw camera media and device serials are not included here.

## Reproducible read-only checks

The following commands were run in PowerShell with the camera reported attached:

```powershell
Get-PnpDevice -PresentOnly | Where-Object { $_.Class -in @('Net','Ports','USB','Modem','Unknown') }
Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -like 'USB\VID_*' }
Get-NetAdapter -IncludeHidden
Get-NetIPConfiguration
ipconfig /all
route print -4
arp -a
```

Historical evidence was checked read-only without extracting firmware or changing the camera:

```powershell
tar -xOf C:\Projects\bubl\LOGS\18072621.TGZ var/log/all | rg -n -i -m 20 'g_ether|usb0|192\.168\.2\.[12]'
tar -xOf C:\Projects\bubl\LOGS\16011210.TGZ var/log/all | rg -n -i -m 20 'g_ether|usb0|192\.168\.2\.[12]'
```

`Get-PnpDevice -PresentOnly` showed no class `Ports`, `Modem`, or `Unknown` entry attributable to the Bublcam. The present USB VID/PID records were identified as other laptop equipment:

| Present USB ID | Windows identification | Why not assigned to Bublcam |
|---|---|---|
| `32AC:0002` | HDMI Expansion Card | Bus-reported device description |
| `32AC:001C` | Laptop Webcam Module (2nd Gen), plus its DFU interface | Bus-reported description and camera/DFU child functions |
| `0E8D:0717` | RZ717 Bluetooth adapter | Bluetooth child interface |
| `0BDA:8156` | Realtek Gaming USB 2.5GbE Family Controller | Active laptop Ethernet interface, `192.168.1.71/24` with gateway `192.168.1.254` |
| `27C6:609C` | Framework Fingerprint Reader | Biometric device |

Thus **Bublcam VID/PID, USB class/subclass/protocol, configuration/interface count, endpoints, manufacturer/product strings, and USB serial are undetermined**. There was no pre-attachment enumeration snapshot, so this check cannot prove whether any transient device briefly appeared and disappeared. A past non-present Windows entry for an unknown USB descriptor failure does not identify this camera and was not treated as live evidence.

The present network adapters included the laptop's Realtek USB Ethernet (`ifIndex 14`, `192.168.1.71/24`), Wi-Fi (`ifIndex 19`, `192.168.0.10/24`), and unrelated virtual/tunnel adapters. None had `192.168.2.1`, and `route print -4` showed no `192.168.2.0/24` on-link route. A packet to `192.168.2.2` would have followed the ordinary default route via `192.168.1.254`, not a verified USB link. Therefore **no ping to 192.168.2.2 was sent**, and no HTTP or port probe was misrepresented as USB traffic. No Windows address or route was added.

For a Wi-Fi-only reference, the route to `192.168.0.100` was on-link via Wi-Fi `192.168.0.10`. `GET /osc/info` with `X-XSRF-Protected: 1` returned HTTP 200 and model `bubl1` in about 355 ms; `POST /osc/state` with `{}` and the same header returned HTTP 200 in about 29 ms. These timings are single requests and not a stability benchmark. The full JSON was not published.

## Historical camera evidence, not a live USB observation

Archived logs in the privately held `18072621.TGZ` and `16011210.TGZ` contain kernel lines such as `g_ether gadget: Ethernet Gadget ... ready`, `usb0: MAC ...`, and `usb0: HOST MAC ...`. Later Avahi lines join `usb0.IPv4` at `192.168.2.2`. For example, `18072621.TGZ` `var/log/all` around lines 1093–1098 and 1138–1142 show those events. The logs also contain `usb0: link is not ready` shortly after boot. The gadget MACs vary across logged boots and were not published as stable identifiers.

There is stronger **historical network evidence** in `16011210.TGZ` `var/log/all` around lines 1832–1853: Scarlet recorded HTTP GET requests addressed to host `192.168.2.2:80` from remote address `192.168.2.1`. They requested `/` and `/favicon.ico` without `X-XSRF-Protected` and were rejected with `expected X-XSRF-Protected header`. This confirms that a host at `.2.1` reached the Scarlet HTTP server at `.2.2` in that older session, and explains why the header is needed there too. It does **not** prove a successful `/osc/info` response over USB, identify the historical host OS/USB descriptors, or establish the current cable's data link.

## Capability comparison

| Item | Wi-Fi, observed on this unit | USB, this connection |
|---|---|---|
| Camera IP | `192.168.0.100` | Historical `192.168.2.2`; not live-verified |
| Host IP | `192.168.0.10` on Wi-Fi | Historical Scarlet client address `.2.1`; no live `.2.1` or identified USB adapter |
| OSC `/osc/info`, `/osc/state` | Both HTTP 200 | Not live-testable; historical Scarlet HTTP on `.2.2:80` rejected headerless requests |
| RTSP | Previously confirmed over Wi-Fi with dynamic endpoint | Not tested; no USB network path |
| SSH/Telnet/targeted ports | Not tested in this USB phase | Not tested; do **not** infer ports are closed |
| USB CDC ACM / COM | Not applicable | No present COM interface attributable to camera |
| USB class/descriptors | Not applicable | Camera VID/PID and interfaces unknown |
| Latency/stability | One Wi-Fi info/state request: ~355/~29 ms | No measurement possible |

USB cannot currently be recommended as the main development/control connection on this Windows setup. The historical `g_ether` evidence makes it worth retesting after the user confirms the camera's USB data port, a known data-capable cable, and an attachment event. Capture a before/after PnP snapshot while attaching; if a USB network adapter appears, establish its identity and route before pinging `192.168.2.2` or probing OSC/RTSP. Do not install an unusual driver or alter gadget mode as a discovery step.
