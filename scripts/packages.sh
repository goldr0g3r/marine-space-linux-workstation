#!/usr/bin/env bash
# Print by default; --apply performs one full pacman transaction.
set -euo pipefail

usage() {
  printf 'Usage: %s {core|containers|embedded|cad} [--apply]\n' "$0"
}
[[ $# -ge 1 && $# -le 2 ]] || { usage; exit 2; }
[[ $# -eq 1 || $2 == --apply ]] || { usage; exit 2; }
case "$1" in
  core) packages=(base-devel git cmake ninja clang gdb ccache python uv ripgrep fd jq tmux btop lm_sensors pciutils usbutils bluez bluez-utils pipewire pipewire-pulse wireplumber pavucontrol restic pacman-contrib) ;;
  containers) packages=(podman crun distrobox) ;;
  embedded) packages=(arm-none-eabi-gcc arm-none-eabi-newlib arm-none-eabi-gdb openocd dfu-util picocom sigrok-cli pulseview dtc gperf) ;;
  cad) packages=(kicad freecad) ;;
  *) usage; exit 2 ;;
esac
printf 'Command:'
printf ' %q' sudo pacman -Syu --needed "${packages[@]}"
printf '\n'
if [[ ${2:-} != --apply ]]; then
  printf 'Preview only. Read docs/05-applications.md before applying.\n'
  exit 0
fi
[[ -r /etc/os-release ]] || { printf 'Cannot identify distribution.\n' >&2; exit 1; }
# shellcheck disable=SC1091
. /etc/os-release
[[ ${ID:-} == cachyos ]] || { printf 'This helper targets CachyOS only.\n' >&2; exit 1; }
command -v pacman >/dev/null
exec sudo pacman -Syu --needed "${packages[@]}"
