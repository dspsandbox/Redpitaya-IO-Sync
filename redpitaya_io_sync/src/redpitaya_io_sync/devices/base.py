from __future__ import annotations
from typing import Any, Dict, Optional

from redpitaya_io_sync.sequencer import IoSequence


class RpDeviceBase:
    def __init__(self, url: str):
        self.url = url
        self._loaded: Optional[IoSequence] = None
        self._running: bool = False

    def load(self, seq: IoSequence) -> None:
        self._loaded = seq

    def start(self) -> None:
        if self._loaded is None:
            raise RuntimeError("No sequence loaded. Call load(seq) first.")
        self._running = True

    def stop(self) -> None:
        self._running = False

    def get_status(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "loaded": self._loaded is not None,
            "running": self._running,
            "frames": 0 if self._loaded is None else len(self._loaded.frames),
        }

    def get_data(self) -> Dict[str, Any]:
        # Placeholder: later return acquired data buffers by labels, etc.
        return {"data": {}}
