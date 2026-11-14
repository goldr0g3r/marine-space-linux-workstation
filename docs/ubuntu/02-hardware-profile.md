# Hardware profile

Read from this laptop on **14 November 2026**, running CachyOS with kernel 7.3.3. Sources were an `lshw` report generated without root, plus read-only checks of `/sys`, `/proc`, `lsusb` and `lspci`. Serial numbers, MAC addresses and IP addresses are deliberately left out; see [privacy](#privacy).

The guides in this folder use these facts. After installing Ubuntu, repeat the checks in [the last section](#repeat-the-checks-on-ubuntu) and note any difference.

## Inventory

| Part | Finding |
|---|---|
| Model | ASUS TUF Gaming A17 FA706IC |
| BIOS | American Megatrends `FA706IC.302`, dated 28 December 2022 |
| CPU | AMD Ryzen 7 4800H (Zen 2 "Renoir"), family 17h, model 60h, stepping 1; 8 cores, 16 threads; up to 4.30 GHz; microcode `0x860010d` |
| Memory | 16 GB installed as 2 × 8 GB; 512 MiB of it reserved for the integrated GPU |
| Integrated GPU | AMD Renoir Radeon `[1002:1636]`, driver `amdgpu` |
| Discrete GPU | NVIDIA GeForce RTX 3050 Mobile, GA107M `[10de:25a2]`, 4 GB VRAM, driver `nvidia`, PCI address `0000:01:00.0` |
| Internal display | 1920 × 1080, 144 Hz and 60 Hz modes |
| Linux SSD | Samsung PM991a, `MZVLQ512HBLU-00B00`, 476.9 GiB, firmware `FXM7201Q` |
| Windows SSD | Samsung SSD 980 500GB, 465.8 GiB, firmware `3B4QFXO7` |
| Ethernet | Realtek RTL8111/8168 gigabit `[10ec:8168]`, driver `r8169`, interface `enp2s0` |
| Wi-Fi | MediaTek MT7921 Wi-Fi 6 `[14c3:7961]` on an AzureWave module, driver `mt7921e`, interface `wlan0` |
| Bluetooth | USB device `13d3:3563`, the Bluetooth half of the MT7921 module |
| Audio | Realtek ALC256 codec for speakers, headphones and microphone; HDMI/DP audio on each GPU |
| Webcam | Sonix USB 2.0 HD UVC `322e:202c` |
| Touchpad | ELAN1203 over I2C |
| Platform | ASUS WMI hotkeys, platform profiles (quiet, balanced, performance), battery `BAT1` with a charge limit, AC adapter `ACAD` |

## CPU

- **Instruction level: x86-64-v3.** AVX2, FMA, BMI1, BMI2 and F16C are present; AVX-512 is not. CachyOS used its v3 package repositories on this laptop. Ubuntu's normal packages target the baseline; 26.04 has an opt-in v3 variant, described in [its performance chapter](26.04/04-performance.md#optimised-packages-on-2604-tier-3-experimental).
- **Frequency scaling.** The `cppc` flag is present and the running driver was `amd-pstate-epp` in active mode. The power-profile sections of the performance chapters rely on this.
- **Threads.** Sibling threads are numbered in pairs: 0–1, 2–3, up to 14–15. The CPU-isolation example in the performance chapters reserves the last pair, which is one physical core.
- **Virtualisation.** `svm`, nested paging and an IOMMU are present, so KVM works. That makes a Windows virtual machine an option for Windows-only tools.

## Memory

`lshw` reports 16,642,998,272 bytes, which is exactly 16 GiB minus 512 MiB. The 512 MiB is the firmware's reservation for the integrated GPU. The integrated GPU takes further memory from the system as needed, since it drives the desktop.

The report was made without root, so it has no per-slot detail. Before buying memory for the planned 8 + 16 GB upgrade, read the speed and part number of the installed modules:

```bash
sudo dmidecode -t memory | grep -E 'Size|Speed|Part Number|Locator|Manufacturer'
```

Match the new module's speed to the existing one. With 8 + 16 GB, the first 16 GB runs dual-channel and the remaining 8 GB single-channel.

## Graphics and display wiring

Which GPU a display socket is wired to decides whether the NVIDIA GPU can power down.

| Output | Wired to | Effect |
|---|---|---|
| Internal panel (`eDP-1`) | AMD | Desktop renders on AMD; NVIDIA can sleep |
| HDMI (`HDMI-A-1`) | AMD | An HDMI monitor leaves NVIDIA free to sleep |
| DisplayPort (`DP-1`), reached through the USB-C port | NVIDIA | A USB-C or DisplayPort monitor keeps NVIDIA awake |

For desk use with one external monitor, HDMI is the cooler and quieter choice. Use the USB-C output when a monitor needs to be driven directly by NVIDIA.

## Storage

| | Linux SSD | Windows SSD |
|---|---|---|
| Model | Samsung PM991a (`MZVLQ512HBLU`) | Samsung SSD 980 500GB |
| Type | OEM NVMe without a DRAM cache | Retail NVMe without a DRAM cache |
| Device node when read | `nvme0` | `nvme1` |
| PCI device ID | `144d:a809` | `144d:a809` |

- Both drives report the same PCI device ID and similar sizes. Identify the install target by model name and existing partitions. Device nodes can swap between boots.
- The Linux filesystem was **88% full**: 415 GiB used, 59 GiB free. Drives without a DRAM cache slow down noticeably when nearly full and during long writes. This was costing performance under CachyOS and would do the same on any distribution.
- A fresh install starts empty. Restore selectively and keep to the [capacity budget](../02-fresh-install.md#4-capacity-budget).

## Network, audio and input

- Ethernet had no cable when read. Wi-Fi was connected with power saving on.
- The AMD audio coprocessor `[1022:15e2]` had no driver bound. Recording goes through the ALC256 codec, which has a capture device, so this does not affect the microphone.
- The NVIDIA audio function exposes four HDMI/DP outputs and the AMD one exposes one. These carry sound to external displays.

## Driver support on Ubuntu

| Device | Driver | In the Ubuntu kernel |
|---|---|---|
| AMD integrated GPU | `amdgpu` | Yes |
| NVIDIA GPU | `nvidia` | No; installed with `ubuntu-drivers` |
| Both SSDs | `nvme` | Yes |
| Ethernet | `r8169` | Yes |
| Wi-Fi | `mt7921e` | Yes; firmware from `linux-firmware` |
| Bluetooth | `btusb` with MediaTek firmware | Yes |
| Audio | `snd_hda_intel` | Yes |
| Touchpad | `i2c_hid` | Yes |
| ASUS platform features | `asus_wmi`, `asus_nb_wmi` | Yes |
| Temperature sensor | `k10temp` | Yes |

All of this hardware dates from 2020 and 2021. Ubuntu 24.04's original 6.8 kernel already supports it, so newer kernels are a choice here, not a requirement.

## What limits this laptop

In order of how much each affects the planned work:

1. **Disk space on a cache-less SSD.** Fixed by the reinstall, if the disk is kept under about 80% afterwards.
2. **16 GB of memory.** Gazebo, MATLAB, a build and a browser together exceed it. zram and build job limits manage it; the planned upgrade removes it.
3. **4 GB of VRAM.** Limits simulation with rendering and any CUDA work at the same time. No setting changes this.
4. **Cooling.** A 45 W CPU and a discrete GPU in one chassis. Clean it yearly.

The CPU itself is not a limit for this work.

## Oddities in the lshw report that are not faults

- The NVMe drives are labelled "AHCI SSD Controller (Apple slot)". That is the database name for their subsystem ID.
- Each NVMe namespace appears three times, as `hwmon`, `ng` and `nvme` entries.
- A "PCI bridge" is named "Video Bus", and some bridges show `ioport` ranges of several gigabytes. These are 64-bit memory windows and an input device that `lshw` attached to the wrong node.
- The `usb-storage` host was a USB flash drive plugged in at the time.
- CPU "size" (2.86 GHz) is the frequency at the moment of capture; "capacity" (4.30 GHz) is the maximum.

## Firmware

BIOS `FA706IC.302` is from December 2022. Before reinstalling, check ASUS's support page for this model for a newer version, read its notes, and apply it on AC power. Firmware for the SSDs and other devices is offered through `fwupdmgr get-updates`.

## Privacy

A raw `lshw` report contains both SSD serial numbers, the Ethernet and Wi-Fi MAC addresses and the local IP address. Do not commit one to this repository. To produce a report that is safe to keep or share:

```bash
sudo lshw -sanitize -xml > lshw-sanitized.xml
```

Running it with `sudo` also adds the memory-slot, cache and firmware detail the original lacked.

## Repeat the checks on Ubuntu

```bash
cat /sys/class/dmi/id/product_name /sys/class/dmi/id/bios_version
```

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver; ld.so --help | grep -E 'x86-64-v[234]'
```

```bash
for c in /sys/class/drm/card[0-9]; do echo "$(basename "$c") $(basename "$(readlink "$c/device/driver")")"; ls -d "$c"-* | xargs -n1 basename; done
```

```bash
lspci -nnk | grep -A3 -E 'VGA|Network|Ethernet|Non-Volatile'
```

```bash
lsusb; cat /proc/asound/cards; df -h /
```

The connector names and the GPU each belongs to should match the wiring table above.
