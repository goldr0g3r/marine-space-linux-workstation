# Ubuntu 24.04.5 LTS: installation

This replaces CachyOS on the Linux SSD and leaves Windows alone. It is a researched procedure and was not performed on the laptop. Next chapter: [snap, Flatpak and apt](02-snap-flatpak-apt.md).

## Target configuration

| Component | Choice |
|---|---|
| Release | Ubuntu 24.04.5 LTS or Kubuntu 24.04.5 LTS |
| Kernel | 7.0 HWE (the desktop default), 6.8 GA installed as a fallback |
| Session | X11 first on Kubuntu (Plasma 5.27); Wayland or X11 on GNOME 46 |
| Linux SSD | `SAMSUNG MZVLQ512HBLU`: 1 GiB EFI partition, ext4 root, optional LUKS |
| Windows SSD | `Samsung SSD 980 500GB`: no changes |
| Bootloader | GRUB with Ubuntu's signed shim, on the Linux SSD's EFI partition |
| Secure Boot | Can stay enabled |
| Swap | Installer's swap file, plus zram added in the [performance chapter](04-performance.md) |
| Recovery | Timeshift (rsync mode) for the system, restic for home |

ext4 is chosen because it is the installer default and the layout vendors test. The Ubuntu Desktop installer's Btrfs option does not reliably create the `@` and `@home` subvolumes that Timeshift's Btrfs mode needs. If you choose Btrfs anyway, check with `sudo btrfs subvolume list /` before relying on snapshots.

## 1. Back up and record the current system

Follow [the recovery baseline](../../02-fresh-install.md#1-capture-a-recovery-baseline). The whole Linux SSD is erased. Push or copy every repository under `~/Projects`, and export container volumes that hold unique data.

Record these outside the disk being erased:

```bash
lsblk -o NAME,SIZE,MODEL,SERIAL,FSTYPE,MOUNTPOINTS
```

```bash
efibootmgr -v > uefi-boot-entries.txt
```

```bash
pacman -Qqe > explicit-packages.txt
```

In Windows: save the BitLocker recovery key if device encryption is on, turn off Fast Startup, and shut down fully.

## 2. Download and verify the ISO

Get the ISO, `SHA256SUMS` and `SHA256SUMS.gpg` from [releases.ubuntu.com/24.04](https://releases.ubuntu.com/24.04/) or [the Kubuntu download page](https://kubuntu.org/getkubuntu/). Put them in one directory.

```bash
sha256sum -c SHA256SUMS --ignore-missing
```

```bash
gpg --keyid-format long --verify SHA256SUMS.gpg SHA256SUMS
```

The first command must print `OK` for the ISO. The second needs Ubuntu's CD image signing key; follow [Ubuntu's verification tutorial](https://ubuntu.com/tutorials/how-to-verify-ubuntu) to import and check it.

Write the USB with a graphical image writer and confirm the selected device before writing.

## 3. Firmware

- UEFI mode, CSM disabled.
- Secure Boot may stay on. Ubuntu boots through a signed shim. If the NVIDIA driver is built by DKMS, the installer or `ubuntu-drivers` asks for a one-time password, and the next boot shows a blue MOK screen where you choose **Enroll MOK** and type it.
- Do not change the storage controller mode.

## 4. Test the live session

Boot the USB and choose **Try**. Check keyboard, touchpad, Wi-Fi, brightness, speakers, webcam, Bluetooth pairing and an external monitor. Stay on AC power.

## 5. Install

Ubuntu Desktop uses its own installer; Kubuntu 24.04 uses Calamares. The choices are the same.

1. Choose the interactive install and the default (not minimal) selection.
2. If offered, tick **third-party software for graphics and Wi-Fi hardware**. Set the Secure Boot password it asks for. If it is not offered, the driver is installed in section 7.
3. Disk setup. Use one of these:
   - **Erase disk**, select the `MZVLQ512HBLU` disk by model and size, and enable encryption there if you want LUKS.
   - **Manual partitioning** on that disk: 1 GiB FAT32 mounted at `/boot/efi` with the boot flag, the rest as ext4 mounted at `/`. Set the bootloader device to the same disk.
4. Do not create a swap partition.
5. Read the summary. The `Samsung SSD 980` disk must show no format, delete or bootloader action. If it does, go back.

Never choose the target by `nvme0n1` or `nvme1n1` alone; the numbering can change between boots.

## 6. First boot

```bash
sudo apt update && sudo apt full-upgrade
```

Reboot, then confirm the boot files went to the Linux SSD:

```bash
findmnt /boot/efi
```

```bash
efibootmgr -v
```

The `ubuntu` entry should point at a partition on the `MZVLQ512HBLU` disk. Remove the dead CachyOS entry only after identifying it, with `sudo efibootmgr -b XXXX -B`. Never remove Windows Boot Manager.

Baseline checks:

```bash
cat /etc/os-release && uname -r
```

```bash
systemctl --failed
```

```bash
systemctl --user --failed
```

## 7. Graphics driver

```bash
ubuntu-drivers devices
```

```bash
sudo ubuntu-drivers install
```

This installs the recommended packaged NVIDIA driver. Do not use NVIDIA's `.run` installer. Reboot, complete MOK enrolment if prompted, then:

```bash
nvidia-smi
```

```bash
prime-select query
```

`on-demand` is the right mode: AMD drives the desktop and NVIDIA is used when asked. Set it with `sudo prime-select on-demand` and log out if it is anything else.

## 8. Fallback kernel

The HWE kernel is 7.0. Install the 6.8 GA kernel beside it so there is a different kernel series to boot if an update regresses:

```bash
sudo apt install linux-generic
```

Make the GRUB menu visible. In `/etc/default/grub` set `GRUB_TIMEOUT_STYLE=menu` and `GRUB_TIMEOUT=3`, then:

```bash
sudo update-grub
```

Boot the 6.8 entry once from **Advanced options** and check `nvidia-smi`, Wi-Fi and audio there. A fallback kernel without a working graphics module is not a fallback.

## 9. Windows in the boot menu

If Windows is missing from GRUB, set `GRUB_DISABLE_OS_PROBER=false` in `/etc/default/grub` and run `sudo update-grub`. The firmware boot menu (Esc at power-on on this ASUS) always works as well.

Windows and Linux disagree about the hardware clock. Keep Linux on UTC and tell Windows to use UTC, following [Ubuntu's time management notes](https://help.ubuntu.com/community/UbuntuTime).

## 10. Base tools and recovery

```bash
sudo apt install build-essential git cmake ninja-build clang gdb ccache \
  python3-venv python3-pip pipx ripgrep fd-find jq tmux btop lm-sensors \
  curl wget timeshift restic
```

```bash
sudo usermod -aG dialout,plugdev "$USER"
```

Log out and back in for the groups to apply. Create a first Timeshift snapshot in rsync mode, then restore one file from it to prove it works. Timeshift excludes home by default; back up home with restic to an external disk.

Firmware updates:

```bash
fwupdmgr get-updates
```

## Acceptance checks

- [ ] `findmnt /boot/efi` shows the Linux SSD.
- [ ] Windows boots, and its disk is unchanged.
- [ ] `nvidia-smi` works on both the 7.0 and 6.8 kernels.
- [ ] `prime-select query` prints `on-demand`.
- [ ] Wi-Fi, Bluetooth, webcam, microphone and brightness keys work.
- [ ] Five suspend and resume cycles succeed.
- [ ] A Timeshift snapshot exists and a file restore was tested.

Continue with [snap, Flatpak and apt](02-snap-flatpak-apt.md).
