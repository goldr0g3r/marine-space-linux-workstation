"""Small, ROS-independent state machine for a temperature-monitoring lesson."""

import math


class TemperatureMonitorLogic:
    def __init__(self, *, started_at, high_c=21.0, clear_c=20.5, stale_after_s=2.0):
        if not all(math.isfinite(v) for v in (high_c, clear_c, stale_after_s)):
            raise ValueError("Thresholds and timeout must be finite")
        if clear_c >= high_c or stale_after_s <= 0:
            raise ValueError("Require clear_c < high_c and stale_after_s > 0")
        self.started_at = started_at
        self.high_c = high_c
        self.clear_c = clear_c
        self.stale_after_s = stale_after_s
        self.last_valid_at = None
        self.last_valid_temperature_c = None
        self.high = False
        self.invalid = False

    def observe(self, temperature_c, now):
        # Invalid packets must not keep an otherwise dead sensor 'fresh'.
        if not math.isfinite(temperature_c) or temperature_c < -273.15:
            self.invalid = True
            return
        self.invalid = False
        self.last_valid_at = now
        self.last_valid_temperature_c = temperature_c
        if temperature_c >= self.high_c:
            self.high = True
        elif temperature_c <= self.clear_c:
            self.high = False

    def snapshot(self, now):
        last = self.started_at if self.last_valid_at is None else self.last_valid_at
        if now - last >= self.stale_after_s:
            state = "STALE"
        elif self.invalid:
            state = "INVALID"
        elif self.last_valid_at is None:
            state = "WAITING"
        else:
            state = "HIGH" if self.high else "NORMAL"
        return {
            "state": state,
            "last_valid_temperature_c": self.last_valid_temperature_c,
            "seconds_since_valid": (
                None if self.last_valid_at is None else now - self.last_valid_at
            ),
        }
