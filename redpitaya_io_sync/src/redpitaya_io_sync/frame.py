from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple




class AnalogOut(_CommandSink):
    def frequency(self, t, val, update=True): self._emit(t, "frequency", val, update)
    def phase(self, t, val, update=True): self._emit(t, "phase", val, update)
    def amplitude(self, t, val, update=True): self._emit(t, "amplitude", val, update)
    def reset_phase(self, t, val=True, update=True): self._emit(t, "reset_phase", val, update)


class AnalogIn(_CommandSink):
    def frequency(self, t, val, update=True): self._emit(t, "frequency", val, update)
    def phase(self, t, val, update=True): self._emit(t, "phase", val, update)
    def amplitude(self, t, val, update=True): self._emit(t, "amplitude", val, update)
    def reset_phase(self, t, val=True, update=True): self._emit(t, "reset_phase", val, update)
    def acquire(self, t, samples, dec=1, label: str | None = None): self._emit(t, "acquire", samples, dec, label=label)


class PWM(_CommandSink):
    def duty_cycle(self, t, mask, val): self._emit(t, "duty_cycle", mask, val)


class XADC(_CommandSink):
    def acquire(self, t, samples, dec=1, label: str | None = None): self._emit(t, "acquire", samples, dec, label=label)


class Digital(_CommandSink):
    def output(self, t, mask, val): self._emit(t, "output", mask, val)
    def tristate(self, t, mask, val): self._emit(t, "tristate", mask, val)
    def acquire(self, t, samples, dec=1, label: str | None = None): self._emit(t, "acquire", samples, dec, label=label)


class Monitor(_CommandSink):
    def source(self, t, val): self._emit(t, "source", val)
    def acquire(self, t, samples, dec=1, label: str | None = None): self._emit(t, "acquire", samples, dec, label=label)


# --- Frame and sequence --------------------------------------------------------

class IoSyncFrame:
    """
    Collects time-tagged commands for one 'frame' (optionally with trigger).
    """
    def __init__(self, trig=None):
        self.trig = trig
        self._commands: List[Command] = []

        # Expose the exact attributes used in your example
        self.analog_out_1 = AnalogOut(self, "analog_out_1")
        self.analog_out_2 = AnalogOut(self, "analog_out_2")

        self.analog_in_1 = AnalogIn(self, "analog_in_1")
        self.analog_in_2 = AnalogIn(self, "analog_in_2")

        self.pwm = PWM(self, "pwm")
        self.xadc = XADC(self, "xadc")
        self.digital = Digital(self, "digital")
        self.monitor = Monitor(self, "monitor")

    def reset(self) -> None:
        self._commands.clear()

    @property
    def commands(self) -> List[Command]:
        return list(self._commands)


class IoSequence:
    """
    A labeled list of frames.
    """
    def __init__(self):
        self._frames: List[Tuple[Optional[str], IoSyncFrame]] = []

    def reset(self) -> None:
        self._frames.clear()

    def append(self, frame: IoSyncFrame, label: str | None = None) -> None:
        self._frames.append((label, frame))

    def replace(self, label: str, frame: IoSyncFrame) -> None:
        for i, (lbl, _) in enumerate(self._frames):
            if lbl == label:
                self._frames[i] = (label, frame)
                return
        raise KeyError(f"label not found: {label!r}")

    @property
    def frames(self) -> List[Tuple[Optional[str], IoSyncFrame]]:
        return list(self._frames)
