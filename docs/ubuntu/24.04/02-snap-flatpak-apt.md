# Ubuntu 24.04: keep snap, default to apt and Flatpak

Previous: [installation](01-install.md). Next: [toolchain](03-toolchain.md).

## Policy

Snap stays installed and working. It is simply not where new software comes from.

| Source | Use it for | Examples |
|---|---|---|
| **apt** | The system, drivers, compilers, libraries, ROS 2, anything that talks to hardware | NVIDIA driver, `ros-jazzy-*`, `gcc-arm-none-eabi`, Podman, VS Code from Microsoft's repository |
| **Flatpak** | Sandboxed desktop applications | Browser, chat, media, office, KiCad if you want the newest build |
| **snap** | Only what Ubuntu ships as a snap | Firmware updater, App Center, the seeded Firefox, core runtimes |
| **Containers** | Project userspace that must be reproducible | The ROS image in this repository, CUDA stacks, other ROS releases |

## Why snapd is not removed

- Ubuntu ships part of the desktop as snaps: Firefox, the App Center, the firmware updater and their runtimes. See your list with `snap list`.
- Some `.deb` packages are stubs that install a snap. Purging snapd leaves those in a broken or half-configured state.
- Release upgrades and Canonical's testing assume snapd is present. Removing it is the kind of deviation that makes later updates fail in ways nobody else reproduces.

So the rule is: **never `apt purge snapd`, never remove `core*`, `snapd`, `bare`, `gtk-common-themes` or `gnome-*` runtime snaps, never mask `snapd.service`.**

## 1. Add Flatpak and Flathub

```bash
sudo apt install flatpak
```

```bash
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

Reboot once so application menus and portals pick it up.

## 2. Make the graphical store show apt and Flatpak

**Kubuntu.** Discover already handles apt:

```bash
sudo apt install plasma-discover-backend-flatpak
```

In Discover, open Settings and make Flathub the default source. The snap backend can stay installed; it just stops being the first result.

**Ubuntu Desktop.** The App Center only handles snaps and local `.deb` files. Add GNOME Software for apt and Flatpak, and leave the App Center installed for the snaps it manages:

```bash
sudo apt install gnome-software gnome-software-plugin-flatpak
```

Do not install `gnome-software-plugin-snap`. Use **Software** day to day and pin it to the dock in place of the App Center.

## 3. Stop apt installing snaps by surprise

A few archive packages are transitional: installing the `.deb` installs a snap. Check before installing anything unfamiliar:

```bash
apt show chromium-browser 2>/dev/null | grep -i -E 'snap|transitional'
```

Block the ones you would otherwise hit by accident. Create `/etc/apt/preferences.d/no-transitional-snaps`:

```text
Package: chromium-browser chromium-chromedriver
Pin: release o=Ubuntu
Pin-Priority: -1
```

Leave the already-installed `firefox` and `thunderbird` stub packages alone. Pinning or removing them causes more trouble than the disk space is worth.

## 4. Browser

Keep the Firefox snap installed as the fallback, and install the Flatpak for daily use:

```bash
flatpak install flathub org.mozilla.firefox
```

Set it as the default browser in system settings. If you want a native `.deb` instead, use [Mozilla's own apt repository](https://support.mozilla.org/en-US/kb/install-firefox-linux), which includes the pinning needed to outrank the Ubuntu stub.

## 5. Keep snap quiet and predictable

Snaps refresh on their own schedule. Move that to a window when you are not working:

```bash
sudo snap set system refresh.timer=sat,02:00-05:00
```

Keep only two revisions of each snap on disk:

```bash
sudo snap set system refresh.retain=2
```

Before a demo, exam or field day, hold all refreshes for a few days:

```bash
sudo snap refresh --hold=72h
```

```bash
sudo snap refresh --unhold
```

Do not hold refreshes indefinitely; the core snaps carry security fixes. Useful checks:

```bash
snap refresh --time
```

```bash
snap changes
```

## 6. Flatpak notes for engineering work

- **Sandboxing hides hardware.** Serial ports, debug probes and USB devices are not visible to a Flatpak unless you grant access. Install anything that flashes or debugs boards from apt or the vendor: STM32CubeIDE, Arduino IDE, serial terminals, PlatformIO.
- **Editors and IDEs** need your compilers and ROS environment. Install VS Code from [Microsoft's apt repository](https://code.visualstudio.com/docs/setup/linux), not Flatpak or snap.
- **Permissions.** Install Flatseal to inspect and adjust them:

```bash
flatpak install flathub com.github.tchx84.Flatseal
```

- **NVIDIA.** Flatpak downloads a GL runtime matching the host driver. After every NVIDIA driver update run `flatpak update`, or Flatpak apps fall back to software rendering.

## 7. Update routine

Weekly, on AC power:

```bash
sudo apt update && sudo apt full-upgrade
```

```bash
flatpak update
```

```bash
sudo snap refresh
```

Leave `unattended-upgrades` enabled; it applies security updates from the Ubuntu archive between your manual runs. Take a Timeshift snapshot before an update that changes the kernel or the NVIDIA driver.

## 8. Third-party apt sources

PPAs and vendor repositories are the main way an LTS install breaks. Keep the list short and written down:

| Source | Why |
|---|---|
| ROS 2 (`ros2-apt-source`) | Jazzy |
| NVIDIA Container Toolkit | GPU in containers |
| KiCad PPA | KiCad 10 |
| deadsnakes PPA | Python 3.10 for the MATLAB ROS Toolbox |
| Microsoft | VS Code |

List what is configured with:

```bash
apt policy | grep -E 'https?://' | sort -u
```

Before a release upgrade, disable every third-party source and re-enable them one at a time afterwards.

## Acceptance checks

- [ ] `snap list` still shows the seeded snaps and `snap changes` shows no errors.
- [ ] `flatpak remotes` lists Flathub.
- [ ] The graphical store offers apt and Flatpak results.
- [ ] `apt install chromium-browser` is refused by the pin.
- [ ] `snap refresh --time` shows the weekend window.

Continue with [the toolchain](03-toolchain.md).
