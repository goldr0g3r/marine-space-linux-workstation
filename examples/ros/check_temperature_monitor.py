#!/usr/bin/env python3
"""Bounded integration check. Run in an otherwise unused, local ROS domain."""

import json
import math
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

import rclpy
from sensor_msgs.msg import Temperature
from std_msgs.msg import String


def main():
    monitor_path = Path(__file__).with_name("temperature_monitor.py")
    rclpy.init()
    node = rclpy.create_node("temperature_monitor_check")
    publisher = node.create_publisher(Temperature, "/lab/temperature", 10)
    observed = []

    def receive(message):
        observed.append(json.loads(message.data)["state"])

    subscription = node.create_subscription(String, "/lab/temperature_status", receive, 10)
    with tempfile.TemporaryFile(mode="w+") as log:
        child = subprocess.Popen(
            [sys.executable, str(monitor_path), "--ros-args", "-p", "stale_after_s:=0.8",
             "-p", "use_sim_time:=true"],
            stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 10.0
            while publisher.get_subscription_count() == 0:
                if child.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("Monitor did not become discoverable")
                rclpy.spin_once(node, timeout_sec=0.05)

            def expect(state, value=None):
                observed.clear()
                deadline = time.monotonic() + 4.0
                while time.monotonic() < deadline:
                    if child.poll() is not None:
                        raise RuntimeError("Monitor exited unexpectedly")
                    if value is not None:
                        message = Temperature()
                        message.header.stamp = node.get_clock().now().to_msg()
                        message.header.frame_id = "test_sensor"
                        message.temperature = value
                        publisher.publish(message)
                    rclpy.spin_once(node, timeout_sec=0.05)
                    if state in observed:
                        print(f"PASS: {state} with input {value}", flush=True)
                        return
                raise AssertionError(f"Expected {state}; observed {observed}")

            expect("NORMAL", 20.0)
            expect("HIGH", 22.0)
            # Consume status while publishing a deadband value for a full second.
            observed.clear()
            deadline = time.monotonic() + 1.0
            while time.monotonic() < deadline:
                message = Temperature(temperature=20.75)
                publisher.publish(message)
                rclpy.spin_once(node, timeout_sec=0.05)
            assert observed and all(state == "HIGH" for state in observed), observed
            print("PASS: HIGH persists within hysteresis band", flush=True)
            expect("NORMAL", 20.0)
            expect("INVALID", math.nan)
            expect("NORMAL", 20.0)
            expect("STALE")
            expect("NORMAL", 20.0)
            print("PASS: live ROS checks, including timeout with no simulated clock", flush=True)
        except BaseException:
            log.flush()
            log.seek(0)
            print(log.read(), file=sys.stderr)
            raise
        finally:
            if child.poll() is None:
                child.send_signal(signal.SIGINT)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            node.destroy_subscription(subscription)
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()
