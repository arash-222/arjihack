from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from .scenario import ScenarioManager
from .policy import PolicyGuard
from .telemetry import TelemetryBus
from .twin import TwinExecutor
from .orchestrator import Orchestrator


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Safe Adversarial Simulator (inert)")
	parser.add_argument("--scenario", required=True, help="Path to scenario YAML")
	parser.add_argument("--episodes", type=int, default=1)
	parser.add_argument("--batch-size", type=int, default=4)
	parser.add_argument("--output", default=str(Path("/workspace/output").absolute()))
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	sm = ScenarioManager(args.scenario)
	policy = PolicyGuard(sm.scenario.constraints)
	telemetry = TelemetryBus(output_dir=args.output)
	twin = TwinExecutor(telemetry=telemetry)
	orch = Orchestrator(
		scenario_manager=sm,
		policy_guard=policy,
		telemetry=telemetry,
		twin=twin,
		batch_size=args.batch_size,
	)
	results = orch.run(episodes=args.episodes)
	Path(args.output).mkdir(parents=True, exist_ok=True)
	with open(Path(args.output) / "run_summary.json", "w", encoding="utf-8") as f:
		json.dump(results, f, indent=2)
	print(f"Completed {args.episodes} episode(s). Summary written to {args.output}.")


if __name__ == "__main__":
	main()