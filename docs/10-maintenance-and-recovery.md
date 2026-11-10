# Maintenance and recovery

## Weekly update routine

1. Finish active work, commit source changes and complete an external backup.
2. Read CachyOS and Arch news for manual interventions relevant to your installed packages.
3. Confirm free space and an existing root snapshot configuration.
4. Update on AC power; reboot for kernel/driver changes.
5. Test graphics, Bluetooth, a call and one suspend/resume before a field session or important demo.

```bash
df -h /
sudo snapper list-configs
# Only if a config named root already exists:
sudo snapper -c root create --description 'before planned system update'
sudo pacman -Syu
```

Do not interrupt pacman or perform partial upgrades. Review `.pacnew` files using `pacdiff` after relevant configuration changes. If using an AUR package, review its source/build updates separately. [Arch system maintenance](https://wiki.archlinux.org/title/System_maintenance), [CachyOS news](https://cachyos.org/blog/).

## Snapshots and rollback

Snapshots help recover system changes but do not protect against SSD failure or an erased disk. Root snapshots do not automatically include home, container data on separate subvolumes, or EFI assets. Inspect actual coverage in Btrfs Assistant and Snapper. CachyOS documents bootloader-specific recovery; use the section for the bootloader you installed. [Snapshot guide](https://wiki.cachyos.org/configuration/btrfs_snapshots/).

Set a modest retention policy in Btrfs Assistant, inspect space use and enable the appropriate cleanup timer. Keep several known-good states around major updates. Do not copy another distribution's `snapper rollback` command onto a different subvolume layout.

Recovery order:

1. Boot the LTS kernel. If it works, record the failing main-kernel/driver versions.
2. If the update broke userspace, boot a known-good snapshot using the configured boot menu.
3. Use the documented restore operation for that bootloader/layout; a temporary snapshot boot is not necessarily a permanent restoration.
4. Check kernel, initramfs, modules and EFI/boot files for consistency before rebooting.
5. If the system cannot boot, use the CachyOS live USB and its documented chroot helper. Unlock encrypted volumes first and identify the correct root subvolume.

Rehearse recovery before relying on it. Never remove both working kernels to save space.

## External backups with restic

Choose an external disk or remote repository. Keep its password outside the laptop as well as in your password manager. These commands use an **example path**; replace it with a verified, mounted external destination. [Restic preparing a repository](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html), [backup](https://restic.readthedocs.io/en/stable/040_backup.html), [restore](https://restic.readthedocs.io/en/stable/050_restore.html).

```bash
findmnt /run/media/USER/BACKUP
# Stop if that is not the intended external filesystem.
restic -r /run/media/USER/BACKUP/workstation-restic init
restic -r /run/media/USER/BACKUP/workstation-restic backup \
  "$HOME/Projects" "$HOME/Documents" "$HOME/.config" "$HOME/.ssh" \
  --exclude '**/.venv' --exclude '**/node_modules' \
  --exclude '**/build' --exclude '**/.cache'
restic -r /run/media/USER/BACKUP/workstation-restic snapshots
restic -r /run/media/USER/BACKUP/workstation-restic check
restic -r /run/media/USER/BACKUP/workstation-restic restore latest \
  --target "$HOME/restore-check"
```

Initialize only once. Customize the selected folders and exclusions: any excluded build directory containing unique data will not be backed up. Include additional personal folders, GPG material and application exports that matter to you. Compare restored files before deleting the temporary restore. Back up `/etc` and boot/EFI configuration separately using suitable permissions and encryption. Do not commit backup credentials here.

Automate backup only after a manual restore succeeds. Require the external mount to be present before writing, so an absent drive cannot silently redirect backups into a local mountpoint directory.

## Monthly storage review

```bash
df -h /
podman system df
du -sh "$HOME/.local/share/containers" "$HOME/.cache" 2>/dev/null
sudo btrfs filesystem usage /
sudo snapper -c root list
paccache -dk2
```

The last command is a dry run of keeping two package versions. If reviewed and appropriate, `sudo paccache -rk2` performs cleanup. Keep rollback needs in mind. Delete only identified unused container images, finished build outputs and unneeded datasets. Avoid blanket container pruning with volumes; volumes may hold the only copy of work. Routine Btrfs balancing is not a general cleanup step.

## Fast troubleshooting map

| Problem | First checks | Recovery direction |
|---|---|---|
| Black screen after update | LTS boot, TTY, kernel/NVIDIA package matching | Distribution-supported driver repair, then snapshot recovery if needed |
| Wi-Fi/Bluetooth disappears | rfkill, USB/PCI presence, kernel firmware logs | Cold boot and alternate kernel; compare live media |
| Audio fidelity drops | Headset profile and active microphone | A2DP + laptop mic; see audio guide |
| USB permission denied | Actual node owner/group and udev rules | Correct host permissions, new login, recreate container |
| ROS discovery fails | Domain, discovery range, QoS, network interface | Match settings and scoped firewall rules |
| CUDA unavailable | Host driver, wheel build, CDI if containerized | Fix the failing layer; avoid reinstalling every component |
| Laptop freezes under load | RAM pressure, disk space, thermals | Reduce parallel jobs and concurrent workloads |

Keep a short change log: date, kernel/driver, what changed, what broke and how it was resolved. That is more useful than accumulating unexplained sysctl and modprobe overrides.
