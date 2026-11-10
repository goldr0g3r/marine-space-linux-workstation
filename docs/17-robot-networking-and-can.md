# Robot networking and CAN practice

These are optional steps for a bench or field project. They do not change the laptop automatically. Keep each experiment on a deliberately chosen interface or virtual bus.

## Dedicated Ethernet without losing Wi-Fi internet

A wired robot connection can make transfers and discovery easier to diagnose. First identify the Ethernet device, existing profiles and routes:

```bash
nmcli device status
nmcli connection show
ip -4 address
ip -4 route
```

Choose an unused private subnet that does not overlap Wi-Fi, VPNs or other lab networks. The example below uses laptop `192.168.50.10/24` and robot `192.168.50.20/24`. These are examples, not addresses detected on your equipment. Configure the robot separately and verify there are no duplicate addresses.

Replace the interface placeholder with the observed Ethernet name. Run this from the laptop locally, not over the interface you are reconfiguring:

```bash
robot_if=REPLACE_WITH_ETHERNET_INTERFACE
sudo nmcli connection add type ethernet ifname "$robot_if" \
  con-name robotics-bench connection.autoconnect no \
  ipv4.method manual ipv4.addresses 192.168.50.10/24 \
  ipv4.never-default yes ipv6.method disabled
sudo nmcli connection up robotics-bench
ip -4 route get 192.168.50.20
ping -c 3 192.168.50.20
```

The profile has no default gateway or DNS server; Wi-Fi can remain the internet route. `never-default` makes that intent explicit. Disabling IPv6 applies only to this example IPv4 bench profile. Do not copy the profile onto a network that needs IPv6. [NetworkManager settings](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-nmcli.html).

When finished, deactivate the profile and restore the prior Ethernet connection if needed:

```bash
sudo nmcli connection down robotics-bench
```

To remove this newly created profile later, use `sudo nmcli connection delete robotics-bench` only after confirming it is the profile you created. [nmcli reference](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nmcli.html).

## Move from IP reachability to ROS

Use the robot's matching ROS domain and compatible message definitions. For the supplied helper, enable subnet discovery explicitly:

```bash
ROS_AUTOMATIC_DISCOVERY_RANGE=SUBNET ROS_DOMAIN_ID=42 bash scripts/ros.sh
```

If the route is correct but discovery fails, inspect the selected interface, multicast behavior, VPN routes and firewall. Allow only the traffic needed on the bench interface; do not make every network trusted. A successful ping does not prove DDS discovery or QoS compatibility.

Check clocks on the laptop and companion computer with `timedatectl status`. Use a common time source when comparing timestamps across machines. “Synchronized” alone is not proof of sub-millisecond agreement; measure offsets for tasks that require precision. Local duration measurements should use a monotonic clock. Never infer network latency by subtracting unsynchronized wall clocks.

For SSH/SCP, use the device's documented user and address and verify its host key on first connection. This guide cannot supply the correct credentials for hardware that has not been selected.

## Learn SocketCAN without an adapter

Virtual CAN lets you learn frame IDs, payload handling and SocketCAN APIs before choosing a physical adapter. It does not model transceivers, wiring, arbitration timing or electrical faults. [Linux SocketCAN documentation](https://docs.kernel.org/networking/can.html).

The inspected repository metadata did not provide `can-utils`, so do not assume `pacman -S can-utils` will work. Use a reviewed package if your distribution provides one, or build the upstream tagged release below with the C/C++ tools from the core setup. It keeps the tools in your project directory and does not install them system-wide:

```bash
git clone --branch v2025.01 --depth 1 https://github.com/linux-can/can-utils.git \
  "$HOME/Projects/can-utils-lab"
cmake -S "$HOME/Projects/can-utils-lab" \
  -B "$HOME/Projects/can-utils-lab/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$HOME/Projects/can-utils-lab/build" --target candump cansend --parallel 2
```

`v2025.01` is the release selected for this exercise, not a promise that it is always the latest. Inspect the [upstream release](https://github.com/linux-can/can-utils/releases/tag/v2025.01) when revisiting the guide. Use a new directory if that destination already contains work.

Before creating the virtual interface:

```bash
ip link show vcanlab0
```

If `vcanlab0` already exists, inspect who uses it or choose a different name. Only create it when absent:

```bash
sudo modprobe vcan
sudo ip link add dev vcanlab0 type vcan
sudo ip link set vcanlab0 up
```

In terminal A:

```bash
"$HOME/Projects/can-utils-lab/build/candump" vcanlab0
```

In terminal B:

```bash
"$HOME/Projects/can-utils-lab/build/cansend" vcanlab0 123#11223344
```

Expect CAN ID `123` and the four payload bytes in the receiver. Stop `candump`, then delete only this lab interface when finished:

```bash
sudo ip link delete vcanlab0
```

The two application commands use the host directly; do not grant a container broad privileges just to run this first exercise. Later, define payload byte order, units, scaling, message rate and a timeout in a small protocol document. A physical CAN bus additionally needs compatible adapters, bitrate and wiring/termination appropriate to its equipment. Never transfer arbitrary virtual-bus test frames onto a real vehicle.

Sources for tool behavior: [linux-can can-utils](https://github.com/linux-can/can-utils). Neither the Ethernet profile nor virtual interface was created during preparation of this guide.
