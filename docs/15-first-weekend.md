# First-weekend execution plan

This turns the longer guide into an ordered setup session. Time ranges are planning estimates, excluding large downloads and any unexpected recovery work. Do not rush the backup or partition review to fit the schedule.

## Before the weekend: choose and prepare

**Deliverable:** verified backup, installer USB, recovery information and an explicit disk target.

1. Read [the recommendation](01-distro-decision.md) and [CachyOS versus EndeavourOS](13-cachyos-vs-endeavouros.md). Pick one host; keep the other as an alternative if acceptance tests fail.
2. Complete the pre-install section of [TODO.md](../TODO.md). Preserve the separate Windows SSD unless you explicitly decide otherwise.
3. Confirm you can sign in to GitHub and your password manager from another device.
4. Keep a copy of these Markdown documents on a phone, external drive or second machine. The laptop's local copy will not survive erasing its Linux filesystem.
5. Copy [the acceptance record](../templates/acceptance-record.md) into private notes or `reports/` in a surviving clone. `reports/` is ignored by Git.

**Proceed when:** a restored sample file matches its original, your installer is verified and the intended disk is unambiguous.

## Session 1: operating system, 1–3 hours

Use [the CachyOS install chapter](02-fresh-install.md) or [the EndeavourOS chapter](14-endeavouros-install.md). Complete installation, full update and reboot. Confirm the expected desktop, kernel and disk layout, then check NVIDIA, Wi-Fi and basic audio.

Choose a browser/editor, restore only necessary credentials and verify external backup access. Keep old system-wide audio, GPU and power overrides out of the fresh configuration until a specific need appears.

**Proceed when:** normal boot works, networking is reliable, the display is usable and the Windows disk remains intact. If graphics fail, diagnose that before adding SDKs.

## Session 2: audio and recovery, 1–2 hours

Use the [Realme audio tests](04-bluetooth-audio.md#acceptance-matrix). Start with phone multipoint disconnected and 5 GHz Wi-Fi where available. Compare offered AAC and SBC profiles, test a call with the laptop microphone, then test the neckband microphone separately.

Check suspend/resume and test the LTS kernel. Configure one snapshot system appropriate to the chosen distro/bootloader, and perform a small external backup/restore check.

**Proceed when:** you have a repeatable daily audio configuration and know how to boot a working fallback. If headset audio still fails, capture the exact failure and profile instead of changing many settings at once.

## Session 3: core development, 1–2 hours

Install Git, your editor, C/C++ tools and Podman. Build the supplied ROS image and run the talker/listener pair. Build one package using the container guide. Confirm created files belong to your normal user.

Keep the CLI environment first. Add RViz/Gazebo only after the small example works; that makes GUI/driver problems easier to distinguish from ROS/networking problems.

**Proceed when:** two containers exchange messages, a package builds and your source changes persist after the container exits.

## Session 4: choose one engineering branch

| Available equipment / immediate goal | First task | Success evidence |
|---|---|---|
| MCU board and debug probe | Blinky, breakpoint and UART output | You can reproduce build/flash/debug from written steps |
| No board yet | [Synthetic sensor lab](16-first-sensor-lab.md): publisher, recording and replay | Replayed data matches expected values and timestamps |
| AI/ML first | Small CPU dataset baseline, then CUDA smoke test | Saved evaluation and a passing numerical test if using GPU |
| Marine simulation first | Minimal documented SITL exercise | Telemetry reaches the ground station |
| Space software first | F´ command/event/telemetry example | Command changes state and emits expected telemetry |

Avoid installing all branches before finishing one. The laptop's 16 GB RAM and 4 GB VRAM reward small, reproducible workloads.

## End-of-weekend handover to yourself

Save the chosen kernel/driver/audio profile and the acceptance record. Write down unresolved issues, the next project and the recovery procedure. Back up the new project and restore one file. Keep roughly 70–90 GiB free instead of filling the SSD with speculative SDKs and datasets.

The initial setup is complete when you can develop, listen, call, reboot and recover reliably—not when every suggested application is installed.
