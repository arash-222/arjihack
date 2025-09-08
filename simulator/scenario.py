from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

try:
	import yaml  # type: ignore
except Exception:  # minimal fallback: extremely limited YAML subset
	class _MiniYAML:
		@staticmethod
		def safe_load(text: str):
			import json as _json
			try:
				return _json.loads(text)
			except Exception as _:
				raise RuntimeError("PyYAML not available and fallback cannot parse YAML. Install pyyaml.")
		safe_load = staticmethod(safe_load)
	yaml = _MiniYAML()  # type: ignore


@dataclass
class Scenario:
	id: str
	name: str
	tactics: List[str]
	style_tokens: Dict[str, str]
	constraints: Dict[str, bool]
	kpis: Dict[str, float]
	environment: Dict[str, str]


class ScenarioManager:
	def __init__(self, path: str):
		self.path = path
		with open(path, "r", encoding="utf-8") as f:
			content = f.read()
			# Normalize tabs for YAML parsing without altering file on disk
			if "\t" in content:
				content = content.replace("\t", "  ")
			self.config = yaml.safe_load(content)
		self._validate()

	def _validate(self) -> None:
		required = ["id", "name", "tactics", "constraints"]
		for key in required:
			if key not in self.config:
				raise ValueError(f"Scenario missing required field: {key}")
		constraints = self.config.setdefault("constraints", {})
		constraints.setdefault("no_live_exploit", True)
		constraints.setdefault("no_credentials", True)
		constraints.setdefault("no_outbound_dns", True)
		constraints.setdefault("no_external_urls", True)

	def sample_condition(self) -> Dict[str, str]:
		style = self.config.get("style_tokens", {})
		return {**style, "scenario_id": self.config.get("id", "unknown")}

	@property
	def scenario(self) -> Scenario:
		return Scenario(
			id=self.config["id"],
			name=self.config["name"],
			tactics=list(self.config.get("tactics", [])),
			style_tokens=dict(self.config.get("style_tokens", {})),
			constraints=dict(self.config.get("constraints", {})),
			kpis=dict(self.config.get("kpis", {})),
			environment=dict(self.config.get("environment", {})),
		)