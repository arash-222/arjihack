from __future__ import annotations

import time
from typing import List

from .generators import GeneratedArtifact
from .telemetry import TelemetryBus


class TwinExecutor:
	def __init__(self, telemetry: TelemetryBus):
		self.telemetry = telemetry

	def run_batch(self, artifacts: List[GeneratedArtifact]) -> None:
		for a in artifacts:
			start = time.time()
			# simulate execution latency only
			time.sleep(0.01)
			self.telemetry.log_event(
				event_type="execution",
				payload={"kind": a.kind, "duration_ms": int(1000 * (time.time() - start))},
			)