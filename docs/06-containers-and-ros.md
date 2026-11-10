# Containers and ROS 2

## Baseline and version choice

Use **rootless Podman + crun**. The included image uses Ubuntu 24.04-based ROS 2 Jazzy, Cyclone DDS and demo nodes. It is intentionally small and has no GUI. Jazzy/Harmonic is a supported pairing; choose Lyrical with its matching Ubuntu/Gazebo versions for projects that require that newer stack. Never mix ROS apt packages from different distributions. [ROS releases](https://github.com/ros2/ros2_documentation/blob/rolling/source/Releases.rst), [Gazebo compatibility](https://gazebosim.org/docs/harmonic/ros_installation/).

```bash
bash scripts/packages.sh containers --apply
podman info --format '{{.Host.Security.Rootless}} {{.Host.OCIRuntime.Name}}'
```

Expect `true` and `crun`. Rootless operation requires subordinate UID/GID ranges. If Podman reports those missing, inspect `/etc/subuid` and `/etc/subgid` for your username and follow the distribution's rootless setup; do not assign overlapping ranges by copying someone else's numbers.

## Build and run

From this repository:

```bash
podman build -t localhost/robotics-jazzy -f containers/ros/Containerfile .
# Terminal A:
bash scripts/ros.sh ros2 run demo_nodes_cpp talker
# Terminal B:
bash scripts/ros.sh ros2 run demo_nodes_py listener
```

The listener should print the talker's messages. Stop with Ctrl-C. The helper creates `workspaces/ros`, maps your UID, keeps supplementary groups, and shares the host network. It defaults to domain 42 and local-only discovery. It limits each container to 8 GiB RAM and 6 CPUs; limits are **per container**, so running several can still exhaust the host. [Podman run options](https://docs.podman.io/en/latest/markdown/podman-run.1.html).

Interactive shell:

```bash
bash scripts/ros.sh
# Inside:
mkdir -p src
cd src
ros2 pkg create --build-type ament_python sensor_lab --dependencies rclpy
cd /workspace
colcon build --symlink-install
source install/setup.bash
ros2 pkg prefix sensor_lab
```

Source the workspace overlay in each new shell after building. Build outputs and code persist in the bind mount; ad hoc apt installs inside a disposable container do not. Add persistent dependencies to the Containerfile and rebuild. `rosdep` may require network initialization and sufficient package-install permissions during a build stage; it is not automatically run by the helper.

For repeatable bases, record the pulled digest and use the provided build argument:

```bash
podman image inspect docker.io/library/ros:jazzy-ros-base-noble --format '{{json .RepoDigests}}'
# Substitute the actual digest from that output:
podman build --build-arg BASE_IMAGE=docker.io/library/ros@sha256:REPLACE_WITH_DIGEST \
  -t localhost/robotics-jazzy -f containers/ros/Containerfile .
```

Pinning the base does not freeze later apt repository contents. Preserve a known-good built image or use a package snapshot repository when exact rebuilds matter. Record source revisions, package versions and the built image ID alongside experiment results.

## Networking and a physical robot

For local learning, the helper's local-only discovery avoids advertising the lab to the LAN. For a robot on a trusted network:

```bash
ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET ROS_DOMAIN_ID=42 bash scripts/ros.sh
```

Set the same domain and compatible discovery configuration on the robot. Sharing host networking avoids a layer of rootless NAT, but multicast may still be blocked by Wi-Fi client isolation, a VPN or firewall. Test basic IP reachability, then ROS discovery; domain ID is not authentication. Limit firewall changes to the robot interface/network. Do not disable the entire firewall to make DDS work. For untrusted/shared networks, configure ROS security and explicit peers as appropriate.

If topics are missing: verify domain, discovery scope, RMW and message definitions; then inspect `ros2 topic list` and `ros2 topic info -v TOPIC`. If topics exist but no samples arrive, inspect QoS compatibility as well as networking. Containers cannot hide a host kernel or radio problem.

## USB serial access

First make the device accessible to your normal host user as described in [embedded setup](07-embedded.md). Then:

```bash
# Replace the by-id path with the actual device; helper resolves it for Podman.
ROS_DEVICE=/dev/serial/by-id/REPLACE_WITH_BOARD bash scripts/ros.sh
# Inside, the exposed device is /dev/robot.
```

The helper uses crun's supplementary-group support. After changing host groups, log out fully or reboot before testing. Recreate the container after unplug/replug if the node changes. Debug probes that use USB buses need their own narrow access configuration; the serial option is not a generic USB passthrough switch. Do not use `--privileged` as the default repair.

## GUI robotics: optional trusted Distrobox

For RViz/Gazebo, Distrobox handles desktop integration more conveniently than a hand-built X11 socket recipe. It is tightly integrated with your session and must be used only with trusted images. [Distrobox documentation](https://distrobox.it/usage/distrobox-create/).

```bash
mkdir -p "$HOME/Containers/ros-jazzy-home"
distrobox create --name ros-jazzy-gui \
  --image docker.io/library/ros:jazzy-ros-base-noble \
  --home "$HOME/Containers/ros-jazzy-home" \
  --additional-flags '--group-add keep-groups'
distrobox enter ros-jazzy-gui
# Inside the box:
sudo apt-get update
sudo apt-get install ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-rmw-cyclonedds-cpp
source /opt/ros/jazzy/setup.bash
export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
rviz2
```

Reapply those exports in each shell or put them in the box's own shell configuration. Begin with a simple empty scene on the iGPU. If NVIDIA graphics are needed, recreate a separate box with Distrobox's `--nvidia` option and verify rendering; driver integration depends on the installed versions. Do not assume a working CUDA CLI test proves OpenGL/Wayland rendering works. Do not use `xhost +`.

For a basic Gazebo demo, inside the prepared GUI box:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:='shapes.sdf'
```

On 16 GB RAM, use a small world, one robot and modest sensor resolutions. The GUI path is documented, but was not executed during preparation; validate it after the fresh install.

## Optional GPU compute containers

Install the distribution's `nvidia-container-toolkit` only after host `nvidia-smi` succeeds. Newer toolkit versions provide automatic CDI refresh. Inspect the supplied units, refresh and list devices:

```bash
sudo pacman -Syu --needed nvidia-container-toolkit
systemctl status nvidia-cdi-refresh.path
sudo systemctl restart nvidia-cdi-refresh.service
nvidia-ctk cdi list
ROS_GPU=1 bash scripts/ros.sh nvidia-smi
```

If your package lacks the refresh unit, use the manual generation procedure in NVIDIA's documentation and regenerate after driver changes. Avoid leaving duplicate stale CDI definitions in `/etc/cdi` and `/var/run/cdi`. [NVIDIA CDI guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html).

This is a device-access smoke test, not a CUDA numerical test; see [AI/ML](08-ai-ml.md). Do not mix legacy NVIDIA OCI hooks and CDI injection blindly. Docker is also valid, but choose one primary engine to avoid duplicate images and confusing device configuration; ordinary membership in Docker's rootful daemon group grants broad host privileges.
