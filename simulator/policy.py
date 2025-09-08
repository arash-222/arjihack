from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

PLACEHOLDER = "[[REDACTED]]"


@dataclass
class PolicyConfig:
	no_live_exploit: bool = True
	no_credentials: bool = True
	no_outbound_dns: bool = True
	no_external_urls: bool = True


class PolicyGuard:
	def __init__(self, constraints: Dict[str, bool]):
		self.cfg = PolicyConfig(
			no_live_exploit=constraints.get("no_live_exploit", True),
			no_credentials=constraints.get("no_credentials", True),
			no_outbound_dns=constraints.get("no_outbound_dns", True),
			no_external_urls=constraints.get("no_external_urls", True),
		)
		self.credential_regex = re.compile(r"(?i)(password|passwd|apikey|token|secret|ssn)")
		self.url_regex = re.compile(r"(?i)\bhttps?://[\w\.-]+\b")
		self.dns_regex = re.compile(r"(?i)\b([a-z0-9-]+\.)+[a-z]{2,}\b")
		self.suspect_syscall_regex = re.compile(r"(?i)\b(exec|socket|connect|ptrace|mount|insmod|modprobe)\b")

	def sanitize_text(self, text: str) -> Tuple[str, List[str]]:
		violations: List[str] = []
		if self.cfg.no_credentials and self.credential_regex.search(text):
			text = self.credential_regex.sub(PLACEHOLDER, text)
			violations.append("credentials")
		if self.cfg.no_external_urls and self.url_regex.search(text):
			text = self.url_regex.sub("http://safe.local/" + PLACEHOLDER, text)
			violations.append("urls")
		if self.cfg.no_outbound_dns and self.dns_regex.search(text):
			text = self.dns_regex.sub("safe.local", text)
			violations.append("dns")
		if self.suspect_syscall_regex.search(text):
			text = self.suspect_syscall_regex.sub("noop", text)
			violations.append("syscalls")
		text = self._watermark(text)
		return text, violations

	def _watermark(self, text: str) -> str:
		return f"{text}\n\n[WATERMARK: SAFE_SIMULATOR_ARTIFACT]"

	def hard_gate(self, content: str) -> Tuple[bool, str, List[str]]:
		sanitized, violations = self.sanitize_text(content)
		allowed = True
		if self.cfg.no_live_exploit and "exploit" in content.lower():
			violations.append("live_exploit_phrase")
		return allowed, sanitized, violations