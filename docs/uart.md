# UART / I²C / debug

Visible UART pads:
```text
RX TX GND
```
3.3 V TTL is a hypothesis: **measure first**. Conservative initial terminal setting after verification: 115200 8N1.

Connection:
```text
Bubl TX -> adapter RX
Bubl RX -> adapter TX
GND     -> GND
VCC     -> DO NOT CONNECT
```

If a shell appears, begin read-only:
```sh
uname -a
cat /proc/cpuinfo
cat /proc/cmdline
cat /proc/mtd
mount
df
ps
netstat -lntup 2>/dev/null || netstat -lnt
ls -la /opt/bubl
find /opt/bubl -type f 2>/dev/null
ubinfo -a 2>/dev/null
```

Visible I²C pads:
```text
SDA SCL GND
```
If i2c-tools exist, inventory buses before scanning. Some I²C devices react badly to indiscriminate probing.

Power test pads observed: `3.3V`, `2.5V`, `1.8V`, `1.2V`.
