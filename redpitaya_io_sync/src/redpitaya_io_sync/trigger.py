from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class TrigEdge(str, Enum):
    HIGH = "high"
    LOW = "low"
    RISE = "rise"
    FALL = "fall"
    RISE_FALL = "rise_fall"


@dataclass(frozen=True)
class Trigger:
    """Represents a trigger condition for a frame."""
    edge: TrigEdge


# Convenience aliases used by your example imports
TrigHigh = Trigger(TrigEdge.HIGH)
TrigLow = Trigger(TrigEdge.LOW)
TrigRise = Trigger(TrigEdge.RISE)
TrigFall = Trigger(TrigEdge.FALL)
TrigRiseFall = Trigger(TrigEdge.RISE_FALL)
º