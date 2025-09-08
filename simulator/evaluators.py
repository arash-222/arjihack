from __future__ import annotations

import hashlib
import math
from typing import List, Tuple

from .policy import PolicyGuard
from .generators import GeneratedArtifact


class SimilarityDiscriminator:
	def __init__(self):
		self.archive_hashes = set()

	@staticmethod
	def _hash(text: str) -> str:
		return hashlib.sha256(text.encode("utf-8")).hexdigest()

	def score(self, artifacts: List[GeneratedArtifact]) -> List[float]:
		scores: List[float] = []
		for a in artifacts:
			hv = self._hash(a.content)
			dup = 1.0 if hv in self.archive_hashes else 0.0
			scores.append(dup)
			self.archive_hashes.add(hv)
		return scores


class MockBlueToolAdapter:
	def score(self, artifacts: List[GeneratedArtifact]) -> List[float]:
		# Higher means more likely to be detected; we want to challenge by lowering this
		return [min(1.0, 0.2 + 0.8 * (len(a.content) % 50) / 50.0) for a in artifacts]


class PolicyJudge:
	def __init__(self, guard: PolicyGuard):
		self.guard = guard

	def evaluate(self, artifacts: List[GeneratedArtifact]) -> Tuple[List[bool], List[List[str]], List[str]]:
		allowed: List[bool] = []
		violations: List[List[str]] = []
		sanitized_contents: List[str] = []
		for a in artifacts:
			ok, sanitized, v = self.guard.hard_gate(a.content)
			allowed.append(ok)
			violations.append(v)
			sanitized_contents.append(sanitized)
		return allowed, violations, sanitized_contents