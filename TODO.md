# Workstation TODOs

Unchecked boxes are actions for the laptop owner, not claims of completed setup.

Use the [first-weekend plan](docs/15-first-weekend.md) for execution order and the [acceptance record](templates/acceptance-record.md) to keep actual results. For EndeavourOS, substitute its [installation chapter](docs/14-endeavouros-install.md) for CachyOS-specific steps.

## Before reinstalling — required

- [ ] Read the distro comparison and agree with its rolling-release tradeoff.
- [ ] Back up projects, documents, dotfiles, SSH/GPG material, browser data, password vault and unpushed Git work to an external destination.
- [ ] Export package lists; record boot layout and current audio settings outside the disk being erased.
- [ ] Restore several files from backup; verify access to GitHub after reinstall.
- [ ] Save Windows recovery/BitLocker information if applicable; disable Windows Fast Startup.
- [ ] Identify **both SSDs by model, capacity and serial locally**, and mark the Linux target.
- [ ] Download and verify the selected distro's current ISO; prepare recovery media.
- [ ] Boot live USB in UEFI mode; test keyboard, touchpad, Wi-Fi, screen brightness, audio and external monitor.
- [ ] Decide encryption. Prefer LUKS for laptop data when the current installer/bootloader supports the desired layout.
- [ ] Review the installer's complete partition summary. Preserve the Windows disk and its EFI partition.

## Install and first boot

- [ ] Install KDE Plasma + Btrfs to the Linux SSD, with a separate EFI partition on that SSD.
- [ ] Keep the installer-supported bootloader; verify both main and LTS kernel entries.
- [ ] Complete a full update on AC power and reboot.
- [ ] Validate `nvidia-smi`, AMD graphics, Wi-Fi, Bluetooth, webcam and microphone.
- [ ] Confirm the chosen snapshot manager is configured and bootable recovery is available for the chosen bootloader (Snapper on the CachyOS path, Timeshift on the described EndeavourOS path).
- [ ] Confirm one power-management service, active zram and periodic SSD TRIM.
- [ ] Install the core tools; restore projects selectively rather than copying all old configuration.

## Audio acceptance — high priority

- [ ] Pair Realme neckband, test AAC if offered and SBC fallback.
- [ ] Select built-in laptop microphone for music + calls without headset profile switching.
- [ ] Test the neckband microphone separately and record the quality tradeoff.
- [ ] Play audio for 30 minutes while browsing and compiling; record dropouts.
- [ ] Repeat using 5 GHz Wi-Fi and with phone multipoint disconnected.
- [ ] Suspend/resume five times and test reconnect; repeat after a cold boot.
- [ ] Record profile, kernel, codec and outcome in [the test matrix](docs/04-bluetooth-audio.md#acceptance-matrix).

## Development readiness

- [ ] Install Podman group and verify rootless operation.
- [ ] Build the supplied ROS image; run talker/listener in two terminals.
- [ ] Build a small ROS package and check that host files remain owned by your user.
- [ ] Set up GUI robotics only when needed; verify RViz rendering.
- [ ] Validate NVIDIA CDI and a real CUDA tensor operation before adding ML projects.
- [ ] Verify a USB serial board and debug probe as a normal user.
- [ ] Flash a blinky example; set a breakpoint; read UART output.
- [ ] Complete one ROS bag replay and one simulator exercise.
- [ ] Complete the [synthetic sensor recording/replay lab](docs/16-first-sensor-lab.md) before connecting real sensors.
- [ ] Run the [temperature-monitor project](docs/19-temperature-monitor-project.md), including its threshold, missing-data and recovery checks.
- [ ] If working with a companion computer, verify its Ethernet route, ROS discovery and timestamp assumptions using the [networking guide](docs/17-robot-networking-and-can.md).

## Reliability and capacity

- [ ] Restore a file from an external backup after installation.
- [ ] Boot the LTS kernel and check NVIDIA + Bluetooth there.
- [ ] Rehearse snapshot recovery using the installed bootloader's documented procedure.
- [ ] Keep roughly 70–90 GiB free; inspect images, datasets and snapshots monthly.
- [ ] Establish a weekly update window and re-run the short hardware/audio test afterward.
- [ ] Review [the learning path](docs/09-learning-path.md) every two weeks.
- [ ] Archive a known-good container image and back up its project data separately; follow [environment recovery](docs/18-offline-and-environment-backup.md).
- [ ] Before field work, rehearse the actual project with internet access unavailable.
