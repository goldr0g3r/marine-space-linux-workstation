# Fresh installation playbook

## 1. Capture a recovery baseline

Use an external drive or another machine for backups. A directory on the Linux SSD will be erased with the install. Record these results privately:

```bash
lsblk -o NAME,SIZE,MODEL,SERIAL,FSTYPE,MOUNTPOINTS
findmnt /
findmnt /boot/efi
pacman -Qqe > explicit-packages.txt
pacman -Qqm > foreign-packages.txt
efibootmgr > uefi-boot-entries.txt
```

Export browser/password-manager recovery data, unpushed code, SSH/GPG keys, development certificates and any container volumes holding unique data. Keep secrets encrypted. Verify a restore before proceeding. Save the Windows recovery key if BitLocker/device encryption is enabled; firmware or boot changes can trigger recovery.

The observed layout has **Windows and Linux on separate SSDs**. A fresh Linux installation does not require touching Windows. Preserve that disk unless you separately decide to remove Windows. Never identify a target by `nvme0n1` versus `nvme1n1` alone: enumeration can change. When inspected, Linux was on the `SAMSUNG MZVLQ512HBLU` (476.9 GiB) and Windows on the `Samsung SSD 980 500GB` (465.8 GiB). Both are Samsung drives of similar size, so confirm model, capacity and existing partitions together.

The firmware held 29 UEFI boot entries when first inspected. The 25 dead ones, left by earlier installations, were removed on 11 November 2026. Four remain: Windows Boot Manager, the current CachyOS entry, the fallback `UEFI OS` loader and the firmware's PXE entry. A reinstall adds a new entry and can leave the old CachyOS one behind. Keep the saved `efibootmgr` list. After the new system boots, remove only entries you have identified as dead, one at a time, with `sudo efibootmgr -b XXXX -B`. Never delete Windows Boot Manager or the entry you booted from.

## 2. Prepare and test the installer

Use the current [CachyOS download and verification instructions](https://wiki.cachyos.org/cachyos_basic/download/). Match the ISO's checksum against the published checksum and follow signature verification when provided. Use a graphical USB image writer and inspect its selected USB device before writing.

In firmware, use UEFI mode and disable CSM. The current CachyOS install guide requires Secure Boot disabled during installation; configure it later only using the distribution's supported procedure. Do not change storage-controller settings casually. In Windows, turn off Fast Startup and fully shut down before manipulating shared disks. [Installation guide](https://wiki.cachyos.org/installation/installation_on_root/).

Boot live media and check Wi-Fi, touchpad, keyboard, brightness, speakers, webcam, Bluetooth pairing and external display. Live media is a screening test; repeat after installation with the final NVIDIA driver. Keep AC power connected and retain another way to read recovery instructions.

## 3. Disk layout

Recommended conceptual layout for the **Linux SSD only**:

| Area | Suggested size | Purpose |
|---|---:|---|
| EFI system partition | FAT32, sized for the bootloader: at least 4 GiB for Limine, 2 GiB for systemd-boot or rEFInd, 512 MiB for GRUB | Boot assets; Limine, systemd-boot and rEFInd mount it at `/boot`, GRUB at `/boot/efi` |
| Linux filesystem | Remaining space | Btrfs, encrypted if supported by your selected installer layout |
| Root/home separation | Btrfs subvolumes | Flexible capacity; avoid a small fixed root partition |
| Swap | zram initially | Memory pressure handling; no hibernation in this baseline |

These are planning sizes, not partitioning commands. Follow the installer's supported encryption and bootloader combination. A root snapshot usually excludes separate home and other nested subvolumes. ESP contents also need separate recovery handling.

Choose the bootloader before partitioning, because it fixes the EFI partition's size and mountpoint. In UEFI mode the CachyOS installer offers Limine, systemd-boot, rEFInd and GRUB. CachyOS provides bootable Btrfs snapshots for Limine (`limine-snapper-sync`, enabled by default with Btrfs) and for GRUB (`grub-btrfs-support`); systemd-boot and rEFInd need a custom setup for that. GRUB is the option that supports an encrypted `/boot`, with limited LUKS2 support; the others keep `/boot` unencrypted. The existing installation uses GRUB with a 512 MiB EFI partition, and the install guide's dual-boot section labels its GRUB instructions “only for older installations”, so do not carry that layout over by habit. [Boot manager comparison](https://wiki.cachyos.org/installation/boot_managers/), [partition requirements](https://wiki.cachyos.org/installation/installation_on_root/).

The same guide cautions that the installer's “Install alongside” and “Replace partition” options are not fully reliable and prefers manual partitioning.

Use a fresh EFI partition on the Linux SSD so Windows recovery is independent. Prefer the current installer's Btrfs defaults instead of inventing a subvolume scheme. Review every format/delete action in the final summary; the Windows disk must show no destructive changes. If you cannot identify the target confidently, stop the installation and resolve it first.

Hibernation is a separate project: zram cannot store a resume image across power-off. Btrfs swapfiles, encrypted swap and resume configuration require deliberate setup. Suspend is the initial target.

## 4. Capacity budget

On roughly 475 GiB usable Linux capacity, aim for:

| Category | Planning allowance |
|---|---:|
| OS, applications, package cache | 55 GiB |
| Source trees and active builds | 70 GiB |
| Container images and SDKs | 70 GiB |
| Datasets, small models and ROS recordings | 90 GiB |
| Personal data | 70 GiB |
| Snapshot growth allowance | 30 GiB |
| Free operating headroom | 90 GiB |

These are soft budgets, not partitions. Shared Btrfs snapshot extents complicate accounting. Move old recordings/datasets to external storage before expanding the container library. Keep at least roughly 15–20% available as a practical operating target.

## 5. First boot

```bash
sudo pacman -Syu
# Reboot after the update through KDE, then:
uname -r
nvidia-smi
systemctl --failed
systemctl --user --failed
wpctl status
zramctl
swapon --show
```

Install the core package group after reviewing it:

```bash
bash scripts/packages.sh core
bash scripts/packages.sh core --apply
sudo systemctl enable --now bluetooth.service
systemctl --user status pipewire pipewire-pulse wireplumber
systemctl status fstrim.timer
```

If TRIM is not scheduled and the storage stack supports it, enable `fstrim.timer`. Check encrypted-discard policy before altering LUKS options. Do not replace the installer-selected NVIDIA packages with an NVIDIA `.run` installer. Use CachyOS Kernel Manager/hardware detection for matching kernel modules. [chwd documentation](https://wiki.cachyos.org/features/chwd/chwd/).

Use CachyOS Hello's snapshot setup if a root Snapper configuration is absent; then verify the actual bootloader integration (`limine-snapper-sync` for Limine, `grub-btrfs-support` for GRUB). Restore dotfiles selectively. Old WirePlumber, power-manager and GPU overrides can reintroduce problems on a clean install.
