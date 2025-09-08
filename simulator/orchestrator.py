from __future__ import annotations

from typing import Dict, Any, List

from .scenario import ScenarioManager
from .policy import PolicyGuard
from .generators import TextContentGenerator, TrafficGenerator, ProgramStubGenerator, GeneratedArtifact, ObfuscationStylizer
from .evaluators import SimilarityDiscriminator, MockBlueToolAdapter, PolicyJudge
from .telemetry import TelemetryBus
from .twin import TwinExecutor


class Orchestrator:
	def __init__(
		self,
		scenario_manager: ScenarioManager,
		policy_guard: PolicyGuard,
		telemetry: TelemetryBus,
		twin: TwinExecutor,
		batch_size: int = 4,
	):
		self.scenario_manager = scenario_manager
		self.policy_guard = policy_guard
		self.telemetry = telemetry
		self.twin = twin
		self.batch_size = batch_size
		self.text_gen = TextContentGenerator(seed=42)
		self.traffic_gen = TrafficGenerator(seed=42)
		self.stub_gen = ProgramStubGenerator()
		self.stylizer = ObfuscationStylizer()
		self.sim_disc = SimilarityDiscriminator()
		self.blue = MockBlueToolAdapter()
		self.policy_judge = PolicyJudge(policy_guard)

	def run(self, episodes: int = 1) -> Dict[str, Any]:
		archive: List[Dict[str, Any]] = []
		for ep in range(episodes):
			cond = self.scenario_manager.sample_condition()
			batch = self._generate_batch(cond)
			allowed, violations, sanitized = self.policy_judge.evaluate(batch)
			for i, a in enumerate(batch):
				batch[i] = GeneratedArtifact(kind=a.kind, content=sanitized[i], metadata=a.metadata)
			self.twin.run_batch(batch)
			detect_scores = self.blue.score(batch)
			sim_scores = self.sim_disc.score(batch)
			for i, a in enumerate(batch):
				archive.append({
					"kind": a.kind,
					"detect": detect_scores[i],
					"similarity": sim_scores[i],
					"violations": violations[i],
				})
		return {"telemetry": self.telemetry.summary(), "archive_len": len(archive)}

	def _generate_batch(self, condition: Dict[str, str]) -> List[GeneratedArtifact]:
		texts = self.text_gen.generate_batch(self.batch_size, condition)
		texts = [GeneratedArtifact(kind=t.kind, content=self.stylizer.stylize(t.content, condition), metadata=t.metadata) for t in texts]
		traffic = self.traffic_gen.generate_batch(self.batch_size, condition)
		stubs = self.stub_gen.generate_batch(self.batch_size, condition)
		return texts + traffic + stubs