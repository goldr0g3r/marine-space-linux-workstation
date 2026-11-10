"""Timing/threshold contracts, tested without ROS or real sleeps."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples" / "ros"))
from temperature_monitor_logic import TemperatureMonitorLogic


class TemperatureMonitorTests(unittest.TestCase):
    def setUp(self):
        self.monitor = TemperatureMonitorLogic(started_at=0.0)

    def state(self, now):
        return self.monitor.snapshot(now)["state"]

    def test_no_sensor_transitions_from_waiting_to_stale(self):
        self.assertEqual(self.state(0.0), "WAITING")
        self.assertEqual(self.state(1.99), "WAITING")
        self.assertEqual(self.state(2.0), "STALE")

    def test_threshold_boundaries_and_hysteresis(self):
        for value, state in [(20.0, "NORMAL"), (21.0, "HIGH"),
                             (20.75, "HIGH"), (20.5, "NORMAL"), (20.75, "NORMAL")]:
            with self.subTest(value=value, expected=state):
                self.monitor.observe(value, 1.0)
                self.assertEqual(self.state(1.0), state)

    def test_stale_boundary_and_recovery(self):
        self.monitor.observe(22.0, 1.0)
        self.assertEqual(self.state(2.99), "HIGH")
        self.assertEqual(self.state(3.0), "STALE")
        self.monitor.observe(20.0, 4.0)
        self.assertEqual(self.state(4.0), "NORMAL")

    def test_invalid_data_does_not_refresh_freshness(self):
        for value in (math.nan, math.inf, -math.inf, -274.0):
            with self.subTest(value=value):
                self.monitor.observe(20.0, 1.0)
                self.monitor.observe(value, 2.5)
                self.assertEqual(self.state(2.5), "INVALID")
                self.assertEqual(self.state(3.0), "STALE")
                self.assertEqual(self.monitor.snapshot(3.0)["last_valid_temperature_c"], 20.0)

    def test_valid_data_recovers_after_invalid(self):
        self.monitor.observe(math.nan, 0.5)
        self.assertEqual(self.state(0.5), "INVALID")
        self.monitor.observe(20.0, 1.0)
        self.assertEqual(self.state(1.0), "NORMAL")

    def test_unknown_values_are_null_before_first_sample(self):
        status = self.monitor.snapshot(0.0)
        self.assertIsNone(status["last_valid_temperature_c"])
        self.assertIsNone(status["seconds_since_valid"])

    def test_recovery_in_deadband_preserves_high_latch(self):
        self.monitor.observe(22.0, 0.0)
        self.assertEqual(self.state(2.0), "STALE")
        self.monitor.observe(20.75, 3.0)
        self.assertEqual(self.state(3.0), "HIGH")

    def test_configuration_rejects_bad_thresholds_and_timeout(self):
        for config in ({"high_c": math.nan}, {"clear_c": math.inf},
                       {"clear_c": 21.0}, {"stale_after_s": 0.0},
                       {"stale_after_s": -1.0}, {"stale_after_s": math.inf}):
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    TemperatureMonitorLogic(started_at=0.0, **config)


if __name__ == "__main__":
    unittest.main()
