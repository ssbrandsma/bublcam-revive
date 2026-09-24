# Differing `_bublAtmelVersion` observations

Two `/osc/info` observations for model `bubl1`, serial `f4b85e1a4e97`, firmware `2.1.1`, and endpoint `192.168.0.100:80` differ:

| Field | Earlier supplied JSON | Later saved response |
|---|---:|---:|
| `_bublAtmelVersion` | `"1"` | `"2.2"` |
| `uptime` | `211085` | `349291` |

All other parsed top-level JSON fields, including the serial, firmware, endpoint ports, and advertised API list, match. Both values are strings, so this is not a numeric-format difference.

**Provenance:** the earlier JSON was pasted by the camera owner as an observed `/osc/info` response. There is no preserved earlier HTTP packet or header/body capture, so copying or transcription error cannot be ruled out. The later response is preserved locally from a successful GET; the PowerShell capture re-encoded its text as UTF-16LE, so it is not byte-for-byte identical to the original wire response either. A local comparison report records SHA-256 hashes for both source files and the parsed field differences.

**Unresolved:** the value could change with device state, reflect a component restart/update, or result from an earlier transcription error. Both uptimes are high, so these samples do not establish a startup transition. No update operation was performed during this investigation. Future work should capture `/osc/info` response bytes directly at known times and correlate them with a read-only state snapshot; until then, documentation must retain both observations.
