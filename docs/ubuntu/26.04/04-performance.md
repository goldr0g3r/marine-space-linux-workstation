# Ubuntu 26.04: performance and optimisation

Previous: [toolchain](03-toolchain.md).

The aim is to recover most of what CachyOS gave without leaving the configuration vendors support. Every change here is reversible and uses Ubuntu's own packages. Nothing was measured on this laptop; record your own numbers in [the baseline worksheet](../../03-performance-and-hardware.md#baseline-worksheet).

## 1. Measure first

Record before changing anything, and repeat after each change. Use the median of three runs.

```bash
uname -r && powerprofilesctl get && free -h && swapon --show
```

```bash
systemd-analyze && systemd-analyze blame | head -15
```

Use one real workload as the benchmark: a clean `colcon build` of a workspace you care about, or a Gazebo world with a fixed real-time factor.

## 2. Kernel

- Stay on the stock **7.0 kernel**. On 26.04 it is both the GA and the HWE kernel, and it is the kernel NVIDIA validated CUDA 13.5 against.
- There is no older kernel series in the archive to fall back to. The fallback is the previous 7.0 build, kept as described in [the install chapter](01-install.md#8-fallback-kernel).
- Do not install XanMod, Liquorix or a CachyOS kernel. They are faster in some benchmarks, but they move the system off the tested kernel and make the NVIDIA DKMS build your problem. That is the trade this migration was made to avoid.

**Lower latency without a different kernel.** The generic kernel supports dynamic preemption. For audio work or tighter control loops, add `preempt=full` to `GRUB_CMDLINE_LINUX_DEFAULT` in `/etc/default/grub`, then:

```bash
sudo update-grub
```

Check after reboot with `cat /sys/kernel/debug/sched/preempt` as root. Throughput drops slightly; keep it only if a measurement or an audible difference justifies it.

**Hard real time.** Ubuntu Pro is free for personal use on up to five machines and provides a PREEMPT_RT kernel. Check that it is offered for 26.04 with `pro status` after attaching:

```bash
sudo pro attach
```

```bash
sudo pro enable realtime-kernel
```

Use it only for control-loop experiments. Confirm NVIDIA driver support for that kernel before enabling it on this laptop, and keep the generic kernel as the default boot entry.

## 3. Power and thermals

Ubuntu ships `power-profiles-daemon`. Keep it as the only power manager; do not add TLP, auto-cpufreq or tuned.

```bash
powerprofilesctl list
```

```bash
powerprofilesctl set performance
```

Use `performance` on AC for builds and simulation, and `balanced` otherwise. If `performance` only raises temperature and triggers throttling, `balanced` sustains the better result.

Check the frequency driver before changing anything about it:

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

The 4800H is Zen 2. Many firmwares for it do not expose the CPPC interface `amd_pstate` needs, in which case the driver is `acpi-cpufreq` and that is correct. Do not force `amd_pstate` with kernel parameters.

Battery charge limit, if the kernel exposes it:

```bash
cat /sys/class/power_supply/BAT*/charge_control_end_threshold
```

Watch temperatures with `sensors` and `btop` during the benchmark. Clean vents and a hard surface are worth more than any setting here.

## 4. Memory

Confirm what is installed first. Guidance below assumes 16 to 24 GB.

```bash
sudo dmidecode -t memory | grep -E 'Size|Speed|Locator'
```

Ubuntu Desktop uses a swap file and `systemd-oomd`. Add compressed swap in RAM in front of it:

```bash
sudo apt install systemd-zram-generator
```

Create `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = min(ram / 2, 8192)
compression-algorithm = zstd
swap-priority = 100
```

Reboot, then check that zram has the higher priority and the swap file remains as the backstop:

```bash
zramctl && swapon --show
```

With zram, the kernel should prefer swapping to compressed RAM over dropping file cache. These are the values commonly shipped by distributions that default to zram. Create `/etc/sysctl.d/99-zram.conf`:

```ini
vm.swappiness = 180
vm.page-cluster = 0
vm.watermark_boost_factor = 0
vm.watermark_scale_factor = 125
```

```bash
sudo sysctl --system
```

To undo, delete both files and reboot. Leave `systemd-oomd` enabled; it kills a runaway build before the desktop freezes.

Zram is not extra RAM. If Gazebo, MATLAB and a build together exhaust memory, lower build parallelism (section 6) before raising zram.

## 5. Storage

- `fstrim.timer` is enabled by default. Confirm with `systemctl status fstrim.timer`; do not add `discard` to `fstab`.
- NVMe uses the `none` I/O scheduler by default, which is correct.
- Keep 15 to 20% of the disk free. Prune container storage with `podman system prune` after checking what it will remove.
- Exclude build trees, datasets and container storage from desktop file indexing. On Kubuntu: **System Settings → Search → File Search**. On GNOME: **Settings → Search → Search Locations**.

## 6. Build speed

```bash
sudo apt install ccache mold ninja-build
```

```bash
ccache --max-size=10G
```

For CMake projects:

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
  -DCMAKE_EXE_LINKER_FLAGS=-fuse-ld=mold -DCMAKE_SHARED_LINKER_FLAGS=-fuse-ld=mold
```

For ROS workspaces, parallel packages multiply with parallel compiler jobs. Start here and raise only while memory pressure stays low:

```bash
CMAKE_BUILD_PARALLEL_LEVEL=6 colcon build --parallel-workers 3 --symlink-install \
  --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_C_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
```

```bash
cat /proc/pressure/memory
```

Do not set `-march=native` globally. Binaries built that way do not run on a different robot computer.

## 7. Graphics

- Keep `prime-select on-demand`. Forcing the whole session onto NVIDIA costs battery and heat and gains nothing for the desktop.
- Launch RViz, Gazebo and KiCad's 3D viewer with the `nvrun` alias from [the toolchain chapter](03-toolchain.md#1-nvidia-driver-and-cuda).
- Check that the NVIDIA GPU powers down when idle:

```bash
cat /sys/bus/pci/devices/0000:01:00.0/power/runtime_status
```

Adjust the PCI address using `lspci | grep -i nvidia`. `suspended` is the goal. Polling `nvidia-smi` wakes the GPU, so stop monitors before judging.

- The Ubuntu Desktop session is Wayland only, and Kubuntu defaults to Wayland. X11 applications run through XWayland. If RViz or another Qt tool misbehaves under Wayland, start it with `QT_QPA_PLATFORM=xcb`.

### Suspend

Several reports describe suspend hangs on NVIDIA hybrid laptops with early 7.0 kernels on 26.04. Ubuntu enables the driver's suspend and resume support by default. Confirm the services exist and test before trusting the lid:

```bash
systemctl is-enabled nvidia-suspend.service nvidia-resume.service nvidia-hibernate.service
```

Run five suspend and resume cycles after every kernel or NVIDIA driver update. If a new kernel breaks suspend, boot the previous one from **Advanced options** and hold the kernel packages with `sudo apt-mark hold` until a fix lands.

## 8. ROS 2 networking

Only when large messages (images, point clouds) are dropped. These are the kernel settings from the [ROS 2 DDS tuning guide](https://docs.ros.org/en/lyrical/How-To-Guides/DDS-tuning.html). Create `/etc/sysctl.d/60-ros-dds.conf`:

```ini
net.core.rmem_max = 2147483647
net.ipv4.ipfrag_time = 3
net.ipv4.ipfrag_high_thresh = 134217728
```

```bash
sudo sysctl --system
```

For localhost-only work keep `ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`, which avoids multicast traffic on Wi-Fi.

## 9. Boot and background load

```bash
systemd-analyze blame | head -15
```

Safe, common savings on a laptop:

```bash
sudo systemctl disable NetworkManager-wait-online.service
```

Review startup applications in the desktop settings and remove what you do not use. Snap adds a mount per snap at boot; keeping `refresh.retain=2` from [the snap chapter](02-snap-flatpak-apt.md#5-keep-snap-quiet-and-predictable) limits that. Do not disable services you have not identified.

## 10. Changes in 26.04 that affect tuning

- **Dracut** builds the initramfs. After changing kernel module options, regenerate with `sudo dracut --regenerate-all --force`.
- **Chrony** is the default time service, which suits ROS clock synchronisation across machines. Check with `chronyc tracking`.
- **GCC 15 and Python 3.14** are the defaults. Older code may need `gcc-14`, and Python projects should use a per-project virtual environment with a pinned interpreter.
- **sudo-rs and Rust coreutils** are the defaults. If an old script fails on a `sudo` or coreutils option, the originals are available as `sudo.ws` and with the `gnu` prefix.

## 11. What not to do

- Do not remove snapd.
- Do not disable CPU security mitigations.
- Do not replace the packaged NVIDIA driver with the `.run` installer.
- Do not stack power managers or zram services.
- Do not copy the old CachyOS `sysctl`, WirePlumber or GPU overrides onto the new system.

## Expected outcome

Desktop responsiveness under load should be close to CachyOS once zram and the build settings are in place. Compile throughput is governed mostly by the compiler, ccache and thermals, not the distribution. The honest remaining gap is CachyOS's optimised package builds, which do not apply to MATLAB, ROS binaries from the ROS repository, Python wheels or anything in a container anyway.

## Acceptance checks

- [ ] Baseline and after-change numbers are recorded for one real workload.
- [ ] `swapon --show` lists zram above the swap file.
- [ ] A full workspace build completes without `systemd-oomd` intervening.
- [ ] The NVIDIA GPU reports `suspended` at idle.
- [ ] Temperatures under sustained load are recorded for both power profiles.
