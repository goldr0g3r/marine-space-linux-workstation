# Embedded development

## Start with one board and a debug probe

Use a board you already own if possible. Your first milestone needs a documented MCU, USB serial or UART adapter, a supported debug interface and a simple LED or sensor. Exact board/debug-probe models are not known, so flashing commands must come from that board's documentation.

```bash
bash scripts/packages.sh embedded --apply
arm-none-eabi-gcc --version
arm-none-eabi-gdb --version
openocd --version
```

Keep vendor-mandated compiler versions within a project SDK rather than replacing the host compiler. Never treat an arbitrary host `gcc` as an ARM cross compiler. Record board revision, SDK tag, compiler and flash/debug tool versions in each project.

## Serial permissions

Connect the board, then inspect its device node:

```bash
ls -l /dev/serial/by-id/
stat -c '%A %U %G %n' /dev/ttyACM0
id
```

Use the actual node; `/dev/ttyACM0` is an example. On Arch-family systems the group is often `uucp`, but check before changing membership. If that is the device's group:

```bash
sudo usermod -aG uucp "$USER"
# Fully log out and back in, or reboot; then verify with id.
picocom --baud 115200 /dev/serial/by-id/REPLACE_WITH_BOARD
```

Exit picocom with Ctrl-A then Ctrl-X. Match the firmware's baud rate. Prefer stable by-id paths over device numbers that change when another board is connected.

For a USB debug probe, install the vendor/project's documented udev rules. Inspect rules already shipped by OpenOCD before adding duplicates. Apply rules and replug only the target device:

```bash
pacman -Ql openocd | rg 'udev|rules'
sudo udevadm control --reload-rules
```

Do not use `chmod 777` on serial devices or run your editor as root. If a port keeps getting opened by another service, identify the process before disabling anything globally.

## Bare-metal learning loop

1. Build the board vendor's minimal blinky example from a pinned SDK release.
2. Flash using its exact target/probe configuration.
3. Halt at `main`, inspect a variable and step through a GPIO change.
4. Add UART logs, then a timer interrupt.
5. Read an I²C/SPI sensor and capture transactions using a supported logic analyzer.
6. Add watchdog recovery, explicit error handling and host-side unit tests for pure logic.

Keep a pin map and voltage levels next to the code. Use the board's documented logic levels and a common ground. The deliverable is a reproducible build/flash/debug procedure, not just a blinking LED.

## Zephyr

Use the release-specific [Zephyr getting-started guide](https://docs.zephyrproject.org/latest/develop/getting_started/index.html), including its Arch-family host prerequisites, a Python virtual environment, `west`, and the Zephyr SDK. The rolling `latest` guide can change; select a stable tag and record it. SDK compilers and project manifests matter more than the host distro.

A minimal workflow after installing the version-matched dependencies and `west`:

```bash
# Replace TAG with a selected supported Zephyr release tag.
west init -m https://github.com/zephyrproject-rtos/zephyr --mr TAG zephyr-workspace
cd zephyr-workspace
west update
west zephyr-export
# Install the selected release's Python requirements and SDK per its guide.
# Replace BOARD with the exact board target listed by that release:
west build -b BOARD zephyr/samples/basic/blinky
west flash
```

These are templates, not commands to run with literal TAG/BOARD. First pass the SDK's toolchain verification and ensure the board/debug runner is supported. Keep the workspace separate from ROS and ML environments.

## Other useful stacks

- **ESP-IDF:** use Espressif's supported install method and a pinned release; source its environment only in project shells. [Linux setup](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/get-started/linux-macos-setup.html).
- **FreeRTOS:** study tasks, queues, interrupts, deadlines and allocation discipline on a supported board. [Official documentation](https://www.freertos.org/Documentation/00-Overview).
- **PlatformIO:** convenient for supported boards; pin platforms/frameworks in the project rather than relying on whatever was installed globally. [Core installation](https://docs.platformio.org/en/latest/core/installation/index.html).
- **micro-ROS:** add after learning serial transport and ordinary ROS nodes; pin the agent/client versions together. [micro-ROS tutorials](https://micro.vulcanexus.org/docs/tutorials/).

Use the laptop for development, telemetry and planning. Put timing-critical motor/safety control on suitable embedded hardware; containers and a desktop scheduler do not provide a hard real-time guarantee.
