# First sensor lab: publish, record and replay

This exercise turns the container smoke test into a small robotics workflow. It needs no board, GPU or simulator. You will produce timestamped synthetic temperature readings, inspect them, record a bag and replay it with the original publisher stopped.

The included [Python example](../examples/ros/temperature_publisher.py) publishes `sensor_msgs/msg/Temperature` at a target rate of 10 Hz, with a 30-second sinusoidal cycle between 18 and 22 degrees Celsius. Its values are synthetic. The frame name identifies the source; it does not create a TF transform. Variance is left unspecified rather than inventing sensor accuracy. [Message definition](https://github.com/ros2/common_interfaces/blob/jazzy/sensor_msgs/msg/Temperature.msg).

## Prepare once

Build the image using [the container guide](06-containers-and-ros.md). From the repository root:

```bash
mkdir -p workspaces/ros/sensor-lab
cp -i examples/ros/temperature_publisher.py workspaces/ros/sensor-lab/
```

`cp -i` asks before replacing an edited copy. Keep your changes in a project repository when the experiment becomes real work; `workspaces/` is ignored here.

## Publish and inspect

In terminal A:

```bash
bash scripts/ros.sh python3 /workspace/sensor-lab/temperature_publisher.py
```

In terminal B:

```bash
bash scripts/ros.sh ros2 topic info -v /lab/temperature
bash scripts/ros.sh ros2 topic echo /lab/temperature --once
bash scripts/ros.sh ros2 topic hz /lab/temperature
```

Stop `hz` with Ctrl-C. Expect approximately 10 Hz, Celsius readings within the stated bounds, a source frame and nonzero timestamps. Scheduling jitter is expected; this is a desktop process, not a deadline-guaranteed sensor driver. All terminals use the helper's same domain and local discovery scope.

## Record a short run

Leave terminal A publishing. In terminal B:

```bash
bash scripts/ros.sh ros2 bag record --storage mcap \
  --output /workspace/sensor-lab/run-01 --topics /lab/temperature
```

After about 20 seconds, stop recording with Ctrl-C and let it finish writing metadata. Then stop the publisher. Use a new output directory for each run; do not overwrite a recording to repeat the experiment.

```bash
bash scripts/ros.sh ros2 bag info /workspace/sensor-lab/run-01
```

Expect a nonzero message count, the correct topic/type and a duration close to the recording interval. Discovery/startup time means the count will not be exactly 200. Preserve the complete bag directory, including `metadata.yaml`, when copying it. [rosbag2 Jazzy documentation](https://github.com/ros2/rosbag2/blob/jazzy/README.md).

## Replay without the sensor process

Start terminal B first so the subscriber is ready:

```bash
bash scripts/ros.sh ros2 topic echo /lab/temperature --once
```

Then in terminal A:

```bash
bash scripts/ros.sh ros2 bag play /workspace/sensor-lab/run-01 --delay 2
```

The short delay gives discovery time before playback starts. Seeing a message now demonstrates playback from storage. Its header timestamp is from the original recording, not the current wall time. Playback publishes messages onto the ROS graph: keep this learning exercise local and separate from a live vehicle's domain.

For later time-dependent processing, playback can publish `/clock` with `--clock`; the consuming nodes must also use `use_sim_time`. That is unnecessary for the basic `echo` test. Keep the original source timestamps and bag receive timestamps distinct when measuring sensor latency.

## Acceptance and next steps

- [ ] Publisher emits the expected type, units, frame name and approximate rate.
- [ ] A bag records nonzero messages and can be inspected after the recorder exits.
- [ ] Replay works with the original publisher stopped.
- [ ] The bag directory survives container exit and remains owned by your host user.
- [ ] Experiment notes record the Git revision, image ID, topic, rate and collection conditions.

Next, write a subscriber that flags readings above a chosen threshold and test it on replayed data. Then replace the synthetic source with UART sensor readings while keeping units and timestamps explicit. Add missing-reading and malformed-packet cases before attempting a control loop.

If the topic exists but samples are absent, inspect publisher/subscriber QoS and use matching domain/discovery settings. If `ros2 bag` is unavailable in a different image, add the release-matched rosbag packages to that image; avoid installing ROS tools into the host Python environment.
