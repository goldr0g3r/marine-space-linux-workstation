# Which distro, and why?

## Pick: CachyOS Desktop, KDE Plasma on Wayland

This is my best-fit recommendation for **your priorities and experience**, not a claim that a single distro wins every workload. You can maintain Linux, are comfortable with containers, and put responsiveness and performance ahead of minimizing system maintenance. CachyOS provides current Arch-family software plus performance-oriented packaging and kernel work. Its hardware detection handles NVIDIA installation, reducing manual setup. [Optimized repositories](https://wiki.cachyos.org/features/optimized_repos/), [kernel features](https://wiki.cachyos.org/features/kernel/), [hardware detection](https://wiki.cachyos.org/features/chwd/chwd/).

Your Ryzen 4800H is a Zen 2 CPU. Let the installer select compatible optimized repositories; do not force Zen 4 or AVX-512 packages. Vendor performance claims are workload-dependent and are not measurements of this laptop. CUDA throughput, memory pressure, cooling and disk usage may dominate any distro difference. Ubuntu container binaries and downloaded Python wheels do not inherit CachyOS repository compiler optimizations; the host kernel still matters.

The existing OS is not a selection criterion. With both SSDs ready for a fresh installation, I would still narrowly choose CachyOS for your explicit performance-first preference. EndeavourOS is a close alternative if a less customized Arch baseline matters more. [Detailed comparison](13-cachyos-vs-endeavouros.md).

KDE is a practical choice because audio profiles, Bluetooth and power settings are easy to inspect. Your current KDE Wayland session works with the installed NVIDIA stack. That is useful compatibility evidence, although it does not guarantee a future driver or kernel will behave identically.

**Bluetooth is not a CachyOS-exclusive advantage.** Fedora, Ubuntu and other distributions use the same upstream building blocks. New versions can bring fixes and regressions. The right codec, microphone selection, adapter firmware and suspend behavior are the deciding factors. WirePlumber documents the quality loss when Bluetooth switches into headset mode. [Bluetooth settings](https://pipewire.pages.freedesktop.org/wireplumber/daemon/configuration/settings.html).

## Comparison

These are qualitative judgments based on project documentation and your workflow, not numerical benchmark scores.

| Candidate | Why consider it | Cost for this laptop/workflow | Decision |
|---|---|---|---|
| **CachyOS KDE** | Performance-oriented defaults, current stack, Arch ecosystem, integrated hardware setup | Rolling updates; kernel/NVIDIA changes require fallback and recovery discipline | **Best fit** |
| **Fedora KDE Plasma Desktop** | Current desktop stack with a versioned release process; good container-oriented workflow | NVIDIA setup is an additional packaging step; still needs periodic release upgrades | **Runner-up** if maintenance predictability becomes more important |
| **openSUSE Tumbleweed KDE** | Rolling packages with automated testing and established Btrfs/Snapper recovery | Another packaging workflow to learn; GPU integration still needs validation | Strong alternative if rollback workflow is the main attraction |
| **Ubuntu LTS / Kubuntu LTS** | Broad vendor tooling and documentation alignment | No demonstrated audio or performance advantage for this hardware; host ROS compatibility is not required here | Good project userspace inside containers |
| **EndeavourOS KDE** | Close-to-Arch package baseline, current GPU hardware tooling, user-selected setup | More explicit recovery/tuning setup; same rolling-update responsibilities | **Closest Arch-family alternative**; prefer for fewer distribution-specific customizations |
| **Arch KDE** | Full control over every component | More installation and integration work | Choose if constructing the host is part of the learning goal |
| **NixOS** | Declarative configuration and reproducible environments | Vendor SDKs and ad hoc embedded tooling can require extra packaging work | Worth learning later; not my first workstation recommendation |

References: [Fedora KDE](https://fedoraproject.org/kde/), [Tumbleweed](https://get.opensuse.org/tumbleweed/), [Ubuntu Desktop](https://ubuntu.com/desktop), [EndeavourOS](https://endeavouros.com/), [NixOS manual](https://nixos.org/manual/nixos/stable/).

## Exact configuration I would choose

- Current stable CachyOS Desktop ISO; KDE Plasma; Wayland initially.
- Btrfs using the installer-supported subvolume layout, with snapshot recovery verified.
- Installer-supported bootloader. Keep GRUB if it is the best-supported option for the chosen encryption/layout; no need to switch purely for speed.
- Default CachyOS kernel plus CachyOS LTS, each with matching NVIDIA support.
- AMD iGPU for ordinary desktop use, NVIDIA on demand for compute/rendering.
- PipeWire + WirePlumber + BlueZ; AAC or SBC for your neckband, chosen by listening and dropout tests.
- Existing/default zram configuration initially; balanced power profile for daily use.
- Rootless Podman for the reproducible CLI lab; Distrobox only for trusted interactive GUI/vendor environments.
- ROS 2 Jazzy / Ubuntu 24.04 / Gazebo Harmonic for the supplied learning lab. This is a deliberate mature compatibility target, **not the newest ROS release**. ROS 2 Lyrical is the newer LTS, supported through May 2031; Jazzy remains supported through May 2029. [ROS release source](https://github.com/ros2/ros2_documentation/blob/rolling/source/Releases.rst).

## When I would change this recommendation

Choose Fedora KDE if repeated rolling-update regressions cost more time than the performance tuning is worth. Choose an Ubuntu host if a specific employer, certified vendor SDK or course requires a supported bare-metal platform. If Bluetooth fails identically on different current distributions, investigate the headset, radio conditions and adapter before reinstalling again.

There was no side-by-side distro benchmark or physical Bluetooth listening test during research. The guide provides acceptance tests so you can make the final hardware judgment on evidence.
