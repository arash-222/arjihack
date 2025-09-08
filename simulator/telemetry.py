from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List


class TelemetryBus:
	def __init__(self, output_dir: str):
		self.output_dir = Path(output_dir)
		self.output_dir.mkdir(parents=True, exist_ok=True)
		self.events: List[Dict[str, Any]] = []

	def log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
		event = {"type": event_type, **payload}
		self.events.append(event)
		with open(self.output_dir / "telemetry.jsonl", "a", encoding="utf-8") as f:
			f.write(json.dumps(event) + "\n")

	def summary(self) -> Dict[str, Any]:
		return {
			"events": len(self.events),
			"by_type": self._by_type(),
		}

	def _by_type(self) -> Dict[str, int]:
		counts: Dict[str, int] = {}
		for e in self.events:
			counts[e["type"]] = counts.get(e["type"], 0) + 1
		return counts