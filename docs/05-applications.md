# Application catalogue

Install in stages. The package names used by `scripts/packages.sh` were checked against this machine's configured repositories on 10 November 2026. Repository availability may change; `pacman -Si NAME` checks metadata without installing.

## Essential host tools

| Purpose | Choice | Installation / notes |
|---|---|---|
| Desktop | KDE Plasma, Dolphin, Konsole, Spectacle, Okular | Installer selection; avoid a second desktop initially |
| Browser | Firefox or your existing browser | Distribution package; restore only needed extensions |
| Editor | Your existing editor; VS Code or Neovim are practical options | Native editor is simplest for USB tools and containers |
| C/C++ | GCC/base-devel, Clang, CMake, Ninja, GDB, ccache | `core` package group |
| Python | Python + uv | `core`; project environments, no `sudo pip` |
| CLI | Git, ripgrep, fd, jq, tmux | `core` |
| Monitoring | btop, lm_sensors, pciutils, usbutils | `core` |
| Audio | PipeWire, WirePlumber, BlueZ, pavucontrol | `core`; use KDE Bluetooth UI |
| Backup | restic | `core`; destination must be external/off-machine |
| Recovery | Snapper, Btrfs Assistant, correct boot integration | CachyOS Hello/current distro instructions |
| Passwords | Existing password manager or KeePassXC | Restore and verify recovery access first |

```bash
bash scripts/packages.sh core          # preview
bash scripts/packages.sh core --apply  # full update + requested packages
```

The helper invokes `pacman -Syu`, not a partial `-Sy` upgrade. Review pacman's changes and conflicts. Firmware, kernel and GPU packages are intentionally left to distribution tooling.

## Development layers

| Work | Tools | Where to put them |
|---|---|---|
| Containers | Podman, crun, Distrobox | Host: `containers` group |
| ARM bare metal | arm-none-eabi GCC/GDB/newlib, OpenOCD, dfu-util | Host: `embedded` group, or pinned vendor toolchain per project |
| UART | picocom, pyserial | picocom host; pyserial project venv |
| Logic analyzer | PulseView, sigrok-cli | Host: `embedded` group; verify supported hardware |
| PCB / mechanical CAD | KiCad, FreeCAD | Optional `cad` group |
| MCU frameworks | Zephyr, ESP-IDF, STM32/vendor SDK, PlatformIO | One pinned SDK/project environment; avoid installing all on day one |
| Robotics | ROS 2, colcon, rosdep, RViz, Gazebo | Dedicated Ubuntu container |
| Marine/autopilot | ArduPilot SITL, MAVProxy, QGroundControl | Separate compatible environment; host GUI if needed |
| Space software | NASA F´; later cFS | Separate project environment |
| ML/data | NumPy, SciPy, pandas, matplotlib, scikit-learn, JupyterLab, PyTorch | uv environment, dependencies locked per project |
| Network inspection | Wireshark, tcpdump, can-utils | Optional host tools; can-utils has a [pinned source-build path](17-robot-networking-and-can.md#learn-socketcan-without-an-adapter) because it was absent from the inspected package metadata |
| Documentation | Markdown + Git; diagrams in Mermaid | This repository and your project repos |

Do not install a host CUDA development toolkit merely to use a PyTorch wheel. The NVIDIA driver is required on the host; framework wheels often provide the needed userspace runtime. Compiling custom CUDA extensions is a separate requirement. [PyTorch installation selector](https://pytorch.org/get-started/locally/).

## Packaging policy

Use distribution packages for system integration, drivers, compilers and USB tools. Flatpak is useful for standalone desktop applications, but sandbox permissions can complicate serial probes, host compilers and container sockets. Use a trusted vendor release when a tool requires it. Inspect AUR build instructions and provenance before installation; do not make an AUR helper part of unattended updates.

Distrobox shares substantial host access and is convenient for trusted tools. A custom home reduces clutter; it does not make Distrobox a security boundary. Use the supplied plain Podman workflow for a smaller, explicit set of mounted files. [Distrobox create documentation](https://distrobox.it/usage/distrobox-create/).

## Suggested order

Day one: browser, editor, core tools, backup and audio. Day two: Podman and the ROS CLI example. Next: one board and its debug stack. Install CAD, simulation and ML tooling when needed, keeping one representative working project in each layer.
