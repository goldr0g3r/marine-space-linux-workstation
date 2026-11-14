# Ubuntu 26.04: performance and optimisation

Previous: [toolchain](03-toolchain.md). Next: [long-term upkeep](05-long-term-upkeep.md).

The aim is to get Ubuntu as close as possible to how CachyOS felt on this laptop, using only Ubuntu's own packages and documented kernel settings, so the configuration vendors support is left intact. Every change has a check and an undo.

The CachyOS values below were read from this laptop on 14 November 2026. Nothing in this chapter has been run on Ubuntu on this laptop; record your own numbers in the worksheet at the end.

## Tuning map

Work through the tiers in order. Tier 1 is where most of the difference in feel comes from.

| Tier | Change | Effect | Risk | Section |
|---|---|---|---|---|
| 1 | Display at 144 Hz | Smoothness of everything on screen | None | 9 |
| 1 | NVIDIA driver in on-demand mode | Removes software rendering and GPU heat | None | 8 |
| 1 | Performance profile on AC | Higher sustained clocks and power limits | Fan noise | 3 |
| 1 | zram with matching kernel settings | No stutter when memory fills | Low | 5 |
| 1 | `preempt=full` kernel parameter | Desktop stays responsive during builds | Low | 4 |
| 1 | apt and Flatpak applications instead of snaps | Faster application start | None | [snap chapter](02-snap-flatpak-apt.md) |
| 1 | Exclude build trees from file indexing | Removes background disk and CPU load | None | 9 |
| 2 | Writeback, cache and reclaim settings | Fewer stalls during large copies and under pressure | Low | 5 |
| 2 | Transparent huge pages | Faster large-memory workloads | Uses more memory | 5 |
| 2 | Build tooling: ccache, mold, Ninja, job limits | Shorter builds, no out-of-memory kills | None | 10 |
| 2 | Filesystem and encryption options | More usable space, lower I/O overhead | Low, needs care | 7 |
| 2 | Wi-Fi power saving off for robot links | Lower network jitter | Battery | 12 |
| 2 | Boot and background services | Faster boot, less idle load | Low | 14 |
| 3 | Low-latency packages, if they still differ from generic | 1000 Hz timer | Different kernel to keep working | 4 |
| 3 | Real-time permissions, CPU isolation, RT kernel | Deterministic control loops | Advanced | 13 |
| 3 | Opt-in `amd64v3` packages | About 1% for most packages, more for numerical code | Experimental, no documented way back | 1 |

## 1. What CachyOS was doing on this laptop

This is why it felt faster. The right-hand column is the supported Ubuntu equivalent.

| Area | CachyOS, as measured | Ubuntu equivalent |
|---|---|---|
| Kernel | 7.3.3, 1000 Hz timer, full preemption | 7.0 generic with `preempt=full` |
| Kernel command line | `nowatchdog` | Same parameter |
| CPU driver | `amd-pstate-epp`, active mode | Same driver expected on the 7.0 kernel |
| Power profile | `performance`: governor and energy preference `performance`, ASUS platform profile `performance` | `powerprofilesctl set performance` on AC |
| Swap | zram sized to all of RAM, zstd, priority 100; zswap off | `systemd-zram-generator` with the same settings |
| `vm.swappiness` | 150, set by a udev rule when zram starts | 150 in `sysctl.d` |
| `vm.page-cluster` | 0 | Same |
| `vm.vfs_cache_pressure` | 50 | Same |
| `vm.dirty_ratio` / `dirty_background_ratio` | 10 / 3 | Same |
| `kernel.nmi_watchdog` | 0 | Same |
| `net.core.netdev_max_backlog` | 4096 | Same |
| Transparent huge pages | `always`, defrag `defer+madvise` | Optional, via `tmpfiles.d` |
| Proactive compaction | 0 | Same |
| NVMe I/O scheduler | `kyber` | Keep Ubuntu's `none`; test before changing |
| Process priorities | `ananicy-cpp` daemon with CachyOS rules | No supported equivalent; use `nice`, `systemd-run` and GameMode |
| Journal size | Capped at 50 MB | Cap at 200 MB |
| Service stop timeout | 10 s | 15 s |
| Open-file limit | Soft limit raised | Raised in section 14 |
| NVIDIA | `NVreg_InitializeSystemMemoryAllocations=0` | Not carried over: small gain, and it stops the driver clearing memory it hands out |
| Optimised package builds | x86-64-v3 repositories | Opt-in `amd64v3` packages, described below. Does not affect MATLAB, ROS binaries, Python wheels or containers |

Boot on CachyOS took 47.4 s: 9.4 s firmware, 21.8 s boot loader (mostly the menu timeout), 0.8 s kernel, 6.0 s initrd and 9.5 s userspace. Use those as the comparison for section 14.

### Optimised packages on 26.04 (tier 3, experimental)

This CPU supports the x86-64-v3 instruction level, which is what CachyOS's optimised repositories were built for. Ubuntu introduced the same idea in 25.10 as an opt-in "architecture variant" called `amd64v3`, and 26.04 still offers it as opt-in; the default packages remain the baseline build.

Confirm the CPU qualifies:

```bash
ld.so --help | grep -E 'x86-64-v[234]'
```

`x86-64-v3 (supported, searched)` is the line to look for. Canonical's published steps to opt in are:

```bash
sudo apt update && sudo apt install dpkg
```

```bash
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
```

```bash
sudo apt update && sudo apt upgrade
```

Read this before doing it:

- **The gain is small.** Canonical measured about 1% for most packages, and more for numerical code. Your heaviest software is not affected at all: MATLAB, ROS packages from the ROS repository, NVIDIA's packages, Python wheels and everything inside containers stay as they are.
- **There is no documented way back.** The announcement says a recovery method would be worked on for 26.04. Take a Timeshift snapshot first and treat that as the undo.
- **Its support status is unclear.** Canonical planned to rebuild and test every package for 26.04, but as of late 2026 reports still describe the variant as opt-in testing that Canonical has not endorsed as an equal alternative.
- **One user reported `ubuntu-drivers` stopped working** after switching; Canonical could not reproduce it. On a laptop that depends on the NVIDIA driver, that is a risk worth weighing.
- **A disk prepared this way may not boot in an older computer** without x86-64-v3.

Recommendation: leave it off. It is the one CachyOS advantage with a real Ubuntu counterpart, but it moves the system away from the configuration vendors test, for a gain that the worksheet in section 17 will struggle to show. If you try it, do so last, after everything else works, and measure before and after.

Sources: [Canonical's announcement](https://discourse.ubuntu.com/t/introducing-architecture-variants-amd64v3-now-available-in-ubuntu-25-10/71312), [status in September 2026](https://omgubuntu.co.uk/2026/09/ubuntu-amd64v3-iso-downloads).

## 2. Measure before changing anything

Install the tools:

```bash
sudo apt install hyperfine sysbench fio stress-ng s-tui nvtop powertop iotop-c rt-tests smem ncdu
```

Capture a baseline to a file you keep:

```bash
{ date; uname -r; cat /proc/cmdline; powerprofilesctl get; free -h; swapon --show; \
  cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver; systemd-analyze; } > ~/baseline-$(date +%F).txt
```

Then run the benchmarks that match your work. Change one thing at a time, repeat, and keep the median of three runs.

| What | Command | Read |
|---|---|---|
| Real build | `hyperfine --runs 3 --prepare 'rm -rf build install log' 'colcon build'` in a workspace you care about | Mean time |
| CPU throughput | `sysbench cpu --threads=16 run` | Events per second |
| Disk random read | `fio --name=rr --filename=$HOME/fio.test --size=2G --rw=randread --bs=4k --iodepth=32 --ioengine=io_uring --direct=1 --runtime=30 --time_based` then `rm ~/fio.test` | IOPS |
| Scheduling latency | `sudo cyclictest --mlockall --smp --priority=80 --interval=200 --distance=0 --duration=2m --quiet` | Max latency in µs |
| Responsiveness under load | `stress-ng --cpu 16 --timeout 60s` while you drag windows and play audio | Stutter, audio dropouts |
| Memory, CPU and I/O pressure | `cat /proc/pressure/memory /proc/pressure/cpu /proc/pressure/io` during a workload | `some avg10` |
| Thermals | `s-tui` during the build | Peak temperature, frequency drop |
| Simulation | A fixed Gazebo world | Real-time factor |
| Boot | `systemd-analyze && systemd-analyze critical-chain` | Userspace time |

`cyclictest` is the number that reflects "does the desktop hitch under load" and also matters for control loops. Run it once idle and once with `stress-ng` running.

## 3. CPU frequency and power profile

Check the driver first:

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

On this laptop the firmware supports `amd-pstate-epp`, which CachyOS was using. If Ubuntu shows `acpi-cpufreq`, add `amd_pstate=active` to the kernel command line as described in section 4 and check again.

Ubuntu ships `power-profiles-daemon`. With `amd-pstate-epp` it controls two things at once: the CPU's energy preference and the ASUS platform profile, which sets fan behaviour and power limits.

```bash
powerprofilesctl list
```

```bash
powerprofilesctl set performance
```

Confirm what it changed:

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference /sys/firmware/acpi/platform_profile
```

Use `performance` on AC. That is what CachyOS was set to, so comparing Ubuntu on `balanced` against it is not a fair comparison. Use `balanced` on battery.

**Switch automatically.** On Kubuntu, set the profile per power source in **System Settings → Power Management**. On Ubuntu Desktop, if **Settings → Power** offers no per-source profile, add `/etc/udev/rules.d/99-power-profile.rules`:

```text
SUBSYSTEM=="power_supply", KERNEL=="ACAD", ATTR{online}=="1", RUN+="/usr/bin/powerprofilesctl set performance"
SUBSYSTEM=="power_supply", KERNEL=="ACAD", ATTR{online}=="0", RUN+="/usr/bin/powerprofilesctl set balanced"
```

```bash
sudo udevadm control --reload-rules
```

`ACAD` is this laptop's AC adapter name under `/sys/class/power_supply`. Test by unplugging and running `powerprofilesctl get`. Use the desktop setting or the rule, not both.

**Keep one power manager.** Do not install TLP, auto-cpufreq or tuned beside `power-profiles-daemon`. They fight over the same settings.

**Check for throttling.** Run `s-tui` during a build. If the frequency falls sharply once the temperature reaches the low 90s °C, the limit is cooling, not software. Compare `performance` and `balanced` over a ten-minute build; keep whichever finishes sooner.

Undo: `powerprofilesctl set balanced` and delete the udev rule.

## 4. Kernel responsiveness

Stay on the stock 7.0 kernel, with the previous 7.0 build as fallback, as set up in [the install chapter](01-install.md#8-fallback-kernel). There is no older kernel series on 26.04. Do not install XanMod, Liquorix or a CachyOS kernel: they move the system off the tested kernel and make the NVIDIA module your problem.

See what the running kernel is built with:

```bash
grep -E 'CONFIG_HZ=|CONFIG_PREEMPT_DYNAMIC|CONFIG_PREEMPT_LAZY=|CONFIG_PREEMPT=' /boot/config-$(uname -r)
```

Ubuntu's generic kernel supports changing the preemption model at boot. Linux 7.0 offers two models on this hardware, `lazy` and `full`. `lazy` favours throughput; `full` lets the kernel interrupt long-running work to serve the desktop, audio and input, which is how the CachyOS kernel behaved.

Edit `/etc/default/grub`:

```text
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash preempt=full nowatchdog"
```

```bash
sudo update-grub
```

Reboot and confirm:

```bash
sudo dmesg | grep -i 'dynamic preempt'
```

It should report `full`. Re-run `cyclictest` and the responsiveness test from section 2. Throughput in long batch jobs can drop by a few percent; that is the trade.

**Other parameters from Canonical's own tuning notes**, to add only for a specific need:

| Parameter | Use | Cost |
|---|---|---|
| `threadirqs` | Audio production, lower interrupt latency | Slight overhead |
| `rcu_nocbs=all rcutree.enable_rcu_lazy=1` | Battery life on a lightly loaded system | None noticeable |
| `nohz_full=all` | Virtual machines and audio | Needs careful testing |
| `amd_pstate=active` | Only if section 3 showed `acpi-cpufreq` | None |

Source: [Fine-tuning the Ubuntu 24.04 kernel](https://discourse.ubuntu.com/t/fine-tuning-the-ubuntu-24-04-kernel-for-low-latency-throughput-and-power-efficiency/44834). It was written for 24.04; the parameters are kernel features and apply to 7.0, except that `preempt=voluntary` and `preempt=none` no longer exist.

**Low-latency packages (tier 3).** Sources disagree about 26.04: the archive lists `linux-lowlatency` packages, while Canonical's stated plan is to retire the separate flavour in favour of the generic kernel plus a settings package. Find out what they are on your system before installing anything:

```bash
apt-cache policy linux-lowlatency lowlatency-kernel
```

```bash
apt show linux-lowlatency 2>/dev/null | grep -i -E 'description|depends|transitional'
```

If the package is transitional or only sets boot parameters, it adds nothing beyond `preempt=full`. If it is a real kernel with `CONFIG_HZ=1000`, try it only when `cyclictest` or audio still shows a problem: install it, boot it from **Advanced options**, and check `grep CONFIG_HZ= /boot/config-$(uname -r)` and `nvidia-smi`. If the NVIDIA module is missing on that kernel, run `sudo ubuntu-drivers install` while booted into it. Keep generic as the default entry until it has passed every check in the install chapter.

Undo: remove the parameters from `/etc/default/grub` and run `sudo update-grub`.

## 5. Memory

The laptop has 16 GB today (2 × 8 GB). An 8 + 16 GB upgrade to 24 GB is planned; the settings below work for both. The integrated GPU reserves 512 MiB of that and takes more as the desktop needs it, so less is available to programs than the label suggests.

### zram

Ubuntu swaps to a file on disk. CachyOS swapped to compressed RAM, which is why it stayed responsive when memory filled.

```bash
sudo apt install systemd-zram-generator
```

Create `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = min(ram, 16384)
compression-algorithm = zstd
swap-priority = 100
```

That matches CachyOS on 16 GB and caps the device at 16 GB after an upgrade. The size is the uncompressed capacity; typical data compresses to about a third. Reboot, then:

```bash
zramctl && swapon --show
```

zram must show priority 100 and the swap file a lower number, so the file is only a backstop. Check that zswap is off, since the two should not be combined:

```bash
cat /sys/module/zswap/parameters/enabled
```

### Kernel memory settings

Create `/etc/sysctl.d/99-workstation.conf`:

```ini
# Prefer compressing idle pages to dropping file cache; correct only with zram
vm.swappiness = 150
# Read one page at a time from swap; readahead is pointless on zram
vm.page-cluster = 0
# Keep directory and inode caches longer; faster builds and file browsing
vm.vfs_cache_pressure = 50
# Start writeback earlier so large copies do not stall the desktop
vm.dirty_ratio = 10
vm.dirty_background_ratio = 3
# Do not compact memory in the background
vm.compaction_proactiveness = 0
# Free a performance counter and avoid periodic interrupts
kernel.nmi_watchdog = 0
# Larger receive queue for bursts of packets
net.core.netdev_max_backlog = 4096
```

```bash
sudo sysctl --system
```

These are the values CachyOS applied on this laptop. The writeback values matter most when recording bags or copying datasets to a slow USB disk: with the defaults, several gigabytes can queue in memory and then freeze everything while they flush.

### Thrashing protection and huge pages (tier 2)

Create `/etc/tmpfiles.d/workstation-mm.conf`:

```text
w! /sys/kernel/mm/lru_gen/min_ttl_ms - - - - 1000
w! /sys/kernel/mm/transparent_hugepage/enabled - - - - always
w! /sys/kernel/mm/transparent_hugepage/defrag - - - - defer+madvise
w! /sys/kernel/mm/transparent_hugepage/khugepaged/max_ptes_none - - - - 409
```

```bash
sudo systemd-tmpfiles --create --boot /etc/tmpfiles.d/workstation-mm.conf
```

- The first line keeps recently used memory from being reclaimed for one second, which stops the desktop thrashing when memory is nearly full. It needs the multi-generation LRU, which `cat /sys/kernel/mm/lru_gen/enabled` reports as a non-zero value. Canonical's tuning notes recommend 1000.
- The other three lines turn on transparent huge pages the way CachyOS did. This helps simulators, compilers and MATLAB with large heaps, and uses more memory. On 16 GB, measure a build and a Gazebo run with and without them; delete the three lines if memory pressure rises.

### Out-of-memory handling

Ubuntu Desktop runs `systemd-oomd`, which kills the heaviest application group before the system freezes. Leave it enabled. See what it has done:

```bash
oomctl
```

```bash
journalctl -u systemd-oomd -b --no-pager | tail
```

If it kills your build, lower the build's parallelism (section 10) or put the build in its own limited scope, so that it is slowed down before anything is killed:

```bash
systemd-run --user --scope -p MemoryHigh=10G -p MemoryMax=12G -- colcon build
```

Find out what is using memory with `smem -tk -c 'name pss' | tail -15`.

Undo: delete the files created in this section and reboot.

## 6. Keeping heavy work from starving the desktop

CachyOS ran a daemon that lowered the priority of compilers and raised it for interactive programs. Ubuntu has no supported equivalent, so do it explicitly.

- Lower the priority of a build:

```bash
nice -n 10 ionice -c 3 colcon build
```

- Limit a build's CPU share and memory. Check that your user session can control CPU first:

```bash
cat /sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers
```

If `cpu` is missing, delegate it, as the Podman documentation describes. Create `/etc/systemd/system/user@.service.d/delegate.conf`:

```ini
[Service]
Delegate=cpu cpuset io memory pids
```

```bash
sudo systemctl daemon-reload
```

Log out and back in. This is also what `scripts/ros.sh` needs for its `--cpus` limit. Then:

```bash
systemd-run --user --scope -p CPUWeight=50 -p MemoryHigh=10G -- colcon build
```

- Raise one application temporarily with GameMode, which switches to the performance profile and adjusts priorities while that program runs:

```bash
sudo apt install gamemode
```

```bash
gamemoderun gz sim shapes.sdf
```

## 7. Storage

The Linux SSD is a Samsung PM991a (`MZVLQ512HBLU`), an OEM drive without a DRAM cache. Drives of this type slow down during long sustained writes and when nearly full, so free space is a performance setting here. Under CachyOS it was 88% full, with 59 GiB free, which was already costing speed.

**Free space.** Keep 15 to 20% free. [The upkeep chapter](05-long-term-upkeep.md#3-disk-hygiene) has the monthly routine.

**Reserved blocks.** ext4 reserves 5% for root by default, about 24 GB on this disk. One percent is enough:

```bash
sudo tune2fs -m 1 "$(findmnt -no SOURCE /)"
```

**TRIM.** The weekly timer is enabled by default. Do not add `discard` to `fstab`.

```bash
systemctl status fstrim.timer
```

**Access times (tier 2).** Add `noatime` to the options of the `/` line in `/etc/fstab`, then validate before rebooting:

```bash
sudo findmnt --verify && sudo mount -o remount / && findmnt -no OPTIONS /
```

If `findmnt --verify` reports an error, fix `fstab` before doing anything else. A broken `fstab` stops the system booting.

**Encryption (only if you chose LUKS).** By default every read and write passes through kernel work queues that add latency on NVMe. Find the mapping name with `lsblk -o NAME,TYPE | grep crypt`, then:

```bash
sudo cryptsetup --allow-discards --perf-no_read_workqueue --perf-no_write_workqueue --persistent refresh MAPPING_NAME
```

`--persistent` stores exactly the flags given, so `--allow-discards` must be included or TRIM stops working. Measure with the `fio` command before and after.

**I/O scheduler.** Ubuntu uses `none` for NVMe, which is the right default. CachyOS used `kyber`. To test it for the current boot only:

```bash
echo kyber | sudo tee /sys/block/nvme0n1/queue/scheduler
```

Keep it only if `fio` and the responsiveness test improve. Check which `nvme` device is the Linux disk with `lsblk -o NAME,MODEL` first.

**Where not to work.** Do not build on the Windows NTFS disk or on USB storage.

**Health.**

```bash
sudo apt install nvme-cli smartmontools
```

```bash
sudo nvme smart-log /dev/nvme0 | grep -E 'percentage_used|available_spare|temperature|media_errors'
```

## 8. Graphics

**Confirm you are not on software rendering.** This alone explains a slow desktop:

```bash
glxinfo -B | grep -E 'renderer|Accelerated'
```

It must name the AMD Radeon and say `Accelerated: yes`. `llvmpipe` means the session is rendering on the CPU; fix the driver before anything else.

**Hybrid mode.** Keep `prime-select on-demand`. The desktop runs on AMD; heavy programs run on NVIDIA through the `nvrun` alias from [the toolchain chapter](03-toolchain.md#1-nvidia-driver-and-cuda). For Vulkan programs add `__VK_LAYER_NV_optimus=NVIDIA_only` to that alias.

**Make it permanent per application.** Copy the launcher and mark it for the discrete GPU, so the menu entry always uses NVIDIA:

```bash
cp /usr/share/applications/org.kicad.kicad.desktop ~/.local/share/applications/
```

Add the line `PrefersNonDefaultGPU=true` under `[Desktop Entry]` in the copy. Do the same for RViz, Gazebo and MATLAB launchers.

**Idle power.** The NVIDIA GPU should power down when nothing uses it:

```bash
cat /sys/bus/pci/devices/0000:01:00.0/power/runtime_status
```

`0000:01:00.0` is this laptop's NVIDIA device. `suspended` is the goal. If it stays `active`, run `nvidia-smi` once to see which process holds it, then close that process and stop any GPU monitor; polling keeps the GPU awake. A monitor on the USB-C DisplayPort output also keeps it on, because that output is wired to the NVIDIA GPU. The HDMI port is wired to the AMD GPU, so an HDMI monitor lets NVIDIA sleep. See [the wiring table](../02-hardware-profile.md#graphics-and-display-wiring).

**Session.** The Ubuntu Desktop session is Wayland only, and Kubuntu defaults to Wayland. X11 programs run through XWayland. If RViz or another Qt tool misbehaves under Wayland, start it with `QT_QPA_PLATFORM=xcb`.

**Suspend.** Several reports describe suspend hangs on NVIDIA hybrid laptops with early 7.0 builds on 26.04. Ubuntu enables the driver's suspend and resume support by default. Confirm the services exist:

```bash
systemctl is-enabled nvidia-suspend.service nvidia-resume.service nvidia-hibernate.service
```

Run five suspend and resume cycles after every kernel or NVIDIA driver update. If a new build breaks suspend, boot the previous one and hold the kernel as described in [the upkeep chapter](05-long-term-upkeep.md#before-a-deadline-demo-or-field-day).

**Video.** In Firefox, open `about:support` and check that hardware video decoding is listed as supported. With it, video calls and tutorials stop loading the CPU.

## 9. Desktop responsiveness

**Refresh rate.** The internal panel supports 1920 × 1080 at 144 Hz and at 60 Hz. If Ubuntu selected 60 Hz, every animation and scroll looks slower than it did on CachyOS. Set 144 Hz in display settings. On Kubuntu confirm with:

```bash
kscreen-doctor -o | grep -i modes
```

The active mode is marked with `*`. On Ubuntu Desktop read it from **Settings → Displays**.

**File indexing.** Indexers walking build trees and datasets cause background disk and CPU load.

- Kubuntu: **System Settings → Search → File Search**. Exclude `~/Projects/*/build`, `install`, `log`, datasets, container storage and `~/matlab`. Check with `balooctl6 status`. `balooctl6 disable` turns it off entirely.
- Ubuntu Desktop: **Settings → Search → Search Locations**. Remove everything except the folders you search. Check with `localsearch status`.

**Animations.**

- Kubuntu: **System Settings → Animations**, move the speed towards instant.
- Ubuntu Desktop: `gsettings set org.gnome.desktop.interface enable-animations false`. Keep the number of shell extensions small; each runs inside the compositor.

**Startup applications.** Remove what you do not use from the desktop's autostart settings. Check with:

```bash
systemd-analyze --user blame | head
```

**Editors.** In VS Code, exclude `build`, `install` and `log` from the file watcher (`files.watcherExclude`). Limit clangd's background indexing with `-j=4` in its arguments.

## 10. Build speed

```bash
sudo apt install ccache mold ninja-build
```

```bash
ccache --set-config=max_size=10G
```

**How many jobs.** A C++ translation unit in a ROS package can take 1.5 to 2.5 GB to compile. The product of parallel packages and jobs per package should stay within what memory allows:

| RAM | `--parallel-workers` | `CMAKE_BUILD_PARALLEL_LEVEL` |
|---|---:|---:|
| 16 GB | 2 | 4 |
| 24 GB | 3 | 4 |
| 32 GB | 4 | 4 |

Raise the numbers only while `cat /proc/pressure/memory` stays near zero during a build.

**Make the settings permanent.** Create `~/.colcon/defaults.yaml`:

```yaml
build:
  symlink-install: true
  parallel-workers: 2
  cmake-args:
    - -DCMAKE_BUILD_TYPE=RelWithDebInfo
    - -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
```

Add `export CMAKE_BUILD_PARALLEL_LEVEL=4` to `~/.bashrc`.

**Mixins** give short names for common options:

```bash
colcon mixin add default https://raw.githubusercontent.com/colcon/colcon-mixin-repository/master/index.yaml && colcon mixin update default
```

```bash
colcon build --mixin ccache ninja
```

`colcon mixin show` lists what is available.

**Build less.** `colcon build --packages-up-to my_package` builds only what one package needs. `--packages-select` rebuilds a single package. Add `-DBUILD_TESTING=OFF` when you are not running tests.

**Plain CMake projects:**

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
  -DCMAKE_EXE_LINKER_FLAGS=-fuse-ld=mold -DCMAKE_SHARED_LINKER_FLAGS=-fuse-ld=mold
```

**Container builds.** Order the `Containerfile` so that rarely changing steps come first, and use cache mounts for package downloads (`RUN --mount=type=cache,target=/var/cache/apt ...`), so a rebuild does not download everything again.

Check the cache is working with `ccache --show-stats` after two builds. Do not set `-march=native` globally; those binaries will not run on a different robot computer.

## 11. Containers

Rootless Podman is fast only with the kernel's own overlay driver:

```bash
podman info --format '{{.Store.GraphDriverName}} {{index .Store.GraphStatus "Native Overlay Diff"}}'
```

Expect `overlay true`. If it reports `fuse-overlayfs`, look for an old `~/.config/containers/storage.conf` and remove the override.

- Use `--network=host` for ROS containers, as `scripts/ros.sh` does. It avoids the user-mode network stack and lets DDS discovery work.
- Keep workspaces on the ext4 disk and bind-mount them. Do not build inside the container's own writable layer.
- Check space with `podman system df`.

## 12. ROS 2, Gazebo and devices

**Discovery.** For work on one machine keep `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`. It stops discovery traffic going out over Wi-Fi.

**Large messages.** Only when images or point clouds are dropped. These are the settings from the [ROS 2 DDS tuning guide](https://docs.ros.org/en/lyrical/How-To-Guides/DDS-tuning.html). Create `/etc/sysctl.d/60-ros-dds.conf`:

```ini
net.ipv4.ipfrag_time = 3
net.ipv4.ipfrag_high_thresh = 134217728
net.core.rmem_max = 2147483647
```

```bash
sudo sysctl --system
```

The first two stop lost fragments on Wi-Fi from stalling a connection. The third lets Cyclone DDS ask for a large receive buffer; it also needs a configuration file that sets `SocketReceiveBufferSize` with `min="10MB"`, pointed to by `CYCLONEDDS_URI`. The guide has the XML. Over Wi-Fi, use best-effort QoS for sensor streams.

**Fewer copies.** Run nodes that exchange large messages as components in one container process with intra-process communication enabled.

**Wi-Fi jitter.** Ubuntu enables Wi-Fi power saving, and CachyOS had it on as well. It adds latency spikes that matter when teleoperating a robot. Turn it off for the robot's network only:

```bash
nmcli connection modify "ROBOT_NETWORK_NAME" 802-11-wireless.powersave 2
```

Reconnect and check with `iw dev wlan0 get power_save`. Use Ethernet for anything timing-sensitive; see [the networking guide](../../17-robot-networking-and-can.md).

**USB serial latency.** FTDI adapters buffer for 16 ms by default, which limits control-loop rates. Create `/etc/udev/rules.d/99-ftdi-latency.rules`:

```text
ACTION=="add", SUBSYSTEM=="usb-serial", DRIVER=="ftdi_sio", ATTR{latency_timer}="1"
```

**USB devices that drop out.** Stop the kernel suspending one specific sensor or camera. Find its IDs with `lsusb`, then create `/etc/udev/rules.d/99-usb-no-suspend.rules`:

```text
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="XXXX", ATTR{idProduct}=="YYYY", ATTR{power/control}="on"
```

Reload after either rule with `sudo udevadm control --reload-rules && sudo udevadm trigger`.

**Gazebo with 4 GB of VRAM.**

- Run the server without a window when you only need physics and sensors: `gz sim -r -s --headless-rendering world.sdf`. Attach the GUI separately with `gz sim -g` when needed.
- Lower camera and lidar resolution and update rates in the model before lowering physics accuracy.
- Watch the real-time factor. Below 1.0, the simulation is the bottleneck, not the controller.
- Watch VRAM with `nvtop`. Gazebo, RViz and a CUDA job together will not fit.

**MATLAB and Simulink.**

- Start it on the NVIDIA GPU (`nvrun matlab`) and check `rendererinfo` reports hardware rendering.
- Each parallel worker is a full MATLAB process. On 16 GB, keep `parpool` at four workers or fewer.
- Use Accelerator mode and Fast Restart for repeated Simulink runs.
- Keep `slprj`, cache and generated-code folders on the local disk, outside any cloud-synced directory.
- Run scripts without the desktop using `matlab -batch "script_name"`.

## 13. Real-time work (tier 3)

Only for control loops where missed deadlines matter.

**Permissions.** `ros2_control` tries to run its control loop with real-time priority 50. A normal user is not allowed to. Following the ros2_control documentation:

```bash
sudo groupadd realtime && sudo usermod -aG realtime "$USER"
```

Create `/etc/security/limits.d/99-realtime.conf`:

```text
@realtime soft rtprio 99
@realtime soft priority 99
@realtime soft memlock unlimited
@realtime hard rtprio 99
@realtime hard priority 99
@realtime hard memlock unlimited
```

Log out and back in. With `preempt=full` this already reduces jitter noticeably.

**A dedicated core.** CPU threads 14 and 15 are the two halves of one physical core on this processor. To reserve that core, add to the kernel command line:

```text
isolcpus=domain,managed_irq,14-15 nohz_full=14-15 rcu_nocbs=14-15 irqaffinity=0-13
```

Run the control process on it with `taskset -c 14 chrt -f 80 your_command`. Everything else loses one of eight cores, so remove the parameters when the experiment ends.

**A real-time kernel.** From 26.04 the real-time kernel is in the normal archive and does not need Ubuntu Pro:

```bash
sudo apt install ubuntu-realtime
```

NVIDIA does not officially support its driver on real-time kernels, and no report for 26.04 was found during research. Treat the real-time kernel as a separate boot entry for control experiments on the AMD GPU, and keep generic as the default.

Measure every step here with `cyclictest`; the maximum latency is the result.

## 14. Boot and background load

```bash
systemd-analyze blame | head -15
```

```bash
systemd-analyze critical-chain
```

| Item | Action | Why |
|---|---|---|
| GRUB menu | `GRUB_TIMEOUT=3` in `/etc/default/grub` | CachyOS spent 21.8 s in the boot loader, mostly waiting |
| `NetworkManager-wait-online.service` | `sudo systemctl disable NetworkManager-wait-online.service` | Delays boot until the network is up; nothing here needs that |
| `apport.service` | `sudo systemctl disable --now apport.service`, and set `enabled=0` in `/etc/default/apport` | Crash collection stalls the system when Gazebo or MATLAB dumps a multi-gigabyte core |
| `cups-browsed.service` | `sudo systemctl disable --now cups-browsed.service` | Only needed to discover network printers |
| `avahi-daemon` | Keep | Robots and companion computers are found by `.local` names |
| `bluetooth`, `fwupd`, `snapd`, `systemd-oomd`, `unattended-upgrades` | Keep | Each is used elsewhere in these guides |

**Shorter shutdown waits.** Create `/etc/systemd/system.conf.d/timeout.conf`:

```ini
[Manager]
DefaultTimeoutStopSec=15s
```

**Journal size.** Create `/etc/systemd/journald.conf.d/size.conf`:

```ini
[Journal]
SystemMaxUse=200M
```

**Open files.** Large ROS graphs and builds can exceed the default limit of 1024 open files per process. Check with `ulimit -Sn`. To raise it, create both `/etc/systemd/system.conf.d/limits.conf` and `/etc/systemd/user.conf.d/limits.conf`:

```ini
[Manager]
DefaultLimitNOFILE=8192:1048576
```

Reboot after these three changes. Do not disable services you have not identified.

### Notes specific to 26.04

- **Dracut** builds the initramfs. After changing kernel module options, regenerate it with `sudo dracut --regenerate-all --force`. Changes to `/etc/default/grub` still need only `sudo update-grub`.
- **Chrony** is the default time service, which suits clock synchronisation between robot computers. Check with `chronyc tracking`.
- **GCC 15 and Python 3.14** are the defaults. Older code may need `gcc-14`, and Python projects should pin an interpreter per project. See [the toolchain chapter](03-toolchain.md#7-python-314-and-gcc-15).
- **sudo-rs and Rust coreutils** are the defaults. If an old script fails on a `sudo` or coreutils option, the originals are available as `sudo.ws` and with the `gnu` prefix.

## 15. What not to do

- Do not remove snapd.
- Do not disable CPU security mitigations.
- Do not replace the packaged NVIDIA driver with the `.run` installer.
- Do not install a third-party kernel.
- Do not stack power managers, or run zram and zswap together.
- Do not use unofficial power-limit tools on this CPU.
- Do not copy the old CachyOS configuration files onto the new system. The values above are the ones worth keeping.

## 16. Files this chapter creates

Deleting a file and rebooting undoes that change.

| File | Section |
|---|---|
| `/etc/default/grub` (edited) | 4, 13, 14 |
| `/etc/udev/rules.d/99-power-profile.rules` | 3 |
| `/etc/systemd/zram-generator.conf` | 5 |
| `/etc/sysctl.d/99-workstation.conf` | 5 |
| `/etc/tmpfiles.d/workstation-mm.conf` | 5 |
| `/etc/systemd/system/user@.service.d/delegate.conf` | 6 |
| `/etc/fstab` (edited) | 7 |
| `/etc/sysctl.d/60-ros-dds.conf` | 12 |
| `/etc/udev/rules.d/99-ftdi-latency.rules`, `99-usb-no-suspend.rules` | 12 |
| `/etc/security/limits.d/99-realtime.conf` | 13 |
| `/etc/systemd/system.conf.d/timeout.conf`, `limits.conf` | 14 |
| `/etc/systemd/user.conf.d/limits.conf` | 14 |
| `/etc/systemd/journald.conf.d/size.conf` | 14 |
| `~/.colcon/defaults.yaml` | 10 |

Keep copies of these in a private dotfiles repository so a reinstall takes minutes.

## 17. Results worksheet

| Measurement | Default Ubuntu | After tier 1 | After tier 2 |
|---|---|---|---|
| Clean workspace build, median of 3 | | | |
| `sysbench cpu` events per second | | | |
| `fio` random read IOPS | | | |
| `cyclictest` max latency, idle | | | |
| `cyclictest` max latency, under `stress-ng` | | | |
| Audio dropouts during a build | | | |
| Peak temperature during a build | | | |
| Gazebo real-time factor | | | |
| Boot: userspace time | | | |
| NVIDIA GPU `suspended` at idle | | | |

## Expected outcome

With tier 1 applied, responsiveness under load should be close to CachyOS, because the same mechanisms are in place: full preemption, zram, the performance profile and the same memory settings. Compile throughput depends on the compiler, ccache and cooling far more than on the distribution. The remaining gap is CachyOS's optimised package builds, which Canonical's own measurement puts at about 1% for most packages, and, if `CONFIG_HZ` on your kernel is lower than 1000, its timer frequency.

Continue with [long-term upkeep](05-long-term-upkeep.md).
