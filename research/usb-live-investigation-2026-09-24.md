# USB connection investigation, 2026-09-24

**Updated outcome after a controlled cable-#3 before/unplug/reconnect comparison:** The Bublcam did enumerate once as `USB\VID_0525&PID_A4A2`, class `Ports`, friendly name `USB Serial Device (COM4)`. Its bus-reported description was `RNDIS/Ethernet Gadget`, but Windows bound `usbser`/`usbser.inf` and created **no USB network adapter**. After unplugging, COM4 disappeared. On reconnection at the same hub port, Windows instead reported a device-descriptor failure (Code 43); COM4 did not return. No `192.168.2.x` host interface or route was observed in any snapshot. The camera's live USB Ethernet, OSC, and RTSP access remain unverified. Do not treat the failure pseudo-ID `VID_0000&PID_0002` as the camera's real VID/PID.

No USB driver, camera setting, Windows network setting, firmware, or gadget configuration was changed. No camera reboot, USB stream, photo, recording, credential attempt, COM-port write, or broad port scan occurred. Raw camera media and device serials are not included here.

## Controlled cable-#3 comparison

With the camera kept powered on, a private PowerShell snapshot captured all present `Get-PnpDevice` entries, all `Get-NetAdapter -IncludeHidden` records, `Get-NetIPConfiguration -All`, `ipconfig /all`, and `route print` in each state. The user unplugged only cable #3 between the first two snapshots, then reconnected it before the third. Raw snapshots are retained outside Git under `bubl_research/responses/usb_snapshots/`:

| State | Present PnP devices | Adapter records | Camera-associated USB node |
|---|---:|---:|---|
| Connected before unplug (`22:53:44` local) | 223 | 24 | `USB Serial Device (COM4)`, status OK |
| Disconnected (`22:54:19`) | 222 | 24 | None |
| Reconnected (`22:55:15`; confirmed again `22:56:32`) | 223 | 24 | `Unknown USB Device (Device Descriptor Request Failed)`, Code 43 |

The complete InstanceId diff was exactly COM4 disappearing on unplug, then the descriptor-failure node appearing on reconnect. There was no network-adapter identity diff or IP-interface diff. The 24 adapter records include hidden/virtual adapters; none was a Bublcam USB network adapter. `Get-NetIPConfiguration`, `ipconfig /all`, and `route print` showed no `192.168.2.x` interface or USB route in any state. No ping or OSC request to `192.168.2.2` was sent.

The successful connected node's Windows PnP data:

| Field | Observed value |
|---|---|
| Class / friendly name | `Ports` / `USB Serial Device (COM4)` |
| InstanceId | `USB\VID_0525&PID_A4A2\6&22C573BB&0&1` |
| Hardware ID | `USB\VID_0525&PID_A4A2&REV_0316` (plus unversioned ID) |
| VID / PID / MI | `0525` / `A4A2` / no `MI_` interface number in the PnP ID |
| USB compatible class | `Class_02`, `SubClass_02`, `Prot_FF` (from Windows compatible IDs; not a complete raw descriptor dump) |
| Bus-reported description | `RNDIS/Ethernet Gadget` |
| Device description | `USB Serial Device` |
| Manufacturer | Windows driver provider `Microsoft`; actual USB manufacturer string not established |
| Service / driver | `usbser` / `usbser.inf`, `USB Serial Device`, version `10.0.26100.9278` |
| Parent / location | `USB\ROOT_HUB30\5&209565c2&0&0`; `...XHC3.RHUB.PRT1`, port 1 |
| Children/interfaces | No separate child/interface PnP node or `MI_` ID appeared in the diff; endpoint layout not available from these Windows properties |
| Status / problem | `OK` / no problem in first connected snapshot; subsequently non-present (`CM_PROB_PHANTOM`) |

The reconnect failure was on the same hub port/location (`6&22C573BB&0&1` suffix), but Windows could not read its device descriptor. Its PnP fields were:

| Field | Reconnect failure node |
|---|---|
| Class / friendly name | `USB` / `Unknown USB Device (Device Descriptor Request Failed)` |
| InstanceId | `USB\VID_0000&PID_0002\6&22C573BB&0&1` |
| VID / PID / MI | `0000:0002` is a Windows placeholder; no real VID/PID or `MI_` available |
| Manufacturer / description | Windows label `(Standard USB Host Controller)` / descriptor-request failure; no camera manufacturer or bus-reported product string available |
| Service / driver | No functional camera service exposed; Windows failure driver `usb.inf` (`BADDEVICE.Dev.NT`) |
| Parent / children | Same `USB\ROOT_HUB30\5&209565C2&0&0` port; no camera child/interface enumerated |
| Status / problem | `Error`, Code 43 (`CM_PROB_FAILED_POST_START`) |

That pseudo-ID is **not** a Bublcam USB identity. No endpoint, class, or serial descriptor can be recovered from this failed enumeration.

The `RNDIS/Ethernet Gadget` product string agrees with the older `g_ether` logs, but a product string is not proof that Windows exposed a usable Ethernet interface. The observed `usbser` binding matches the reported class/subclass compatible ID and explains why Windows offered COM4 instead. Whether that binding reflects firmware descriptors, a Windows class-selection quirk, or an incomplete/unstable enumeration is unresolved. At this stage, COM4 was not opened because the reconnect failed and the requested phase was passive PnP/network comparison only. No driver was installed or changed.

## Later passive COM4 attempt

COM4 reappeared with the same `0525:A4A2` PnP InstanceId, class `Ports`, status `OK`, and Config Manager problem code `0`. `Win32_SerialPort` reported `MaxBaudRate: 115200` and `SettableBaudRate: True`, but its current `BaudRate` field was empty. These are Windows device/driver properties, **not a measurement of the camera's serial speed**.

One receive-only attempt used `COM4` at 115200, 8 data bits, no parity, one stop bit, no flow control, with DTR and RTS explicitly disabled before opening. `System.IO.Ports.SerialPort.Open()` failed immediately with `A device attached to the system is not functioning.` No bytes were read, no serial data was sent, and no capture file was produced. Windows still listed COM4 as PnP `OK` afterward. Because the port failed to open, the planned 57600/38400/9600 listening attempts were **not** made; no baud rate, login prompt, shell, or live serial protocol can be established from this result. The cause could be device, cable, enumeration, or driver behavior; this test does not isolate it. The exact private attempt record is under `bubl_research/responses/usb_serial_probe/`.

## Earlier attachment snapshot (before cable #3 comparison)

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

At that earlier snapshot, **Bublcam VID/PID and interface descriptors were undetermined**. There was no pre-attachment enumeration snapshot, so that check could not prove whether a transient device briefly appeared and disappeared. The controlled cable-#3 comparison above supersedes that limited conclusion and links the descriptor-failure location to the disappearing COM4 node.

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
| USB CDC ACM / COM | Not applicable | COM4 appeared once with `usbser`, then disappeared on reconnect failure; no serial data tested |
| USB class/descriptors | Not applicable | Successful VID/PID `0525:A4A2`, compatible class `02/02/FF`; full descriptors/endpoints unknown |
| Latency/stability | One Wi-Fi info/state request: ~355/~29 ms | No measurement possible |

USB cannot currently be recommended as the main development/control connection on this Windows setup. The descriptor failure after reconnect is a reason to stop further probing in this session and inspect the physical cable/connector/power situation before any new test. If a later stable attachment produces a genuine network adapter, establish its identity and route before pinging `192.168.2.2` or probing OSC/RTSP. Do not install an unusual driver or alter gadget mode as a discovery step.
