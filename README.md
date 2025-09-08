# Adversarial GAN Attack Simulator (Safe, Offline, Inert)

Purpose: safe, air-gapped, inert simulator for lawful defensive testing. Outputs are sanitized placeholders and replayable traces only; no live exploits or external connectivity.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m simulator.main --scenario /workspace/configs/examples/phishing.yaml --episodes 1 --batch-size 4
```

## Safety
- Air-gapped by design; no HTTP/DNS clients are used
- Placeholders only for secrets/PII; inert code stubs link to mock APIs
- Watermarked artifacts and manifest logs (stubbed in v0.1)

## Legal Notice
For authorized defensive testing in isolated labs only. Do not use against real systems or to generate harmful content.
