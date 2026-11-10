# Performance, power and ASUS hardware

## Keep a measurable baseline

Start with the distribution defaults. Record kernel, driver, power profile, AC/battery state, free memory and workload before changing anything. Use the same project, compiler, build directory state and cache policy for each comparison. Compare three runs and report the median, not the fastest run.

```bash
uname -r
powerprofilesctl get
free -h
zramctl
sensors
systemd-analyze
```

Boot time is not application throughput. Judge daily responsiveness while a compile or simulation runs, and listen for audio dropouts under that load.

## CPU and RAM

Start C/C++ builds with **4 concurrent jobs**, despite having 16 CPU threads. Increase toward 6–8 only if memory and thermals permit. For large ROS builds use fewer packages and fewer compiler jobs:

```bash
CMAKE_BUILD_PARALLEL_LEVEL=4 colcon build --parallel-workers 2 --symlink-install
```

The two levels of parallelism can multiply; lower both for large C++ packages. Monitor `btop`, `free -h` and `/proc/pressure/memory`. Stop running a simulator and a large ML training job simultaneously when memory pressure rises.

Keep the default zram setup first. Your inspected system already had roughly 15 GiB of logical zram swap. That is compressed memory-backed capacity, not 15 GiB of extra physical RAM. Do not add another zram service or copy arbitrary swappiness values over a working distribution configuration. If the system still thrashes, reduce workload concurrency and dataset size.

For your own CMake projects:

```bash
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
cmake --build build --parallel 4
ccache --max-size=5G
ccache --show-stats
```

Warm-cache gains are useful but should not be confused with compiler/kernel speed. Avoid global `-march=native` in binaries intended for other robot computers. Cross-compiled firmware needs target-specific flags.

## Power and thermals

Use one policy manager. The existing installation has `power-profiles-daemon`; keep that initially. Do not stack TLP, auto-cpufreq and tuned on top of it.

```bash
powerprofilesctl list
powerprofilesctl set balanced
# Only if listed, on AC, for a measured workload:
powerprofilesctl set performance
# Afterward:
powerprofilesctl set balanced
```

If performance mode only increases temperature and throttling, balanced may sustain the better result. Keep vents clear and use the correct AC adapter. Check supported ASUS charge-limit and platform-profile features before installing extra utilities. `asusctl`/ROG Control Center support is model- and feature-dependent; an ASUS name does not guarantee every control works on this TUF model. [ASUS Linux setup guidance](https://asus-linux.org/guides/arch-guide/).

Do not force `amd_pstate` options if firmware does not expose the required support. Inspect the active driver first:

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
```

## AMD desktop, NVIDIA when useful

Let CachyOS install the correct NVIDIA driver and modules. Keep a compatible module for **each** installed kernel. A fallback kernel without its graphics module is an incomplete fallback.

```bash
nvidia-smi
pacman -Qs nvidia
```

Use the iGPU for ordinary desktop work. With `nvidia-prime` installed, `prime-run application` can offload supported graphics applications. CUDA does not need `prime-run`: its runtime selects a compute device. A display socket may be wired to the discrete GPU; test your actual external monitor arrangement.

Avoid global environment overrides that force the whole session onto NVIDIA. Polling `nvidia-smi` can itself wake the GPU, so stop polling before judging idle battery consumption. Test screen sharing, external displays and suspend before declaring Wayland fully validated.

The default CachyOS kernel is appropriate initially. Its tuning is not a guarantee of deterministic timing. Keep LTS for regressions and avoid experimental scheduler switching until a baseline is recorded. [Kernel documentation](https://wiki.cachyos.org/features/kernel/).

## Storage and desktop load

- Exclude build trees, large datasets, model caches and container storage from KDE file-content indexing in System Settings; keep indexing useful documents if desired.
- Use one large Btrfs filesystem with subvolumes; watch available space and snapshot growth.
- Check `fstrim.timer`; do not repeatedly run manual TRIM as a benchmark trick.
- Keep compile caches bounded. Install heavy CAD and simulation applications only when the learning milestone needs them.
- Do not disable security mitigations, services you have not identified, or filesystem safeguards for speculative speed gains.

## Baseline worksheet

| Metric | Before change | After change | Conditions |
|---|---|---|---|
| Clean project build, median of 3 | Pending | Pending | Same code/compiler/jobs |
| Warm-cache build | Pending | Pending | Same cache policy |
| Audio dropouts during build | Pending | Pending | Same codec/Wi-Fi band |
| Memory pressure / peak usage | Pending | Pending | Same open apps |
| Sustained temperature / clocks | Pending | Pending | Same AC profile |
| Five suspend/resume tests | Pending | Pending | Same peripherals |

A 32 GB RAM upgrade may help concurrent simulation and development more than changing distro, but check the laptop's service documentation and compatibility before buying. The 4 GB GPU remains a separate limit.
