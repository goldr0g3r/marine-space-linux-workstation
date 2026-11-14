# Distro decision for supported toolchains

Decided on **14 November 2026**. The [earlier decision](../01-distro-decision.md) chose CachyOS for a performance-first brief. This one answers a different brief.

## Requirements

Gathered by asking before researching:

| Question | Answer |
|---|---|
| ROS 2 native or containers? | Either, whichever is most reliable |
| Robotics stack | Gazebo and RViz, real hardware and embedded targets, CUDA and ML |
| PCB tools | KiCad only |
| Release model | No preference |
| Stated problem | Toolchain support on CachyOS for robotics, MATLAB and PCB design |
| Operator | Experienced with Linux, Podman and Docker |

Hard constraint implied by the brief: tools must work as their vendors intend, without the worry that an update breaks them.

## Findings

| Vendor source | What it supports |
|---|---|
| MATLAB R2026b | Ubuntu 22.04, 24.04, 26.04; Debian 12, 13; RHEL 8, 9, 10; SLES 15. Others with kernel 4.18+ and glibc 2.28+ "will likely run" with limited support |
| MATLAB ROS Toolbox R2026b | Ubuntu 24.04 (recommended), 22.04; Debian 12, 13. Targets ROS 2 Jazzy. Python 3.10 (recommended) or 3.11. GCC 6.3 to 14 |
| ROS 2 Jazzy | Tier 1 on Ubuntu 24.04. Supported to May 2029. Pairs with Gazebo Harmonic |
| ROS 2 Lyrical | Tier 1 on Ubuntu 26.04 only. Tier 2 on RHEL 10. Tier 3 on Ubuntu 24.04 and Debian 13. Pairs with Gazebo Jetty |
| CUDA 13.5 | Ubuntu 22.04, 24.04 (kernel 7.0 HWE), 26.04; Debian 12, 13; Fedora 44; RHEL family; SLES and Leap. No Arch-based distro |
| KiCad 10.0.8 | Official PPA for Ubuntu flavours; Flatpak everywhere |
| Ubuntu 26.04 field reports | Several forum and bug reports of suspend hangs on NVIDIA hybrid laptops with kernel 7.0.x. No confirmation of a fix was found |

Two facts decide the outcome. First, Ubuntu 24.04 is the only release named by MATLAB, the ROS Toolbox, ROS 2 Tier 1 and CUDA at the same time. Second, the ROS Toolbox still targets Jazzy, which has no native packages on 26.04.

## Decision matrix

Scores are 1 to 5 and are judgements made from the findings, not measurements. Weights sum to 100.

| Criterion | Weight | Ubuntu 24.04 | Pop!_OS 24.04 | Ubuntu 26.04 | Debian 13 | Atomic (Bluefin) | Fedora | CachyOS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| MATLAB + ROS Toolbox support | 20 | 5 | 4 | 3 | 4 | 2 | 2 | 1 |
| ROS 2 + Gazebo native support | 20 | 5 | 5 | 4 | 2 | 2 | 2 | 2 |
| NVIDIA/CUDA on a hybrid laptop | 15 | 5 | 5 | 4 | 4 | 4 | 3 | 3 |
| Embedded/hardware toolchains | 15 | 5 | 5 | 4 | 3 | 2 | 3 | 2 |
| Stability / regression risk | 15 | 5 | 4 | 3 | 5 | 5 | 3 | 2 |
| Performance | 5 | 3 | 4 | 4 | 3 | 4 | 4 | 5 |
| KiCad currency | 5 | 4 | 4 | 5 | 3 | 4 | 5 | 5 |
| Package freshness | 5 | 2 | 3 | 4 | 2 | 4 | 5 | 5 |
| **Weighted score (out of 5)** | | **4.70** | **4.45** | **3.70** | **3.40** | **3.05** | **2.85** | **2.40** |

The weighted score is the sum of weight × score, divided by 100.

### Sensitivity

Tripling the performance and freshness weights (to 15 each, taken evenly from the first two rows) gives Pop!_OS 24.04 4.25, Ubuntu 24.04 4.20, Ubuntu 26.04 3.80 and CachyOS 3.10. The Ubuntu 24.04 package base still wins under that weighting; only the choice between Ubuntu and its derivative flips, by 0.05. The first four rows carry the result, and those rows are vendor support statements, which are the least subjective inputs.

The ranking would change if MathWorks moved the ROS Toolbox to Lyrical and Ubuntu 26.04. At that point 26.04 scores 5 on the first two rows and overtakes 24.04.

## Why each alternative loses

- **Ubuntu 26.04.** MATLAB is supported, but the ROS Toolbox does not list it, and Jazzy is container-only there. System Python is 3.14 and GCC is 15, both outside the toolbox's listed ranges. Suspend reports on NVIDIA hybrids add risk.
- **Pop!_OS 24.04.** Same package base and good hybrid-graphics handling. MathWorks does not name it, and the COSMIC desktop is young.
- **Debian 13.** MATLAB and the ROS Toolbox list it, but ROS 2 is Tier 3 there, which means source builds or containers.
- **Fedora, atomic desktops, CachyOS.** Everything works only through containers or unofficial paths. That is the situation the brief is trying to leave.

## What Ubuntu 24.04 costs

- CachyOS's optimised kernel and packages are gone. The difference was not measured on this laptop.
- Base packages are older. Newer software comes from Flatpak, PPAs and containers.
- Lyrical needs a container.
- Kubuntu 24.04 ships Plasma 5.27, not Plasma 6.
- The ROS Toolbox needs Python 3.10 or 3.11 beside the system's 3.12.

## Flavour

Ubuntu Desktop (GNOME) is what vendors test. Kubuntu is an official flavour on the same archive, kernel and drivers, and it matches the KDE workflow the rest of this repository assumes. Either is fine. The guides give commands for both where they differ.

## Sources

- [MATLAB R2026b Linux system requirements](https://www.mathworks.com/support/requirements/matlab-linux.html)
- [MATLAB ROS Toolbox system requirements](https://www.mathworks.com/help/ros/gs/ros-system-requirements.html)
- [MATLAB R2026b release notes](https://www.mathworks.com/help/matlab/release-notes-R2026b.html)
- [ROS 2 Lyrical supported platforms](https://docs.ros.org/en/lyrical/Releases/lyrical/supported-platforms.html)
- [ROS 2 Lyrical release announcement](https://discourse.openrobotics.org/t/ros-2-lyrical-luth-released/55021)
- [ROS 2 Jazzy deb installation](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
- [Gazebo and ROS pairings](https://gazebosim.org/docs/latest/ros_installation/)
- [NVIDIA CUDA installation guide for Linux](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)
- [NVIDIA Container Toolkit installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [NVIDIA CDI support](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/cdi-support.html)
- [KiCad Linux packages](https://www.kicad.org/download/linux-distros/)
- [Ubuntu 26.04 summary for LTS users](https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/)
- [Ubuntu 26.04.1 changes](https://documentation.ubuntu.com/release-notes/26.04/1/)
- [Ubuntu 24.04.5 with the Linux 7.0 HWE stack](https://phoronix.com/news/Ubuntu-24.04.5-LTS)
- [Ubuntu 26.04 suspend report on the NVIDIA forum](https://forums.developer.nvidia.com/t/ubuntu-26-04-suspend-resumes-to-black-screen/365785)

Not machine-readable during research: the docs.ros.org installation pages refused automated access. The Jazzy commands were taken from the same text in the [ros2_documentation repository](https://github.com/ros2/ros2_documentation/tree/jazzy/source/Installation). The Lyrical deb page was not read; check it before installing Lyrical.
