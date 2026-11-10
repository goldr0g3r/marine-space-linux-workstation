# Mini-project: a temperature monitor that handles missing data

Build on [the sensor recording/replay lab](16-first-sensor-lab.md). This project adds a subscriber with explicit states, hysteresis, invalid-input handling and a timeout. It publishes status only; it does not command an actuator.

The components are small enough to read completely:

| File | Purpose |
|---|---|
| [temperature_publisher.py](../examples/ros/temperature_publisher.py) | Synthetic source from the first lab |
| [temperature_monitor_logic.py](../examples/ros/temperature_monitor_logic.py) | State machine with no ROS dependency |
| [temperature_monitor.py](../examples/ros/temperature_monitor.py) | ROS subscriber, watchdog and status publisher |
| [test_temperature_monitor_logic.py](../tests/test_temperature_monitor_logic.py) | Deterministic threshold/timing contract tests |
| [check_temperature_monitor.py](../examples/ros/check_temperature_monitor.py) | Bounded live ROS fault/recovery check |

## Behavior and acceptance criteria

Default settings: high threshold **21.0 °C**, clear threshold **20.5 °C**, valid-data timeout **2 seconds**. They are demonstration values, not limits for a particular robot or environment.

| State | Meaning | Example trigger |
|---|---|---|
| `WAITING` | No reading yet; initial timeout has not elapsed | Start monitor before source |
| `NORMAL` | Recent valid reading and high alarm not latched | 20.0 °C |
| `HIGH` | High threshold crossed; remains latched until clear threshold reached | 21.0 °C or above |
| `INVALID` | Latest received value is NaN, infinity or below absolute zero; timeout has not elapsed | Inject NaN |
| `STALE` | No valid reading for the timeout interval, including startup | Stop source |

Hysteresis prevents repeated switching around 21 °C: after entering `HIGH`, 20.75 °C stays high, while 20.5 °C clears it. Invalid readings do not refresh the last-valid receipt time. `STALE` takes precedence once that timeout expires. Valid data recovers the monitor; a value within the hysteresis band preserves the previous alarm latch.

Freshness here means **elapsed time since receipt of a numerically valid value**. It does not prove that a source generated new data. Repeated old samples, source-clock errors, sensor calibration and physical plausibility beyond absolute zero are outside this first exercise.

## Run it

From the repository root, copy the examples into the container workspace. Review any overwrite prompts if you edited a prior copy:

```bash
mkdir -p workspaces/ros/sensor-lab
cp -i examples/ros/*.py workspaces/ros/sensor-lab/
```

Terminal A:

```bash
bash scripts/ros.sh python3 /workspace/sensor-lab/temperature_monitor.py
```

Terminal B:

```bash
bash scripts/ros.sh python3 /workspace/sensor-lab/temperature_publisher.py
```

Terminal C:

```bash
bash scripts/ros.sh ros2 topic echo /lab/temperature_status
```

The status topic carries JSON in `std_msgs/msg/String`, published at a target 5 Hz. Its fields are `state`, `last_valid_temperature_c` and `seconds_since_valid`. Before any valid sample, the last two fields are JSON `null`; invalid input is never serialized as a nonstandard NaN value. This keeps the demonstration simple. A larger project should use a typed custom status message.

Observe the sine wave raise and clear `HIGH`. Stop terminal B: after about two seconds plus scheduling delay, status becomes `STALE`. Restart it and observe recovery. State transitions are also logged by the monitor.

Change thresholds at startup, using decimal values for these floating-point parameters:

```bash
bash scripts/ros.sh python3 /workspace/sensor-lab/temperature_monitor.py \
  --ros-args -p high_c:=21.5 -p clear_c:=20.8 -p stale_after_s:=3.0
```

Require `clear_c < high_c`, a positive timeout and finite values. The parameters are read-only after startup; restart the node to change them. Run one monitor per topic/domain during this exercise.

## Why the watchdog uses a separate clock

The source message has a ROS timestamp, useful for recording and later analysis. The watchdog instead measures local elapsed time with Python's monotonic clock and uses a steady-clock timer. A paused simulated `/clock` therefore does not stop the no-data check. ROS timers accept a clock selection; the implementation follows the [Jazzy rclpy node API/source](https://github.com/ros2/rclpy/blob/jazzy/rclpy/rclpy/node.py).

This is a receipt watchdog for an interactive lab. Playback pause intentionally looks like data loss. It is not a simulation-time watchdog or a hard real-time deadline mechanism. Scheduling delays can postpone the status publication.

## Repeatable checks

Run the logic tests on the host; they need only Python's standard library:

```bash
python -m unittest discover -s tests -v
```

Then run the live check in an otherwise unused local domain. Stop other exercises using domain 79 first:

```bash
ROS_DOMAIN_ID=79 bash scripts/ros.sh \
  python3 /workspace/sensor-lab/check_temperature_monitor.py
```

The check starts and stops its own monitor, publishes known inputs and verifies normal/high states, deadband behavior, invalid input, stale timeout and recovery. It enables simulated time without a `/clock` publisher to exercise the separate watchdog clock. It returns a nonzero exit on failure and cleans up its child monitor.

## Use the recorded bag as an input fixture

Stop the live publisher and automated checker. Keep one monitor and status subscriber running in the normal lab domain. Replay the bag created in the first lab:

```bash
bash scripts/ros.sh ros2 bag play /workspace/sensor-lab/run-01 --delay 2
```

Watch the monitor react to recorded values and become `STALE` after playback finishes. An older source timestamp does not make a just-received replay sample stale in this design. Whether replay enters `HIGH` depends on the portion of the waveform captured and your configured thresholds; a short bag is not guaranteed to contain both crossings. Use a 35-second recording to capture a complete 30-second cycle if needed.

## Finish the project

- [ ] Explain the distinction between source time, receive time and elapsed time.
- [ ] Run the logic and live ROS checks successfully.
- [ ] Demonstrate timeout after stopping the source, then recovery.
- [ ] Replay a saved bag with the live source stopped.
- [ ] Record thresholds, timeout, Git revision, image ID and observed results.

For the next iteration, choose one extension: reject duplicate source sequence numbers, report actual sample rate, add a typed status message, or integrate a real UART sensor. Define the expected behavior before changing the code and add a test for the failure case you care about.
