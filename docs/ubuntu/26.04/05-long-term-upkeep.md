# Ubuntu 26.04: staying fast for years

Previous: [performance](04-performance.md).

A tuned system does not stay fast by itself. It slows down for a small number of ordinary reasons: the disk fills, images and caches pile up, an update changes a driver, dust raises temperatures, the battery wears, and background software accumulates. This chapter is the routine that prevents each of those, and the checklist for when something does get slower.

Researched procedure; not yet run on this laptop.

## Schedule

| When | What | Section |
|---|---|---|
| Weekly | Update, reboot, quick check | 1 |
| Monthly | Disk hygiene, backup verification | 3, 6 |
| Quarterly | Re-run the benchmarks, hardware health | 5, 4 |
| Twice a year | Review vendor support and third-party sources | 2 |
| Yearly | Clean the cooling system, review the battery | 4 |

## 1. Update discipline

Most "it worked yesterday" problems on a robotics workstation come from a driver or kernel changing underneath a running session.

### Weekly routine

On AC power, with work saved:

```bash
sudo timeshift --create --comments "before weekly update"
```

```bash
sudo apt update && sudo apt full-upgrade
```

```bash
flatpak update && sudo snap refresh
```

```bash
cat /var/run/reboot-required 2>/dev/null; cat /var/run/reboot-required.pkgs 2>/dev/null
```

Reboot if that file exists, then run the two-minute check:

```bash
systemctl --failed; nvidia-smi --query-gpu=driver_version --format=csv,noheader; prime-select query; powerprofilesctl get
```

After a kernel or NVIDIA update also run `flatpak update` once more, test suspend, and start RViz.

### Stop the graphics stack changing mid-week

`unattended-upgrades` installs security updates in the background. When it updates the NVIDIA libraries while the old kernel module is still loaded, `nvidia-smi` and CUDA fail with `Driver/library version mismatch` until the next reboot, which can kill a long simulation or training run.

Move the kernel and the NVIDIA driver to the weekly manual update, so they change together and only when you are ready to reboot. Create `/etc/apt/apt.conf.d/51unattended-upgrades-graphics`:

```text
Unattended-Upgrade::Package-Blacklist {
    "nvidia-";
    "libnvidia-";
    "xserver-xorg-video-nvidia-";
    "linux-";
};
```

Check that the rule is read:

```bash
sudo unattended-upgrade --dry-run --debug 2>&1 | grep -i -E 'blacklist|nvidia' | head
```

Everything else still updates automatically. The cost is that kernel security fixes wait for your weekly run, so do not skip it. If you would sooner keep kernels automatic, remove the `"linux-";` line and accept that a reboot is needed whenever `/var/run/reboot-required` appears.

### Before a deadline, demo or field day

Freeze what matters for a few days:

```bash
sudo apt-mark hold $(dpkg -l 'linux-generic*' 'linux-image-generic*' 'linux-headers-generic*' | awk '/^ii/{print $2}')
```

```bash
sudo snap refresh --hold=120h
```

Also hold the installed `nvidia-driver-*` package; find its name with `dpkg -l 'nvidia-driver-*' | grep ^ii`. List holds with `apt-mark showhold` and release them with `sudo apt-mark unhold` afterwards. A hold that is forgotten becomes a security problem.

### Phased updates

`apt` sometimes reports upgrades as "deferred due to phasing". Ubuntu releases updates to a fraction of machines at a time and stops if errors are reported. Leave those packages alone; they arrive within days. Forcing them defeats the protection.

### Kernel series: choose GA

Ubuntu Desktop follows the hardware-enablement (HWE) kernel by default. On 26.04 that means the kernel series changes every six months, starting with 26.04.2 in early 2027 and ending with 26.04.5 in 2028. Each change is a chance for an NVIDIA or suspend regression, and this laptop's 2021 hardware gains nothing from newer kernels.

The GA kernel stays on 7.0 for the whole five years. See which you are following:

```bash
apt list --installed 2>/dev/null | grep -E '^linux-(generic|image-generic)'
```

A name ending in `-hwe-26.04` follows HWE. Today both tracks point at 7.0, so switching changes nothing yet. To stay on 7.0:

```bash
sudo apt install linux-generic
```

```bash
sudo apt remove linux-generic-hwe-26.04
```

Then run `sudo ubuntu-drivers install` again so the NVIDIA module package follows the same track, reboot, and confirm with `nvidia-smi`. If you later need a newer kernel for new hardware, reinstall `linux-generic-hwe-26.04`.

## 2. Keep the supported configuration supported

### Ubuntu Pro

Free for personal use on up to five machines. It extends security updates to the `universe` packages that ROS, Gazebo and many libraries depend on, and extends coverage past 2029:

```bash
sudo pro attach
```

```bash
pro status
```

### Release upgrades

Ubuntu will offer interim releases only if asked, and the next LTS in 2028. Do not accept a release upgrade until every tool you depend on lists the new release. Check `/etc/update-manager/release-upgrades`; `Prompt=lts` offers only LTS releases and `Prompt=never` silences the offer.

Dates that set the plan:

| Item | Supported until |
|---|---|
| Ubuntu 26.04 standard support | April 2031 |
| ROS 2 Lyrical | May 2031 |
| ROS 2 Jazzy, used here in a container | May 2029 |

Twice a year, when MathWorks ships a release, check three pages: the [MATLAB Linux requirements](https://www.mathworks.com/support/requirements/matlab-linux.html), the [ROS Toolbox requirements](https://www.mathworks.com/help/ros/gs/ros-system-requirements.html) and the [platform road map](https://www.mathworks.com/support/requirements/platform-road-map.html). When the ROS Toolbox lists 26.04 and targets Lyrical, install it on the host and retire the 24.04 container described in [the toolchain chapter](03-toolchain.md#ros-toolbox-in-a-2404-container-supported-configuration). When a later LTS becomes the supported platform, move to it with a fresh install, not an in-place upgrade; a clean system is faster and carries no leftovers.

### Third-party sources

Every PPA and vendor repository is a way for the base system to drift. Twice a year:

```bash
apt policy | grep -E 'https?://' | sort -u
```

Remove sources you no longer use. `sudo apt install ppa-purge` followed by `sudo ppa-purge ppa:owner/name` removes a PPA and returns its packages to the Ubuntu versions. The list of sources this setup expects is in [the snap chapter](02-snap-flatpak-apt.md#8-third-party-apt-sources).

### Firmware

```bash
fwupdmgr refresh && fwupdmgr get-updates
```

BIOS updates for this laptop come from ASUS and are installed from the firmware's own update tool. The version installed on 14 November 2026 was `FA706IC.302`, from December 2022. Read the release notes; apply them when they mention stability, charging or thermal fixes, and never on battery.

## 3. Disk hygiene

A nearly full SSD is slower and leaves no room for snapshots or builds. Aim for 15 to 20% free.

### See where the space went

```bash
df -h / && sudo ncdu -x /
```

### Clean each consumer

| Consumer | Inspect | Clean |
|---|---|---|
| apt cache and old packages | `du -sh /var/cache/apt` | `sudo apt autoremove --purge && sudo apt clean` |
| System journal | `journalctl --disk-usage` | `sudo journalctl --vacuum-size=200M` |
| Old snap revisions | `snap list --all \| grep disabled` | The loop below |
| Unused Flatpak runtimes | `flatpak list --runtime` | `flatpak uninstall --unused` |
| Container images | `podman system df` | `podman image prune`, then `podman system prune` after reading what it lists |
| Compiler cache | `ccache --show-stats` | `ccache --evict-older-than 30d` |
| ROS logs | `du -sh ~/.ros/log` | `rm -rf ~/.ros/log/*` |
| Workspace `build`, `install`, `log` | `du -sh ~/Projects/*/{build,install,log} 2>/dev/null` | Delete in workspaces you are not using |
| Gazebo model cache | `du -sh ~/.gz` | Delete models you no longer need |
| Python caches | `du -sh ~/.cache/pip ~/.cache/uv 2>/dev/null` | `pip cache purge`, `uv cache prune` |
| MATLAB and Simulink | `du -sh ~/.matlab`; `slprj` folders in projects | Delete `slprj` and generated-code folders of finished projects |
| Crash dumps | `sudo du -sh /var/crash /var/lib/apport/coredump 2>/dev/null` | `sudo rm -f /var/crash/*` |
| Timeshift snapshots | `sudo timeshift --list` | `sudo timeshift --delete --snapshot 'NAME'` |
| ROS bags and datasets | `du -sh` on your data folders | Move finished recordings to external storage |
| Trash | `du -sh ~/.local/share/Trash` | Empty it |

Old snap revisions. This removes only revisions marked disabled:

```bash
snap list --all | awk '/disabled/{print $1, $3}' | while read -r name rev; do sudo snap remove "$name" --revision="$rev"; done
```

Never run `podman system prune --volumes` without checking; volumes can hold data that exists nowhere else.

### Keep it from growing back

- Timeshift: schedule two weekly and one monthly snapshot, plus the manual one before each update. In rsync mode each snapshot costs real space for every changed file.
- The journal cap and snap `refresh.retain=2` from earlier chapters stay in place.
- Record bags to a dated folder and archive at the end of each project. Use compression when recording: `ros2 bag record --compression-mode file --compression-format zstd`.

Confirm TRIM is running:

```bash
journalctl -u fstrim.service --since "-14 days" --no-pager | tail -3
```

## 4. Hardware upkeep

Software cannot fix a hot or worn machine.

### Cooling

Record the sustained temperature and fan speed for a ten-minute build when the laptop is clean. That is the reference.

```bash
sensors | grep -E 'Tctl|fan|edge'
```

- When the same build runs 8 to 10 °C hotter, or `s-tui` shows the frequency dropping earlier than before, clean the fans and vents. Expect to do this about once a year.
- After two to three years, thermal compound may need replacing. Check ASUS's service information for this model first; some ASUS laptops use liquid metal on the CPU, which must not be treated like ordinary paste.
- Use the laptop on a hard surface during heavy work.

### Battery

Holding a lithium battery at 100% on AC ages it. This laptop exposes a charge limit, currently 100.

```bash
cat /sys/class/power_supply/BAT1/charge_control_end_threshold
```

On Kubuntu set the limit in **System Settings → Power Management → Advanced Power Settings**. On Ubuntu Desktop look for **Settings → Power → Preserve Battery Health**. If neither desktop offers it for this battery, create `/etc/systemd/system/battery-charge-limit.service`:

```ini
[Unit]
Description=Limit battery charge to 80%
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/sh -c 'echo 80 > /sys/class/power_supply/BAT1/charge_control_end_threshold'

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now battery-charge-limit.service
```

Use 80 for desk use and set it back to 100 the evening before a field day. Check wear twice a year; capacity is `energy-full` divided by `energy-full-design`:

```bash
upower -i "$(upower -e | grep BAT)" | grep -E 'energy-full|capacity|cycles'
```

### SSD

Quarterly:

```bash
sudo nvme smart-log /dev/nvme0 | grep -E 'percentage_used|available_spare|media_errors|temperature'
```

The Linux SSD has no DRAM cache, so its speed depends on free space more than most; keep it under about 80% full. `percentage_used` climbing quickly means something is writing constantly; find it with `sudo iotop-c -ao`. Any non-zero `media_errors` means back up now.

### Memory

After changing RAM (the planned 8 + 16 GB), confirm both modules are seen and test them before trusting long simulations:

```bash
sudo dmidecode -t memory | grep -E 'Size|Speed|Locator'
```

```bash
sudo apt install memtest86+
```

Choose the memory test from the GRUB menu and let it complete at least one full pass. Afterwards raise the build job counts from [the performance chapter](04-performance.md#10-build-speed).

## 5. Regression watch

Keep the baseline file and the results worksheet from [the performance chapter](04-performance.md#17-results-worksheet). Re-run the same measurements quarterly and after any kernel or NVIDIA driver update.

### Five-minute health check

```bash
systemctl --failed; journalctl -p 3 -b --no-pager | tail -20
```

```bash
uname -r; cat /proc/cmdline; powerprofilesctl get; swapon --show; df -h / | tail -1
```

```bash
glxinfo -B | grep -E 'renderer|Accelerated'; cat /sys/bus/pci/devices/0000:01:00.0/power/runtime_status
```

| Check | Healthy |
|---|---|
| Failed units | None |
| Kernel command line | Still contains `preempt=full` |
| Power profile on AC | `performance` |
| Swap | zram at priority 100 |
| Root filesystem | Under 85% used |
| Renderer | AMD Radeon, accelerated |
| NVIDIA at idle | `suspended` |

### When it feels slower

Work down the table; the causes are listed from most to least common.

| Symptom | Check | Likely cause and fix |
|---|---|---|
| Everything is choppy | Display settings, or `kscreen-doctor -o` on Kubuntu | Display fell back to 60 Hz after an update or a monitor change. Set 144 Hz |
| Desktop lags, fans quiet | `glxinfo -B \| grep renderer` | `llvmpipe`: the graphics driver broke. Reboot; if it persists, `sudo ubuntu-drivers install` and `flatpak update` |
| Slow after an update | `powerprofilesctl get` | Profile reset to `balanced`. Set `performance` |
| Stutter with memory full | `swapon --show`, `cat /proc/pressure/memory` | zram not active, or genuinely out of memory. Fix the zram unit, lower build jobs |
| Hitches during builds | `sudo dmesg \| grep -i 'dynamic preempt'` | `preempt=full` lost from `/etc/default/grub` after a package rewrote it |
| Slow, hot, loud | `s-tui`, `sensors` | Thermal throttling. Clean the cooling system |
| Constant disk activity | `sudo iotop-c -ao`, `balooctl6 status` or `localsearch status` | File indexer or a snap refresh. Exclude folders; check `snap changes` |
| High idle CPU | `systemd-cgtop`, `btop` | A background service or browser tab. Identify before disabling |
| Slow file operations | `df -h /` | Disk over 85% full. Run section 3 |
| Slow boot | `systemd-analyze blame \| head` | A new service waiting on the network or a timeout |
| Battery drains fast | `cat /sys/bus/pci/devices/0000:01:00.0/power/runtime_status` | NVIDIA GPU held awake. Find the process with `nvidia-smi` |
| `nvidia-smi` mismatch error | `cat /var/run/reboot-required` | Driver updated without a reboot. Reboot |
| Suspend stopped working | `journalctl -b -1 -p 3 \| tail` | Kernel or driver regression. Boot the previous kernel build and hold the kernel packages |
| Applications start slowly | `snap list` | A snap replaced a Flatpak or apt application. Reinstall from the preferred source |

If the cause is a recent update and none of the above fixes it, restore the Timeshift snapshot taken before that update, then hold the package and look for the bug report.

## 6. Backups

Speed is irrelevant if a failed disk takes the work with it.

- Monthly: `restic check`, and restore one file to prove the backup is readable.
- Keep the list of files from [the performance chapter](04-performance.md#16-files-this-chapter-creates) in a private dotfiles repository, with `~/.bashrc`, `~/.colcon/defaults.yaml` and your udev rules. A reinstall then takes an afternoon.
- Export the package selection occasionally:

```bash
apt-mark showmanual > ~/apt-manual-$(date +%F).txt; flatpak list --app --columns=application > ~/flatpak-$(date +%F).txt
```

## Acceptance checks

- [ ] The weekly routine has been run once end to end, including the reboot.
- [ ] The unattended-upgrades dry run shows the NVIDIA and kernel packages as blacklisted.
- [ ] `pro status` shows the machine attached.
- [ ] The disk is under 80% used after the first clean-up.
- [ ] A clean-machine temperature reference is recorded.
- [ ] The battery charge limit survives a reboot.
- [ ] A restic restore of one file has been tested.
- [ ] The health check has been run and matches the "healthy" column.
