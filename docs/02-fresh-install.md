# Fresh installation playbook

## 1. Capture a recovery baseline

Use an external drive or another machine for backups. A directory on the Linux SSD will be erased with the install. Record these results privately:

```bash
lsblk -o NAME,SIZE,MODEL,SERIAL,FSTYPE,MOUNTPOINTS
findmnt /
findmnt /boot/efi
pacman -Qqe > explicit-packages.txt
pacman -Qqm > foreign-packages.txt
```

Export browser/password-manager recovery data, unpushed code, SSH/GPG keys, development certificates and any container volumes holding unique data. Keep secrets encrypted. Verify a restore before proceeding. Save the Windows recovery key if BitLocker/device encryption is enabled; firmware or boot changes can trigger recovery.

The observed layout has **Windows and Linux on separate SSDs**. A fresh Linux installation does not require touching Windows. Preserve that disk unless you separately decide to remove Windows. Never identify a target by `nvme0n1` versus `nvme1n1` alone: both model strings are similar and enumeration can change.

## 2. Prepare and test the installer

Use the current [CachyOS download and verification instructions](https://wiki.cachyos.org/cachyos_basic/download/). Match the ISO's checksum against the published checksum and follow signature verification when provided. Use a graphical USB image writer and inspect its selected USB device before writing.

In firmware, use UEFI mode and disable CSM. The current CachyOS install guide requires Secure Boot disabled during installation; configure it later only using the distribution's supported procedure. Do not change storage-controller settings casually. In Windows, turn off Fast Startup and fully shut down before manipulating shared disks. [Installation guide](https://wiki.cachyos.org/installation/installation_on_root/).

Boot live media and check Wi-Fi, touchpad, keyboard, brightness, speakers, webcam, Bluetooth pairing and external display. Live media is a screening test; repeat after installation with the final NVIDIA driver. Keep AC power connected and retain another way to read recovery instructions.

## 3. Disk layout

Recommended conceptual layout for the **Linux SSD only**:

| Area | Suggested size | Purpose |
|---|---:|---|
| EFI system partition | 1–2 GiB FAT32 on a fresh layout | Boot assets; use the mountpoint required by the chosen installer/bootloader |
| Linux filesystem | Remaining space | Btrfs, encrypted if supported by your selected installer layout |
| Root/home separation | Btrfs subvolumes | Flexible capacity; avoid a small fixed root partition |
| Swap | zram initially | Memory pressure handling; no hibernation in this baseline |

These are planning sizes, not partitioning commands. Follow the installer's supported encryption and bootloader combination. A root snapshot usually excludes separate home and other nested subvolumes. ESP contents also need separate recovery handling.

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

Use CachyOS Hello's snapshot setup if a root Snapper configuration is absent; then verify the actual bootloader integration. Restore dotfiles selectively. Old WirePlumber, power-manager and GPU overrides can reintroduce problems on a clean install.
