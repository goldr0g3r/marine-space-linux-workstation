#!/usr/bin/env bash
# Read-only diagnostics. Does not collect serial numbers, MACs or full logs.
set -uo pipefail
run() {
  printf '\n###'
  printf ' %q' "$@"
  printf '\n'
  if command -v "$1" >/dev/null 2>&1; then
    "$@" 2>&1 || printf '(Unavailable, inactive or not permitted.)\n'
  else
    printf '(Command not installed.)\n'
  fi
}
printf 'Workstation inspection; review output before sharing. No changes made.\n'
run uname -r
run cat /sys/class/dmi/id/product_name
run lscpu
run free -h
run lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
run df -h /
run zramctl
run swapon --show
run lspci -nnk
run lsusb
run nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
run systemctl is-active bluetooth power-profiles-daemon tlp tuned
run systemctl --user is-active pipewire pipewire-pulse wireplumber
run powerprofilesctl get
run systemctl --failed --no-pager
run systemctl --user --failed --no-pager
run pacman -Q pipewire wireplumber bluez linux-firmware linux-cachyos linux-cachyos-lts
printf '\nListen, test suspend and flash a board separately; diagnostics cannot verify those outcomes.\n'
