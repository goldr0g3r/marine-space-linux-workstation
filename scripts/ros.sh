#!/usr/bin/env bash
# Rootless, host-network ROS CLI environment. No GUI or privileged mode.
set -euo pipefail
if [[ ${1:-} == --help ]]; then
  cat <<'EOF'
Usage: bash scripts/ros.sh [command [arguments...]]
Default command: bash
Environment: ROS_IMAGE, ROS_WORKSPACE, ROS_DOMAIN_ID (42),
ROS_AUTOMATIC_DISCOVERY_RANGE (LOCALHOST), ROS_MEMORY (8g), ROS_CPUS (6),
ROS_DEVICE (one serial device path), ROS_GPU (0 or 1; requires NVIDIA CDI).
Host network is shared. Only the chosen workspace is bind mounted.
EOF
  exit 0
fi
command -v podman >/dev/null || { printf 'Install Podman first.\n' >&2; exit 1; }
repo_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
workspace=${ROS_WORKSPACE:-"$repo_dir/workspaces/ros"}
mkdir -p -- "$workspace"
workspace=$(cd -- "$workspace" && pwd)
image=${ROS_IMAGE:-localhost/robotics-jazzy}
podman image exists "$image" || {
  printf 'Build first: podman build -t localhost/robotics-jazzy -f containers/ros/Containerfile .\n' >&2
  exit 1
}
args=(run --rm --runtime crun --userns=keep-id --group-add keep-groups
  --network=host --memory "${ROS_MEMORY:-8g}" --cpus "${ROS_CPUS:-6}"
  -e HOME=/tmp/ros-home
  -e "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-42}"
  -e "ROS_AUTOMATIC_DISCOVERY_RANGE=${ROS_AUTOMATIC_DISCOVERY_RANGE:-LOCALHOST}"
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
  -v "$workspace:/workspace" -w /workspace)
if [[ -t 0 && -t 1 ]]; then args+=(-it); fi
if [[ -n ${ROS_DEVICE:-} ]]; then
  [[ -c $ROS_DEVICE ]] || { printf 'ROS_DEVICE must name a character device.\n' >&2; exit 2; }
  args+=(--device "$ROS_DEVICE:/dev/robot")
fi
if [[ ${ROS_GPU:-0} == 1 ]]; then args+=(--device nvidia.com/gpu=all); fi
if [[ $# -eq 0 ]]; then set -- bash; fi
exec podman "${args[@]}" "$image" bash -c 'mkdir -p "$HOME"; exec "$@"' -- "$@"
