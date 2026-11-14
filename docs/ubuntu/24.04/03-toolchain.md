# Ubuntu 24.04: toolchain

Previous: [snap, Flatpak and apt](02-snap-flatpak-apt.md). Next: [performance](04-performance.md).

Install in this order. Each section ends with a check; do not move on until it passes.

| Tool | Source | Version on this host |
|---|---|---|
| NVIDIA driver | apt, via `ubuntu-drivers` | The recommended packaged branch |
| Podman, Distrobox | apt | Ubuntu archive |
| NVIDIA Container Toolkit | NVIDIA apt repository | 1.20.x |
| ROS 2 | ROS apt repository | Jazzy, native |
| Gazebo | ROS apt repository | Harmonic |
| MATLAB | MathWorks installer or `mpm` | R2026b |
| KiCad | KiCad PPA or Flatpak | 10.0.x |
| Embedded tools | apt and vendor installers | Ubuntu archive |

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

**Do not install a system CUDA toolkit by default.** PyTorch wheels, MATLAB's Parallel Computing Toolbox and CUDA container images each carry their own CUDA libraries and need only the driver. If a project does need the host toolkit, add NVIDIA's CUDA repository and install `cuda-toolkit`, never the `cuda` metapackage, which pulls its own driver and fights `ubuntu-drivers`. See the [CUDA installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html).

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

## 3. ROS 2 Jazzy, native

Jazzy is Tier 1 on this release and is what the MATLAB ROS Toolbox targets. These are the upstream commands.

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

Upstream requires the `noble-updates` and `noble-backports` suites. Check them:

```bash
grep Suites /etc/apt/sources.list.d/ubuntu.sources
```

Install:

```bash
sudo apt update && sudo apt full-upgrade
```

```bash
sudo apt install ros-dev-tools ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-rmw-cyclonedds-cpp
```

```bash
sudo rosdep init && rosdep update
```

`ros-jazzy-ros-gz` brings Gazebo Harmonic, the recommended pairing for Jazzy.

### Shell setup

ROS provides setup files for bash, zsh and sh, not fish. Use bash or zsh for ROS terminals. Do not source ROS in every shell; add a function to `~/.bashrc` and call it when needed:

```bash
jazzy() { source /opt/ros/jazzy/setup.bash; export ROS_DOMAIN_ID=42 RMW_IMPLEMENTATION=rmw_cyclonedds_cpp; }
```

The domain and middleware match `scripts/ros.sh`, so native nodes and the repository's container see each other.

### Check

Terminal A: `jazzy && ros2 run demo_nodes_cpp talker`. Terminal B: `jazzy && ros2 run demo_nodes_py listener`. Then:

```bash
jazzy && nvrun rviz2
```

```bash
jazzy && nvrun gz sim shapes.sdf
```

### Lyrical and other releases

Lyrical is Tier 3 on 24.04. Run it in a container, with the GPU passed through CDI when you need RViz or Gazebo:

```bash
distrobox create --name lyrical --image ubuntu:26.04 --additional-flags "--device nvidia.com/gpu=all"
```

Install Lyrical inside it using the same repository steps. The Jazzy container in this repository still builds and runs unchanged:

```bash
podman build -t localhost/robotics-jazzy -f containers/ros/Containerfile .
```

## 4. MATLAB R2026b

Ubuntu 24.04 is a validated platform for MATLAB and the recommended one for the ROS Toolbox.

### Dependencies

MathWorks publishes the exact package list per release and Ubuntu version in its [container-images repository](https://github.com/mathworks-ref-arch/container-images/tree/main/matlab-deps). Open the `r2026b/ubuntu24.04` folder, read `base-dependencies.txt`, and install those packages with apt.

### Install

Install into a directory you own, so the installer never runs as root and never needs X access for root:

```bash
mkdir -p ~/matlab/R2026b
```

Either download the Linux installer from your MathWorks account, unzip it and run `./install`, or use the MATLAB Package Manager:

```bash
wget https://www.mathworks.com/mpm/glnxa64/mpm && chmod +x mpm
```

```bash
./mpm install --release=R2026b --destination="$HOME/matlab/R2026b" \
  --products MATLAB Simulink ROS_Toolbox Robotics_System_Toolbox Control_System_Toolbox
```

Adjust the product list to your licence. `mpm` does not activate the licence; sign in on first launch. Add `~/matlab/R2026b/bin` to your `PATH`.

Starting with R2026b, MATLAB no longer bundles Java on Linux. Install the **MATLAB Support for OpenJDK** add-on from the Add-On Explorer when a feature asks for it.

### ROS Toolbox

The toolbox needs Python 3.10 (recommended) or 3.11. Ubuntu 24.04 ships 3.12, so add 3.10 beside it without touching the system interpreter:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

```bash
sudo apt update && sudo apt install python3.10 python3.10-venv python3.10-dev
```

In MATLAB, open **Home → Preferences → ROS Toolbox**, set the Python executable to `/usr/bin/python3.10`, and let it recreate its virtual environment. The system GCC 13 is inside the supported 6.3 to 14 range, so custom message generation works with the default compiler.

To talk to native nodes, match the domain before starting MATLAB:

```bash
export ROS_DOMAIN_ID=42 && matlab
```

Check from the MATLAB prompt with `ros2 topic list` while the talker from section 3 runs. If MATLAB and the native nodes use different middleware and cannot see each other, set the same `RMW_IMPLEMENTATION` on both sides.

### GPU

`gpuDevice` in MATLAB should report the RTX 3050. It needs only the driver.

## 5. KiCad

For KiCad 10 as a native package:

```bash
sudo add-apt-repository ppa:kicad/kicad-10.0-releases
```

```bash
sudo apt update && sudo apt install kicad
```

Or as a Flatpak, which is isolated from the system and equally current:

```bash
flatpak install --from https://flathub.org/repo/appstream/org.kicad.KiCad.flatpakref
```

Pick one. The PPA build integrates better with external tools and scripting; the Flatpak adds no third-party apt source.

## 6. Embedded tools

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

Group membership (`dialout`, `plugdev`) was set in the install chapter. Vendor tools with Ubuntu installers install as documented by the vendor: STM32CubeIDE and STM32CubeProgrammer, the nRF tools, and PX4's `Tools/setup/ubuntu.sh`. PlatformIO and west install per user:

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
- [ ] Talker and listener exchange messages natively.
- [ ] RViz and Gazebo render on the NVIDIA GPU.
- [ ] MATLAB starts, `gpuDevice` reports the GPU, and `ros2 topic list` sees the native talker.
- [ ] A custom ROS message builds in MATLAB.
- [ ] KiCad opens a project and the 3D viewer renders.
- [ ] A USB serial board and a debug probe work as a normal user.

Continue with [performance](04-performance.md).
