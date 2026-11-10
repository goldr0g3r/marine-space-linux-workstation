# Validation record

Prepared on 10 November 2026. This file distinguishes repository checks from hardware acceptance tests.

## Completed checks

- Local hardware inspection and confirmation of the target laptop with the owner.
- Package metadata lookup for every package in the four helper groups.
- Bash syntax checking and ShellCheck for the helper scripts.
- Read-only diagnostic helper executed on the existing system.
- ROS image built successfully with rootless Podman on the existing CachyOS installation.
- Two separate containers communicated using the provided helper: C++ talker to Python listener, with 14 messages received during a 15-second test. Both were stopped intentionally by `timeout` (exit 124).
- Created and built an `ament_python` package using colcon inside the container; sourced its overlay and resolved it with `ros2 pkg prefix`.
- Confirmed created source files retain the host user's UID/GID (1000:1000).
- Checked all local Markdown link targets/anchors and balanced code fences across 21 Markdown documents, including the alternative installation path, acceptance template and practical labs.
- Checked external link HTTP responses, corrected a moved micro-ROS tutorial link, and checked the additional EndeavourOS references. HTTP reachability does not guarantee that a page's instructions apply to every future version.
- Reviewed staged files for whitespace issues and kept test workspaces, logs and credentials out of the repository.
- Syntax-checked 70 Bash documentation examples with `bash -n` without executing their commands. This checks shell syntax, not whether each package, device or service is available on a future installation.

## Continuation update

Added the researched EndeavourOS installation path, a first-weekend execution plan and a reusable acceptance record. Checked upstream EndeavourOS kernel/recovery documentation and zram-generator configuration. No EndeavourOS installation or new host configuration was performed.

## Practical-lab validation

- Executed `examples/ros/temperature_publisher.py` in the existing rootless ROS image, using a separate ignored test workspace and local-only domain 77.
- Received a live `sensor_msgs/msg/Temperature` sample, then recorded **75 messages** over roughly **7.4 seconds** to MCAP during an eight-second recorder test.
- Deserialized every recorded sample and checked increasing source timestamps, temperature within 18–22 degrees Celsius, the expected frame name and unspecified variance.
- Stopped the original publisher, replayed the bag and received a stored message in a separate subscriber. Timed publisher/recorder exits were intentional, not test failures.
- Built `candump` and `cansend` from can-utils tag `v2025.01`, commit `01083a64ebf28cc716efe2d2fd51c141042ae34b`, using the documented CMake procedure. No system-wide install was performed.
- Parsed the Python example successfully. Test logs, recordings and the can-utils build remain under ignored `reports/` directories and are not uploaded.

The Ethernet profile, virtual CAN interface and image/volume backup recipes were researched and syntax-checked but not executed. A successful tools build does not validate a physical or virtual CAN exchange.

## Reproduction details

```bash
bash -n scripts/packages.sh scripts/doctor.sh scripts/ros.sh
podman run --rm -v "$PWD:/mnt:ro" docker.io/koalaman/shellcheck:stable \
  scripts/packages.sh scripts/doctor.sh scripts/ros.sh
podman build -t localhost/robotics-jazzy -f containers/ros/Containerfile .
```

The successful test image was approximately 937 MB. Recorded image ID:

```text
ed7fb992393c408e2755bf3ac0584e33d5bb46f2d471ca7fb54cc8db3f80dc84
```

The pulled base reported this repository digest (one of the returned digest references):

```text
docker.io/library/ros@sha256:8eed0a4669bbf43ee331878a4c39bd8ebddea8e3312a58b4fae8edb14526b617
```

The test workspace is ignored by Git. The image and downloaded base remain in local Podman storage for reuse; no images are uploaded to GitHub. Package previews are non-mutating; `--apply` was not used.

## Not performed

- No host package install, disk erase, OS reinstall, firmware flash, bootloader change or power/audio configuration change.
- No physical headset listening/call test, live USB test or suspend/resume cycle.
- No GPU container setup, PyTorch installation, CUDA numerical test, RViz/Gazebo GUI test or attached-board flashing.
- No cross-distro speed benchmark or battery measurement.

The full setup remains in [TODO.md](../TODO.md). Do not interpret a successful container build as validation of real hardware workflows.
