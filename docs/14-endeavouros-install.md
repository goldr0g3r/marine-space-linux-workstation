# EndeavourOS KDE: alternative fresh-install path

Use this chapter if you choose EndeavourOS after reading [the comparison](13-cachyos-vs-endeavouros.md). It replaces the CachyOS-specific installer, kernel and recovery steps. The Realme audio guide, project environments, capacity budget and learning roadmap still apply.

This is a researched procedure, not an installation performed on your laptop. The current recommendation remains CachyOS by a narrow margin; choosing EndeavourOS is reasonable if its closer-to-Arch baseline better matches your preferences.

## Target configuration

| Component | Starting choice |
|---|---|
| Desktop | KDE Plasma; test Wayland with the installed NVIDIA driver |
| Linux SSD | Btrfs, using the installer's supported layout; preserve the separate Windows SSD |
| Encryption | Installer-supported LUKS layout if desired; keep the recovery material externally |
| Bootloader | GRUB for the project-documented bootable Btrfs snapshot route described below |
| Kernels | Standard Arch kernel plus `linux-lts`, with working NVIDIA modules on both |
| Graphics | AMD for daily desktop use; NVIDIA for workloads that need it |
| Audio | PipeWire, WirePlumber and BlueZ; A2DP AAC/SBC for the Realme neckband |
| Memory | Inspect installer settings first; add one zram setup only if absent |
| Containers | Rootless Podman + crun; reuse this repository's ROS image |

GRUB here is a recovery-workflow choice, not a speed claim. EndeavourOS also offers systemd-boot. If you choose that instead, establish its recovery procedure separately and skip the GRUB commands below. [EndeavourOS overview](https://endeavouros.com/).

## 1. Back up, download and install

Complete the backup and disk-identification steps in [the fresh-install guide](02-fresh-install.md#1-capture-a-recovery-baseline). Both SSDs have similar model strings: verify the intended Linux disk by its locally recorded serial, size and existing partitions. Fresh Linux installation does not authorize erasing Windows.

Get the ISO, checksum and signature from the [EndeavourOS download page](https://endeavouros.com/download/). Follow its verification links; do not reuse a CachyOS checksum or signing key. Use UEFI boot and the firmware settings required by the current EndeavourOS installer. Keep AC connected.

In the live environment:

- Test keyboard, touchpad, Wi-Fi, speakers, brightness and Bluetooth pairing.
- Use the online installer to select KDE and current packages when connectivity permits.
- Select the Linux SSD, Btrfs and the intended bootloader. Use an EFI partition on the Linux SSD.
- If the installer's automatic layout cannot clearly preserve the other disk, use its manual layout workflow and review every planned operation.
- Confirm the Windows SSD and its partitions have no formatting or deletion actions in the final summary.

The partition sizes and free-space budget in the main guide are planning aids. Use the actual mountpoints and encryption combination supported by this installer. Do not copy another distro's `/etc/fstab`, initramfs configuration or boot files onto the new system.

## 2. Update and establish a hardware baseline

After first login:

```bash
sudo pacman -Syu
# Reboot through KDE, then inspect:
cat /etc/os-release
uname -r
lspci -nnk
nvidia-smi
systemctl --failed
systemctl --user --failed
```

Let the installer and current EndeavourOS hardware tooling select the NVIDIA package family. Do not run `chwd`, install `linux-cachyos` or add CachyOS repositories as part of this path. If `nvidia-smi` fails, resolve that before CUDA or GPU containers.

For the fallback kernel, use EndeavourOS's AKM when available, or install the standard kernel packages deliberately. AKM's `--connect-header` option associates headers with the chosen kernel, which is useful for DKMS modules. [AKM documentation](https://discovery.endeavouros.com/akm/).

```bash
# Package inspection is read-only:
pacman -Si linux-lts linux-lts-headers
# Installs the LTS kernel and headers, but does not choose NVIDIA modules for you:
sudo pacman -Syu --needed linux-lts linux-lts-headers
```

Before rebooting into LTS, inspect the NVIDIA setup:

```bash
pacman -Qs nvidia
pacman -Q linux linux-lts
# If the driver uses DKMS:
dkms status
```

A DKMS installation needs matching headers for every target kernel and a successful build for each. Prebuilt modules need their corresponding kernel-specific packages. Use the current EndeavourOS driver guidance to resolve that choice; installing headers alone does not install a graphics module. Confirm boot entries and initramfs generation completed without errors. Then boot LTS and repeat `nvidia-smi`, Wi-Fi and audio checks.

## 3. Audio and basic development tools

Check what the installer already provided:

```bash
pacman -Q pipewire pipewire-pulse wireplumber bluez bluez-utils
systemctl --user status pipewire pipewire-pulse wireplumber
systemctl status bluetooth
```

For a fresh PipeWire-based installation, install missing tools as needed:

```bash
sudo pacman -Syu --needed bluez bluez-utils pipewire pipewire-pulse wireplumber pavucontrol
sudo systemctl enable --now bluetooth.service
```

Review any audio-server replacement prompt rather than accepting conflicts automatically. Log out and back in if user-session services need activation. Pair the neckband and follow [the Realme guide](04-bluetooth-audio.md), especially laptop-microphone selection and the AAC/SBC comparison.

For a small development baseline:

```bash
sudo pacman -Syu --needed base-devel git cmake ninja clang gdb ccache \
  python uv ripgrep fd jq tmux btop lm_sensors restic pacman-contrib
sudo pacman -Syu --needed podman crun distrobox
```

These use ordinary Arch-family package names. Check availability on the installed EndeavourOS system. This repository's `packages.sh --apply` remains CachyOS-only; its preview can help you review optional embedded/CAD groups without weakening that guard.

## 4. Power and memory

Inspect the active power manager and keep one policy owner:

```bash
systemctl is-active power-profiles-daemon tlp tuned
powerprofilesctl list
```

If power-profiles-daemon is the installed manager, start with `powerprofilesctl set balanced`. Do not add TLP or tuned on top of it. Keep the CPU/build concurrency advice from [the performance chapter](03-performance-and-hardware.md).

Check swap before configuring anything:

```bash
zramctl
swapon --show
```

**Only if no zram setup exists**, inspect `/etc/systemd/zram-generator.conf`, its drop-ins and the corresponding `/usr/lib/systemd/` configuration. If another service manages zram, use that service's configuration instead.

For a fresh system without a competing setup:

```bash
sudo pacman -Syu --needed zram-generator
sudoedit /etc/systemd/zram-generator.conf
```

Add this initial configuration, preserving unrelated settings:

```ini
[zram0]
zram-size = ram / 2
```

Reboot at a convenient point and verify with `zramctl` and `swapon --show`. On this laptop that gives roughly 7.5 GiB of logical compressed swap capacity, not additional physical RAM. The half-RAM value is a starting point; measure memory pressure before increasing it. To undo this new setup, remove only the stanza/file you added and reboot. Do not disable active swap under memory pressure. [Upstream zram-generator configuration](https://github.com/systemd/zram-generator).

## 5. Recovery: choose one snapshot system

For the GRUB/Btrfs path selected here, EndeavourOS documents **Timeshift + grub-btrfs**. Follow the [project's complete recovery setup](https://discovery.endeavouros.com/btrfs-with-timeshift-snapshots-on-the-grub-menu/) and check it against the installed package versions. Its article includes older configuration details, so inspect actual service definitions before editing them.

Your acceptance checklist is:

- [ ] Timeshift accepts the installed Btrfs subvolume layout.
- [ ] A manually created snapshot is listed and can be inspected.
- [ ] GRUB integration finds the snapshots and its service starts successfully.
- [ ] A snapshot boot is tested, and the documented permanent-restore procedure is understood.
- [ ] Snapshot coverage and boot/EFI recovery are recorded separately from home-data backups.

Automatic pre-update hooks are optional and may involve an AUR package; inspect that package before adopting it. Do not install both Timeshift and Snapper automation over the same layout just to follow both guides. If you prefer Snapper, choose and validate a coherent Snapper procedure instead.

The CachyOS maintenance chapter's `snapper -c root` commands do not apply to a Timeshift-managed system. Weekly update discipline, external restic backup, disk-space review and the hardware regression checks still apply.

## 6. Reuse and verify the robotics environment

Clone this private repository using your preferred GitHub authentication, then run from its root:

```bash
podman info --format '{{.Host.Security.Rootless}} {{.Host.OCIRuntime.Name}}'
podman build -t localhost/robotics-jazzy -f containers/ros/Containerfile .
# Terminal A:
bash scripts/ros.sh ros2 run demo_nodes_cpp talker
# Terminal B:
bash scripts/ros.sh ros2 run demo_nodes_py listener
```

Expect rootless operation, crun and received messages. Continue with [ROS networking/USB/GUI](06-containers-and-ros.md) and [AI/ML](08-ai-ml.md) only after the base host passes its tests. The earlier container tests were performed on CachyOS; these steps still need execution on your new EndeavourOS host.
