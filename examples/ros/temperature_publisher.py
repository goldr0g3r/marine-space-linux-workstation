#!/usr/bin/env python3
"""Publish synthetic temperature readings at 10 Hz; no hardware required."""

import math
import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import Temperature


class TemperaturePublisher(Node):
    def __init__(self):
        super().__init__("synthetic_temperature")
        self.started_at = time.monotonic()
        self.publisher = self.create_publisher(Temperature, "/lab/temperature", 10)
        self.timer = self.create_timer(0.1, self.publish_reading)
        self.get_logger().info("Synthetic temperature: /lab/temperature, degrees Celsius, 10 Hz")

    def publish_reading(self):
        elapsed = time.monotonic() - self.started_at
        reading = Temperature()
        reading.header.stamp = self.get_clock().now().to_msg()
        reading.header.frame_id = "synthetic_temperature_sensor"
        reading.temperature = 20.0 + 2.0 * math.sin(2.0 * math.pi * elapsed / 30.0)
        reading.variance = 0.0  # Unknown/unspecified, not a calibrated sensor estimate.
        self.publisher.publish(reading)


def main():
    rclpy.init()
    node = TemperaturePublisher()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
