# Ubuntu 26.04.1 LTS: installation

This replaces CachyOS on the Linux SSD and leaves Windows alone. It is a researched procedure and was not performed on the laptop. Next chapter: [snap, Flatpak and apt](02-snap-flatpak-apt.md).

Read [the decision](../01-distro-decision.md) first. On 14 November 2026 the MATLAB ROS Toolbox did not list 26.04, and 24.04 scored higher for that reason. Choose this guide if you do not need that toolbox, are willing to run it in a 24.04 container, or MathWorks has since added support.

## Target configuration

| Component | Choice |
|---|---|
| Release | Ubuntu 26.04.1 LTS or Kubuntu 26.04.1 LTS |
| Kernel | 7.0, which is both the GA and HWE kernel on this release |
| Session | Wayland: GNOME 50 has no X11 session; Kubuntu ships Plasma 6 |
| Linux SSD | `SAMSUNG MZVLQ512HBLU`: 1 GiB EFI partition, ext4 root, optional LUKS |
| Windows SSD | `Samsung SSD 980 500GB`: no changes |
| Bootloader | GRUB with Ubuntu's signed shim, on the Linux SSD's EFI partition |
| Secure Boot | Can stay enabled |
| Swap | Installer's swap file, plus zram added in the [performance chapter](04-performance.md) |
| Recovery | Timeshift (rsync mode) for the system, restic for home |

ext4 is chosen because it is the installer default and the layout vendors test. If you choose Btrfs, check with `sudo btrfs subvolume list /` that `@` and `@home` exist before relying on Timeshift's Btrfs mode.

## What is different from 24.04

| Area | 26.04 |
|---|---|
| Initramfs | Dracut. Regenerate with `sudo dracut --regenerate-all --force` |
| `sudo` | sudo-rs. The original is available as `sudo.ws` |
| Core utilities | Rust coreutils. GNU versions are available with a `gnu` prefix |
| Time sync | Chrony |
| APT | 3.1 |
| Python / GCC | 3.14 / 15.2 |
| Software & Updates | Not installed by default; `sudo apt install software-properties-gtk` |
| Disk encryption | Adds TPM-backed encryption beside passphrase LUKS |
| NVIDIA | Wayland fully supported; driver suspend and resume enabled by default |

## 1. Back up and record the current system

Follow [the recovery baseline](../../02-fresh-install.md#1-capture-a-recovery-baseline). The whole Linux SSD is erased. Push or copy every repository under `~/Projects`, and export container volumes that hold unique data.

The old installation was 88% full, which slows this type of SSD. Restore selectively onto the new system; do not copy the whole home directory back. See [the hardware profile](../02-hardware-profile.md#storage).

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

Get the ISO, `SHA256SUMS` and `SHA256SUMS.gpg` from [releases.ubuntu.com/26.04](https://releases.ubuntu.com/26.04/) or [the Kubuntu download page](https://kubuntu.org/getkubuntu/). Put them in one directory.

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
- The installed BIOS is `FA706IC.302` from December 2022. Check ASUS's support page for a newer version and apply it, on AC power, before installing.

## 4. Test the live session

Boot the USB and choose **Try**. Check keyboard, touchpad, Wi-Fi, brightness, speakers, webcam, Bluetooth pairing and an external monitor. Also suspend and resume the live session once; it is an early warning for the suspend reports described below. Stay on AC power.

## 5. Install

1. Choose the interactive install and the default (not minimal) selection.
2. If offered, tick **third-party software for graphics and Wi-Fi hardware**. Set the Secure Boot password it asks for. If it is not offered, the driver is installed in section 7.
3. Disk setup. Use one of these:
   - **Erase disk**, select the `MZVLQ512HBLU` disk by model and size, and enable encryption there if you want it.
   - **Manual partitioning** on that disk: 1 GiB FAT32 mounted at `/boot/efi` with the boot flag, the rest as ext4 mounted at `/`. Set the bootloader device to the same disk.
4. For encryption choose **passphrase LUKS**, not the TPM-backed option. The release notes say TPM-backed encryption still has limitations, and this laptop depends on a third-party kernel module. Read [Ubuntu's notes](https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/) before deciding otherwise.
5. Do not create a swap partition.
6. Read the summary. The `Samsung SSD 980` disk must show no format, delete or bootloader action. If it does, go back.

Never choose the target by `nvme0n1` or `nvme1n1` alone; the numbering can change between boots. Both SSDs also report the same PCI device ID, so tools that list hardware IDs cannot tell them apart.

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
sudo ubuntu-drivers install --recommended
```

Ubuntu supports only drivers installed this way. For the newest packaged branch use `sudo ubuntu-drivers install nvidia:595`. Do not use NVIDIA's `.run` installer. Reboot, complete MOK enrolment if prompted, then:

```bash
nvidia-smi
```

```bash
prime-select query
```

`on-demand` is the right mode: AMD drives the desktop and NVIDIA is used when asked. Set it with `sudo prime-select on-demand` and log out if it is anything else.

## 8. Fallback kernel

26.04 has one kernel series, so the fallback is the previous 7.0 build. Ubuntu keeps it automatically; do not remove old kernels by hand until the new one has passed your checks.

Make the GRUB menu visible. In `/etc/default/grub` set `GRUB_TIMEOUT_STYLE=menu` and `GRUB_TIMEOUT=3`, then:

```bash
sudo update-grub
```

```bash
dpkg -l 'linux-image-7*' | grep ^ii
```

**Suspend.** Several forum and bug reports describe suspend hangs on NVIDIA hybrid laptops with early 7.0 builds on 26.04 (7.0.0-14 and 7.0.0-15 are named). No confirmation of a fix was found during research, and none of the reports is for this laptop model. Test it:

1. Run five suspend and resume cycles on the current kernel.
2. Repeat after every kernel or NVIDIA driver update.
3. If a new kernel fails, boot the previous one from **Advanced options** and hold the kernel:

```bash
sudo apt-mark hold linux-image-generic linux-headers-generic
```

Release the hold with `sudo apt-mark unhold` once a fixed build is published. If suspend never works reliably, that is a reason to use [the 24.04 guide](../24.04/01-install.md), where a 6.8 kernel is available.

## 9. Windows in the boot menu

If Windows is missing from GRUB, set `GRUB_DISABLE_OS_PROBER=false` in `/etc/default/grub` and run `sudo update-grub`. The firmware boot menu (Esc at power-on on this ASUS) always works as well.

Windows and Linux disagree about the hardware clock. Keep Linux on UTC and tell Windows to use UTC, following [Ubuntu's time management notes](https://help.ubuntu.com/community/UbuntuTime).

## 10. Base tools and recovery

```bash
sudo apt install build-essential git cmake ninja-build clang gdb ccache \
  python3-venv python3-pip pipx ripgrep fd-find jq tmux btop lm-sensors \
  curl wget timeshift restic software-properties-common
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
- [ ] `nvidia-smi` works, and two 7.0 kernel builds are installed.
- [ ] `prime-select query` prints `on-demand`.
- [ ] Wi-Fi, Bluetooth, webcam, microphone and brightness keys work.
- [ ] Five suspend and resume cycles succeed.
- [ ] A Timeshift snapshot exists and a file restore was tested.

Continue with [snap, Flatpak and apt](02-snap-flatpak-apt.md).
