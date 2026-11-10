# Research sources and confidence

Research date: **10 November 2026**, Asia/Kolkata. Links point to upstream projects, distribution documentation or manufacturer-authored material. Rolling pages can change; re-check installation instructions immediately before reinstalling.

## Distro and hardware

| Source | Used for |
|---|---|
| [CachyOS optimized repositories](https://wiki.cachyos.org/features/optimized_repos/) | Architecture-specific packages; project performance claims are not laptop benchmarks |
| [CachyOS kernel](https://wiki.cachyos.org/features/kernel/) | Kernel choices and tuning; retaining a fallback |
| [CachyOS chwd](https://wiki.cachyos.org/features/chwd/chwd/) | Hardware/driver setup |
| [CachyOS ISO verification](https://wiki.cachyos.org/cachyos_basic/download/) | Download authenticity/integrity |
| [CachyOS installation](https://wiki.cachyos.org/installation/installation_on_root/) | UEFI, Secure Boot and installer considerations |
| [CachyOS snapshots](https://wiki.cachyos.org/configuration/btrfs_snapshots/) | Snapshot and bootloader recovery workflow |
| [Fedora KDE](https://fedoraproject.org/kde/) | Primary alternative desktop offering |
| [openSUSE Tumbleweed](https://get.opensuse.org/tumbleweed/) | Rolling model and recovery approach |
| [Ubuntu Desktop](https://ubuntu.com/desktop) | LTS desktop alternative |
| [EndeavourOS](https://endeavouros.com/) | Arch-family alternative |
| [EndeavourOS Titan Nova](https://endeavouros.com/news/titan-nova-is-available/) | Current installation-media context; rolling systems update continuously |
| [EndeavourOS snapshot guide](https://discovery.endeavouros.com/btrfs-with-timeshift-snapshots-on-the-grub-menu/) | Explicit Btrfs/GRUB recovery setup; separate from CachyOS defaults |
| [EndeavourOS downloads](https://endeavouros.com/download/) | Alternative installer and verification resources |
| [EndeavourOS AKM](https://discovery.endeavouros.com/akm/) | Kernel and matching-header selection |
| [systemd zram-generator](https://github.com/systemd/zram-generator) | Optional compressed swap setup when the installer has not configured it |
| [Why CachyOS](https://wiki.cachyos.org/cachyos_basic/why_cachyos/) | Performance orientation and distribution-specific tooling |
| [NixOS manual](https://nixos.org/manual/nixos/stable/) | Declarative-system alternative |
| [ASUS Linux guidance](https://asus-linux.org/guides/arch-guide/) | ASUS-specific tooling context; not proof of every FA706IC feature |

## Audio

| Source | Used for |
|---|---|
| [Realme user manual PDF](https://m.media-amazon.com/images/I/81T2WcgkN5L.pdf) | RMA2412 / Buds Wireless 5 ANC, SBC/AAC and pairing; manufacturer document hosted by a retailer |
| [WirePlumber Bluetooth configuration](https://pipewire.pages.freedesktop.org/wireplumber/daemon/configuration/bluetooth.html) | Codec/profile properties and hardware quirks |
| [WirePlumber settings](https://pipewire.pages.freedesktop.org/wireplumber/daemon/configuration/settings.html) | Automatic headset-profile switching |
| [BlueZ project](https://bluez.github.io/) | Linux Bluetooth stack context |

## Engineering environments

| Source | Used for |
|---|---|
| [ROS upstream release table](https://github.com/ros2/ros2_documentation/blob/rolling/source/Releases.rst) | Jazzy/Lyrical support dates; source used because docs.ros.org access was blocked during research |
| [Gazebo + ROS pairing](https://gazebosim.org/docs/harmonic/ros_installation/) | Jazzy/Harmonic compatibility |
| [Podman run manual](https://docs.podman.io/en/latest/markdown/podman-run.1.html) | User mapping, devices and supplementary groups |
| [Distrobox create](https://distrobox.it/usage/distrobox-create/) | Custom home, GUI integration and NVIDIA option |
| [NVIDIA CDI guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html) | GPU device injection and refresh behavior |
| [Zephyr getting started](https://docs.zephyrproject.org/latest/develop/getting_started/index.html) | Versioned RTOS/toolchain workflow |
| [PyTorch installation](https://pytorch.org/get-started/locally/) | Supported installation selector |
| [uv projects](https://docs.astral.sh/uv/guides/projects/) | Project isolation and locking |
| [uv PyTorch integration](https://docs.astral.sh/uv/guides/integration/pytorch/) | Explicit CPU/CUDA wheel indexes |
| [ArduPilot SITL](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html) | Simulation environment |
| [QGroundControl](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html) | Ground station installation |
| [NASA F´ installation](https://fprime.jpl.nasa.gov/latest/docs/getting-started/installing-fprime/) | Space software learning environment |

## What is measured, inferred or still unknown?

**Observed locally:** laptop model, CPU, RAM, PCI/USB devices, GPU VRAM, current distro/session, installed audio stack, kernels, disk layout, free space and repository package availability. User confirmed this is the target laptop, requested a fresh install and identified the neckband.

**Recommendation/judgment:** CachyOS as best fit, balanced power initially, job/memory limits, storage budgets and the order of learning projects. These are proposed starting points, not universal optimum values.

**Not established:** comparative distro performance, audible quality/latency, neckband firmware, actual negotiated codec, live-install hardware behavior, battery life, suspend reliability, every ASUS control, USB board/probe compatibility, or CUDA/GUI behavior after reinstall. Use the checklist and validation record to close these gaps.

No recommendation depends on ROS being exclusive to Ubuntu. The host is selected for your laptop workflow; the container userspace is selected for project compatibility.
