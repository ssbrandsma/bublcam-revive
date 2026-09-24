# Networking

Tested Wi-Fi API address:
```text
192.168.0.100:80
```

Historical default Bublcam Wi-Fi password reported publicly: `12345678`. A unit may have been changed.

Firmware 2.1.1 requires:
```text
X-XSRF-Protected: 1
```

Without it the camera returned:
```json
{"name":"","state":"error","error":{"code":"_bublRequestError","message":"expected X-XSRF-Protected header"}}
```

Safe probes:
```bash
ping 192.168.0.100
curl -H "X-XSRF-Protected: 1" http://192.168.0.100/osc/info
curl -X POST -H "X-XSRF-Protected: 1" -H "Content-Type: application/json" -d '{}' http://192.168.0.100/osc/state
```

`/osc/state` uses POST according to Bubl's original client and a live 200 response. `/osc/checkForUpdates` also uses POST and requires a `stateFingerprint` from `/osc/state`; an empty body returns `missingParameter`. Logs identify `wlcore`, `wl12xx`, hostapd and avahi-daemon. Do not call `_bublUpdate` during discovery.
