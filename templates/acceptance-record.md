# Laptop acceptance record

Copy this template into private notes or `reports/`. Replace “Pending” only with an observed result. Do not include disk serial numbers, Bluetooth addresses, access tokens or unredacted logs if sharing the record.

## Installation identity

| Field | Value |
|---|---|
| Date | Pending |
| Distribution and install media | Pending |
| KDE/session type | Pending |
| Main kernel / fallback kernel | Pending |
| NVIDIA driver | Pending |
| PipeWire / WirePlumber / BlueZ versions | Pending |
| Filesystem / bootloader / encryption choice | Pending |
| Backup destination description | Pending |
| Free disk space | Pending |
| Power profile / AC or battery | Pending |

Useful read-only commands:

```bash
cat /etc/os-release
uname -r
printf '%s\n' "$XDG_SESSION_TYPE"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
pacman -Q pipewire wireplumber bluez
findmnt -no FSTYPE /
df -h /
powerprofilesctl get
zramctl
```

## Hardware and daily use

| Test | Result | Notes / exact failure |
|---|---|---|
| Normal boot and shutdown | Pending | |
| Main + LTS kernel boot | Pending | |
| Wi-Fi transfer while using laptop | Pending | |
| Keyboard, touchpad and brightness | Pending | |
| External monitor and screen sharing, if needed | Pending | |
| Webcam and built-in microphone | Pending | |
| Five suspend/resume cycles | Pending | |
| Bluetooth reconnect after cold boot | Pending | |

## Realme audio

| Condition | Profile / codec | Outcome |
|---|---|---|
| Local audio for 30 minutes | Pending | Pending |
| Audio during compile | Pending | Pending |
| Browser call with laptop microphone | Pending | Pending |
| Browser call with neckband microphone | Pending | Pending |
| Phone disconnected, 5 GHz Wi-Fi | Pending | Pending |
| Phone multipoint enabled | Pending | Pending |

Chosen daily output/profile:

Chosen daily microphone:

Autoswitch setting and reason, if changed:

## Development and recovery

| Test | Result | Evidence |
|---|---|---|
| Rootless container starts | Pending | |
| ROS talker/listener exchange | Pending | |
| Package build + persistent user-owned files | Pending | |
| RViz/Gazebo, if installed | Pending | |
| CUDA tensor operation, if installed | Pending | |
| Board UART/debug probe, if available | Pending | |
| Snapshot recovery rehearsal | Pending | |
| External backup and sample restore | Pending | |

## Performance experiment

Use one specific project and three runs under comparable conditions. Record build cache state, compiler, job count, GPU driver and power profile; differing conditions can explain results.

| Item | Baseline | Changed configuration |
|---|---|---|
| Exact change | None | Pending |
| Project revision / command | Pending | Pending |
| Cold or warm cache | Pending | Pending |
| Run 1 / 2 / 3 | Pending | Pending |
| Median | Pending | Pending |
| Peak memory / memory pressure | Pending | Pending |
| Audio dropouts under load | Pending | Pending |
| Thermal or responsiveness observations | Pending | Pending |

Decision: keep or revert the change, with a reason.

## Open issues and next action

| Issue | Reproduction | Next single change/test | Outcome |
|---|---|---|---|
| Pending | | | |
