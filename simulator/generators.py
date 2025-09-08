from __future__ import annotations

import random
import string
from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class GeneratedArtifact:
	kind: str
	content: str
	metadata: Dict[str, Any]


class TextContentGenerator:
	def __init__(self, seed: int = 0):
		random.seed(seed)

	def generate_batch(self, batch_size: int, condition: Dict[str, str]) -> List[GeneratedArtifact]:
		artifacts: List[GeneratedArtifact] = []
		style = condition.copy()
		for i in range(batch_size):
			length = int(style.get("length", 120))
			topic = style.get("topic", "benign-notification")
			head = f"Subject: {topic} placeholder update"
			body = " ".join(self._safe_token() for _ in range(max(10, length // 6)))
			content = f"{head}\n\n{body}\n\nAccount: [[REDACTED]]"
			artifacts.append(GeneratedArtifact(kind="text", content=content, metadata={"i": i, **style}))
		return artifacts

	def _safe_token(self) -> str:
		letters = string.ascii_lowercase
		return "".join(random.choice(letters) for _ in range(random.randint(3, 10)))


class TrafficGenerator:
	def __init__(self, seed: int = 0):
		random.seed(seed)

	def generate_batch(self, batch_size: int, condition: Dict[str, str]) -> List[GeneratedArtifact]:
		intensity = int(condition.get("traffic_intensity", 5))
		artifacts: List[GeneratedArtifact] = []
		for i in range(batch_size):
			flows = []
			for j in range(intensity):
				flows.append({
					"src": "hostA",
					"dst": "hostB",
					"duration_ms": random.randint(20, 400),
					"bytes": random.randint(200, 4000),
					"direction": random.choice(["A2B", "B2A"]),
				})
			content = {"flows": flows}
			artifacts.append(GeneratedArtifact(kind="traffic", content=str(content), metadata={"i": i}))
		return artifacts


class ProgramStubGenerator:
	def generate_batch(self, batch_size: int, condition: Dict[str, str]) -> List[GeneratedArtifact]:
		artifacts: List[GeneratedArtifact] = []
		for i in range(batch_size):
			stub = (
				"def run():\n"
				"\t# inert stub: logs to sandbox only\n"
				"\treturn 'noop'\n"
			)
			artifacts.append(GeneratedArtifact(kind="program_stub", content=stub, metadata={"i": i}))
		return artifacts


class ObfuscationStylizer:
	def stylize(self, text: str, style: Dict[str, str]) -> str:
		spacing = style.get("spacing", "normal")
		if spacing == "wide":
			return text.replace(" ", "  ")
		return text