# Ubuntu LTS path: supported-toolchain workstation

Prepared on **14 November 2026**. This folder is an alternative to the CachyOS playbook in the rest of this repository. It exists because the priority changed: MATLAB, ROS 2, CUDA and vendor embedded tools have to work without workarounds, and that matters more than rolling-release performance.

These are researched procedures. Nothing here was installed or executed on the laptop. Every command should be read before it is run, and results recorded in [the acceptance record](../../templates/acceptance-record.md).

## Which guide to follow

| | [Ubuntu 24.04.5 LTS](24.04/01-install.md) | [Ubuntu 26.04.1 LTS](26.04/01-install.md) |
|---|---|---|
| Status | **Recommended now** | Use when MathWorks lists it for ROS Toolbox, or if you do not need that toolbox |
| MATLAB R2026b | Supported | Supported |
| MATLAB ROS Toolbox R2026b | Supported, recommended platform | Not listed |
| Native ROS 2 | Jazzy (Tier 1), Gazebo Harmonic | Lyrical (Tier 1), Gazebo Jetty |
| Other ROS 2 release | Lyrical in a container | Jazzy in a container |
| Kernel | 7.0 HWE, with 6.8 GA available as fallback | 7.0 only |
| Desktop | GNOME 46 or Plasma 5.27; X11 and Wayland | GNOME 50 (Wayland only) or Plasma 6 |
| System Python / GCC | 3.12 / 13 | 3.14 / 15 |
| Standard support ends | May 2029 | April 2031 |

The reasoning and the scored comparison against Fedora, Debian, Pop!_OS, atomic desktops and CachyOS are in [the distro decision](01-distro-decision.md).

## Reading order

Each version has the same five chapters:

1. **Install** — backup, media, firmware, partitioning beside Windows, first boot.
2. **Snap, Flatpak and apt** — keep snapd intact, make apt and Flatpak the day-to-day sources.
3. **Toolchain** — NVIDIA, containers, ROS 2, Gazebo, MATLAB, KiCad, embedded tools.
4. **Performance** — what CachyOS was doing on this laptop and the Ubuntu equivalent, in three tiers: power, kernel, memory, storage, graphics, desktop, builds, ROS 2 and real time.
5. **Long-term upkeep** — update discipline, disk hygiene, hardware care, and a symptom table for when it gets slower.

| Chapter | 24.04 | 26.04 |
|---|---|---|
| Install | [24.04/01-install.md](24.04/01-install.md) | [26.04/01-install.md](26.04/01-install.md) |
| Snap, Flatpak and apt | [24.04/02-snap-flatpak-apt.md](24.04/02-snap-flatpak-apt.md) | [26.04/02-snap-flatpak-apt.md](26.04/02-snap-flatpak-apt.md) |
| Toolchain | [24.04/03-toolchain.md](24.04/03-toolchain.md) | [26.04/03-toolchain.md](26.04/03-toolchain.md) |
| Performance | [24.04/04-performance.md](24.04/04-performance.md) | [26.04/04-performance.md](26.04/04-performance.md) |
| Long-term upkeep | [24.04/05-long-term-upkeep.md](24.04/05-long-term-upkeep.md) | [26.04/05-long-term-upkeep.md](26.04/05-long-term-upkeep.md) |

## Hardware this was written for

| Item | Value |
|---|---|
| Laptop | ASUS TUF Gaming A17 FA706IC |
| CPU | Ryzen 7 4800H (Zen 2), 8 cores / 16 threads |
| RAM | 16 GB today (2 × 8 GB). An upgrade to 24 GB (8 + 16) is planned; the memory and build settings cover both |
| Graphics | AMD integrated + RTX 3050 Laptop, 4 GB VRAM |
| Wireless | MediaTek MT7921 Wi-Fi; USB Bluetooth `13d3:3563` |
| Linux SSD | `SAMSUNG MZVLQ512HBLU`, 476.9 GiB, currently CachyOS |
| Windows SSD | `Samsung SSD 980 500GB`, 465.8 GiB, must stay untouched |

## What still applies from the rest of the repository

- [Bluetooth audio](../04-bluetooth-audio.md): PipeWire, WirePlumber and BlueZ are the same stack on Ubuntu.
- [Containers and ROS](../06-containers-and-ros.md) and `scripts/ros.sh`: the Jazzy container runs unchanged on either Ubuntu host.
- [Embedded](../07-embedded.md), [AI/ML](../08-ai-ml.md), [networking and CAN](../17-robot-networking-and-can.md): concepts carry over; package names are in each toolchain chapter here.
- [Capacity budget](../02-fresh-install.md#4-capacity-budget) and the backup steps.

What does not apply: `scripts/packages.sh --apply` (pacman only), Snapper and Limine instructions, `chwd`, and CachyOS kernel guidance.
