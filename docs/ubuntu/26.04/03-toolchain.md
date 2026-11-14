# Ubuntu 26.04: toolchain

Previous: [snap, Flatpak and apt](02-snap-flatpak-apt.md). Next: [performance](04-performance.md).

Install in this order. Each section ends with a check; do not move on until it passes.

| Tool | Source | Version on this host |
|---|---|---|
| NVIDIA driver | apt, via `ubuntu-drivers` | The recommended packaged branch, or 595 |
| Podman, Distrobox | apt | Ubuntu archive |
| NVIDIA Container Toolkit | NVIDIA apt repository | 1.20.x |
| ROS 2 | ROS apt repository | Lyrical, native |
| Gazebo | ROS apt repository | Jetty |
| ROS 2 Jazzy | Container | For MATLAB and existing Jazzy projects |
| MATLAB | MathWorks installer or `mpm` | R2026b on the host; ROS Toolbox work in a 24.04 container |
| KiCad | Ubuntu archive, KiCad PPA or Flatpak | 10.0.x |
| Embedded tools | apt and vendor installers | Ubuntu archive |

Two defaults on this release cause most surprises: **Python 3.14** and **GCC 15**. Section 7 covers them.

## 1. NVIDIA driver and CUDA

The driver was installed in [the install chapter](01-install.md#7-graphics-driver). Confirm:

```bash
nvidia-smi
```

Run one application on the NVIDIA GPU while the desktop stays on AMD:

```bash
__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia glxinfo -B | grep -i renderer
```

`glxinfo` comes from `mesa-utils`. Add an alias for it to your shell configuration, for example `alias nvrun='__NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia'`.

**Do not install a system CUDA toolkit by default.** PyTorch wheels, MATLAB's Parallel Computing Toolbox and CUDA container images each carry their own CUDA libraries and need only the driver. If a project does need the host toolkit, add NVIDIA's CUDA repository and install `cuda-toolkit`, never the `cuda` metapackage, which pulls its own driver and fights `ubuntu-drivers`. CUDA 13.5 lists Ubuntu 26.04.1 with kernel 7.0 and GCC 15.2. See the [CUDA installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html).

The GPU has 4 GB of VRAM. The limits in [the AI/ML chapter](../../08-ai-ml.md) apply unchanged.

## 2. Containers

```bash
sudo apt install podman crun distrobox
```

```bash
podman info --format '{{.Host.Security.Rootless}} {{.Host.OCIRuntime.Name}}'
```

Expect `true crun`. Docker is optional; if you want it beside Podman, use [Docker's Ubuntu repository](https://docs.docker.com/engine/install/ubuntu/) and remember that membership of the `docker` group is root-equivalent.

### GPU in containers

```bash
sudo apt-get install -y --no-install-recommends ca-certificates curl gnupg2
```

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
```

```bash
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
```

The toolkit generates a CDI specification through a systemd unit and refreshes it when the driver changes:

```bash
sudo systemctl enable --now nvidia-cdi-refresh.path nvidia-cdi-refresh.service
```

```bash
nvidia-ctk cdi list
```

```bash
podman run --rm --device nvidia.com/gpu=all --security-opt=label=disable ubuntu nvidia-smi -L
```

If the list is empty, run `sudo nvidia-ctk cdi generate --output=/var/run/cdi/nvidia.yaml`. Source: [NVIDIA CDI support](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html).

## 3. ROS 2 Lyrical, native

Lyrical is Tier 1 on this release and is supported to May 2031. The Lyrical installation page could not be read automatically during research, so compare the commands below with [the official page](https://docs.ros.org/en/lyrical/Installation/Ubuntu-Install-Debs.html) before running them. They are the same repository steps ROS documents for Jazzy, and they detect the Ubuntu codename themselves.

```bash
locale
```

The locale must be UTF-8. Then enable the repositories:

```bash
sudo apt install software-properties-common && sudo add-apt-repository universe
```

```bash
sudo apt update && sudo apt install curl -y
```

```bash
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
```

```bash
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
```

```bash
sudo dpkg -i /tmp/ros2-apt-source.deb
```

Check that the `resolute-updates` and `resolute-backports` suites are enabled:

```bash
grep Suites /etc/apt/sources.list.d/ubuntu.sources
```

Install:

```bash
sudo apt update && sudo apt full-upgrade
```

```bash
sudo apt install ros-dev-tools ros-lyrical-desktop ros-lyrical-ros-gz ros-lyrical-rmw-cyclonedds-cpp
```

```bash
sudo rosdep init && rosdep update
```

`ros-lyrical-ros-gz` brings Gazebo Jetty, the recommended pairing for Lyrical.

### Shell setup

ROS provides setup files for bash, zsh and sh, not fish. Use bash or zsh for ROS terminals. Do not source ROS in every shell; add a function to `~/.bashrc` and call it when needed:

```bash
lyrical() { source /opt/ros/lyrical/setup.bash; export ROS_DOMAIN_ID=42 RMW_IMPLEMENTATION=rmw_cyclonedds_cpp; }
```

### Check

Terminal A: `lyrical && ros2 run demo_nodes_cpp talker`. Terminal B: `lyrical && ros2 run demo_nodes_py listener`. Then:

```bash
lyrical && nvrun rviz2
```

```bash
lyrical && nvrun gz sim shapes.sdf
```

The desktop is Wayland. If RViz fails to start or draws incorrectly, run it through XWayland with `QT_QPA_PLATFORM=xcb`.

## 4. ROS 2 Jazzy, in a container

Jazzy has no native packages for 26.04. The container in this repository is Jazzy on Ubuntu 24.04 and runs unchanged:

```bash
podman build -t localhost/robotics-jazzy -f containers/ros/Containerfile .
```

```bash
bash scripts/ros.sh ros2 run demo_nodes_cpp talker
```

For an interactive Jazzy environment with RViz, Gazebo Harmonic and the GPU:

```bash
distrobox create --name jazzy --image ubuntu:24.04 --additional-flags "--device nvidia.com/gpu=all"
```

```bash
distrobox enter jazzy
```

Inside it, follow [the 24.04 ROS section](../24.04/03-toolchain.md#3-ros-2-jazzy-native). Distrobox shares your home directory, so keep Jazzy and Lyrical workspaces in separate directories and never share `build`, `install` or `log` between them.

Jazzy and Lyrical nodes can exchange messages only where the message definitions are identical. Treat cross-release communication as something to test per message type, not something to rely on.

## 5. MATLAB R2026b

MATLAB and Simulink list Ubuntu 26.04 as validated. The ROS Toolbox does not: it lists Ubuntu 24.04 and 22.04, targets Jazzy, and needs Python 3.10 or 3.11 and GCC 6.3 to 14. Split the work accordingly.

### MATLAB on the host

MathWorks publishes the dependency list per release and Ubuntu version in its [container-images repository](https://github.com/mathworks-ref-arch/container-images/tree/main/matlab-deps). Use the `ubuntu26.04` folder for your release if it exists; otherwise let the installer report what is missing.

Install into a directory you own:

```bash
mkdir -p ~/matlab/R2026b
```

Either download the Linux installer from your MathWorks account, unzip it and run `./install`, or use the MATLAB Package Manager:

```bash
wget https://www.mathworks.com/mpm/glnxa64/mpm && chmod +x mpm
```

```bash
./mpm install --release=R2026b --destination="$HOME/matlab/R2026b" \
  --products MATLAB Simulink Robotics_System_Toolbox Control_System_Toolbox
```

Adjust the product list to your licence. `mpm` does not activate the licence; sign in on first launch. Starting with R2026b, MATLAB no longer bundles Java on Linux; install the **MATLAB Support for OpenJDK** add-on when a feature asks for it.

`gpuDevice` in MATLAB should report the RTX 3050. It needs only the driver.

### ROS Toolbox in a 24.04 container (supported configuration)

Use the `jazzy` Distrobox from section 4. It gives MATLAB the platform the toolbox was tested on, with Jazzy and the right compiler, while sharing your home directory and display.

Inside the container:

1. Install the MATLAB dependencies from the `ubuntu24.04` folder of the same MathWorks repository.
2. Install Python 3.10 as in [the 24.04 guide](../24.04/03-toolchain.md#ros-toolbox).
3. Install MATLAB with the ROS Toolbox into a second directory, for example `~/matlab/R2026b-ros`, so the container has its own complete installation.
4. Start it with `export ROS_DOMAIN_ID=42 && ~/matlab/R2026b-ros/bin/matlab` and check `ros2 topic list` against a Jazzy talker.

Whether your licence allows a second installation on the same machine is a MathWorks licensing question; check before installing.

### ROS Toolbox on the host (unsupported)

It may work with a separately installed Python 3.11 and `gcc-14`, talking to Lyrical nodes where message definitions match. MathWorks will not support it, and it is the kind of setup this migration was meant to avoid. Try it only as an experiment.

## 6. KiCad

Check what the archive ships first:

```bash
apt policy kicad
```

If that is KiCad 10, install it with apt and stop. If it is older, the KiCad PPA is the native route, provided it publishes builds for 26.04:

```bash
sudo add-apt-repository ppa:kicad/kicad-10.0-releases
```

```bash
sudo apt update && sudo apt install kicad
```

If `apt update` reports that the PPA has no release file for this Ubuntu version, remove it with `sudo add-apt-repository --remove ppa:kicad/kicad-10.0-releases` and use the Flatpak:

```bash
flatpak install --from https://flathub.org/repo/appstream/org.kicad.KiCad.flatpakref
```

## 7. Python 3.14 and GCC 15

- **Python.** Never install project packages into the system interpreter. Use a virtual environment per project and pin the interpreter. Check that a framework publishes wheels for 3.14 before starting; if it does not, create the environment with an older interpreter using `uv`, or work in a container.
- **GCC.** Older C and C++ code can fail under GCC 15's stricter defaults. Install the previous compiler beside it and select it per project:

```bash
sudo apt install gcc-14 g++-14
```

```bash
cmake -S . -B build -DCMAKE_C_COMPILER=gcc-14 -DCMAKE_CXX_COMPILER=g++-14
```

## 8. Embedded tools

```bash
sudo apt install gcc-arm-none-eabi gdb-multiarch openocd stlink-tools dfu-util \
  picocom minicom can-utils usbutils
```

Ubuntu packages the Arm debugger as `gdb-multiarch`, not `arm-none-eabi-gdb`. For a newer compiler, use Arm's release tarball in `/opt` for that project only.

Two Ubuntu-specific causes of serial devices disconnecting or refusing to open:

- **brltty** claims CH340 and CP210x USB serial adapters. If you do not use a braille display:

```bash
sudo apt remove brltty
```

- **ModemManager** probes new serial ports and corrupts bootloader handshakes. This laptop has no cellular modem:

```bash
sudo apt remove modemmanager
```

Group membership (`dialout`, `plugdev`) was set in the install chapter.

Vendor tools lag new Ubuntu releases. Before relying on STM32CubeIDE, the nRF tools or PX4's `Tools/setup/ubuntu.sh`, check that the vendor lists 26.04. Where one does not, run that tool in the 24.04 Distrobox and pass the USB device through. PlatformIO and west install per user:

```bash
pipx install platformio
```

After installing any vendor udev rules:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

The exercises in [the embedded chapter](../../07-embedded.md) and [the CAN guide](../../17-robot-networking-and-can.md) apply as written.

## Acceptance checks

- [ ] `nvidia-smi` works on the host and inside a Podman container.
- [ ] Lyrical talker and listener exchange messages natively.
- [ ] RViz and Gazebo Jetty render on the NVIDIA GPU.
- [ ] The Jazzy container builds and its talker runs.
- [ ] MATLAB starts on the host and `gpuDevice` reports the GPU.
- [ ] MATLAB with the ROS Toolbox, in the 24.04 container, sees a Jazzy talker.
- [ ] KiCad opens a project and the 3D viewer renders.
- [ ] A USB serial board and a debug probe work as a normal user.

Continue with [performance](04-performance.md).
