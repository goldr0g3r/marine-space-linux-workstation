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
- Checked all local Markdown link targets/anchors and balanced code fences across 18 Markdown documents, including the alternative installation path and acceptance template.
- Checked external link HTTP responses, corrected a moved micro-ROS tutorial link, and checked the additional EndeavourOS references. HTTP reachability does not guarantee that a page's instructions apply to every future version.
- Reviewed staged files for whitespace issues and kept test workspaces, logs and credentials out of the repository.
- On continuation, syntax-checked 48 Bash documentation examples with `bash -n` without executing their commands. This checks shell syntax, not whether each package, device or service is available on a future installation.

## Continuation update

Added the researched EndeavourOS installation path, a first-weekend execution plan and a reusable acceptance record. Checked upstream EndeavourOS kernel/recovery documentation and zram-generator configuration. No EndeavourOS installation or new host configuration was performed. The earlier ROS runtime results below remain the runtime evidence for this repository.

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
