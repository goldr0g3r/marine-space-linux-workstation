#!/usr/bin/env python3
"""Monitor the learning topic; publish JSON status without commanding hardware."""

import json
import time

import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.clock import Clock, ClockType
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Temperature
from std_msgs.msg import String

from temperature_monitor_logic import TemperatureMonitorLogic


class TemperatureMonitor(Node):
    def __init__(self):
        super().__init__("temperature_monitor")
        self.declare_parameter("high_c", 21.0, ParameterDescriptor(read_only=True))
        self.declare_parameter("clear_c", 20.5, ParameterDescriptor(read_only=True))
        self.declare_parameter("stale_after_s", 2.0, ParameterDescriptor(read_only=True))
        self.logic = TemperatureMonitorLogic(
            started_at=time.monotonic(),
            high_c=self.get_parameter("high_c").value,
            clear_c=self.get_parameter("clear_c").value,
            stale_after_s=self.get_parameter("stale_after_s").value,
        )
        self.subscription = self.create_subscription(
            Temperature, "/lab/temperature", self.receive, 10
        )
        self.publisher = self.create_publisher(String, "/lab/temperature_status", 10)
        self.previous_state = None
        # Keep the watchdog running even if a simulated ROS clock is paused.
        self.watchdog_clock = Clock(clock_type=ClockType.STEADY_TIME)
        self.timer = self.create_timer(0.2, self.publish_status, clock=self.watchdog_clock)

    def receive(self, message):
        self.logic.observe(message.temperature, time.monotonic())

    def publish_status(self):
        status = self.logic.snapshot(time.monotonic())
        self.publisher.publish(String(data=json.dumps(status, allow_nan=False)))
        if status["state"] != self.previous_state:
            self.get_logger().info(f"Temperature state: {status['state']}")
            self.previous_state = status["state"]


def main():
    rclpy.init()
    node = None
    try:
        node = TemperatureMonitor()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
