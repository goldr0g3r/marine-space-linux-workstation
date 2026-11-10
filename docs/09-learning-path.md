# A practical marine/space robotics transition

Treat this as a sequence of deliverables, not a promise that twelve weeks produces professional competence. Adjust the pace to your available time. Your existing Linux/development experience lets you spend more time on electronics, timing, estimation and physical systems.

## Suggested milestones

| Stage | Focus | Concrete output | Completion evidence |
|---|---|---|---|
| Week 1 | Workstation and reproducibility | Working audio, backup and ROS CLI lab | Checklist, version record, successful restore |
| Weeks 2–3 | Embedded C/C++, MCU peripherals | UART sensor logger with timer and watchdog | Flash/debug instructions, captured bus trace, unit tests |
| Weeks 4–5 | RTOS and communications | Timestamped sensor task, bounded queue, error recovery | Timing measurements and injected-failure results |
| Weeks 6–7 | ROS 2 and geometry | Sensor node, transforms, launch/config and bag replay | Reproducible replay and correct units/frame definitions |
| Weeks 8–9 | Controls and estimation | PID simulation and basic state estimator | Plots against ground truth; noise/delay experiments |
| Weeks 10–11 | Marine or space branch | Small domain-specific demonstrator | Automated checks and a recorded demo |
| Week 12 onward | Integration and portfolio | A documented end-to-end system | Architecture, limitations, reproducible build and results |

Alongside coding, study linear algebra, coordinate transforms, probability, feedback/control stability, numerical methods, electronics and signal sampling. Keep each experiment small enough that you can explain every state variable and timing assumption.

## Marine branch

Start with a simulated vehicle and telemetry; add buoyancy, drag and sensor limitations later. Do not assume a generic wheeled-robot world models underwater dynamics.

1. **Telemetry lab:** generate synthetic pressure/depth and IMU data; timestamp, log and replay it through ROS.
2. **Autopilot lab:** run ArduPilot SITL in its own compatible Ubuntu environment. Use the upstream prerequisites and pin the source revision. Start with the documented vehicle/frame; select ArduSub only after checking that revision's supported model. [SITL setup](https://ardupilot.org/dev/docs/setting-up-sitl-on-linux.html).
3. **Ground station:** use a stable QGroundControl release compatible with the chosen firmware. Confirm MAVLink telemetry before attempting a mission. [QGroundControl installation](https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html).
4. **Control/estimation lab:** inject sensor noise, dropouts and communications latency. Plot tracking error and estimator drift.
5. **Portfolio:** a small simulated depth-hold system with explicit units, frame conventions, bounded commands and lost-link behavior.

A dedicated environment avoids mixing autopilot Python dependencies with ROS or PyTorch. Check FUSE/runtime requirements for an AppImage instead of disabling sandboxing indiscriminately. Keep simulated and physical vehicle connections clearly identified.

## Space branch

Start with component architecture, commands, events, telemetry and fault handling. NASA F´ provides a practical framework for learning these concepts; its installation guide uses `fprime-bootstrap` to create a project and environment. Use the current stable release instructions and record the selected version. [F´ installation](https://fprime.jpl.nasa.gov/latest/docs/getting-started/installing-fprime/).

Build a small component that accepts a command, changes state and emits telemetry. Add a periodic task, simulated sensor, timeout and fault event. Write tests that show recovery from invalid input and missed heartbeats. Later explore cFS if it aligns with your target roles. [NASA cFS repository](https://github.com/nasa/cFS).

A laptop simulation is a development artifact, not flight-qualified software. The useful skills are clear interfaces, reproducible builds, traceable requirements, tests and observable failure behavior.

## AI/ML branch

Use ML where there is a measurable task: classify sensor anomalies, detect a small set of objects, or estimate a quantity from data. Compare against a simple analytical/classical baseline. Keep training and evaluation recordings separate. Export an inference artifact, measure latency on the intended device and document failure cases before connecting it to control logic.

## Portfolio repository checklist

- [ ] One-paragraph problem statement and measurable acceptance criteria.
- [ ] Architecture diagram, interfaces, units and coordinate frames.
- [ ] Exact software/firmware revisions and container/environment definitions.
- [ ] Build, run, test and recovery instructions verified from a clean environment.
- [ ] Small redistributable sample data; external links for large datasets.
- [ ] Results, plots, known limitations and fault-injection observations.
- [ ] Short demo and a clear explanation of your engineering decisions.

Prefer one finished sensor-to-telemetry-to-control project over a laptop filled with unused frameworks.
