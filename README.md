# Eve Brain Lab

Eve Brain Lab is a research workspace for hybrid virtual minds: emulated agents that think, remember, and coordinate, and the collective intelligence that emerges when they work together.

## Focus areas

- **Hybrid virtual minds**: architectures that combine language-model reasoning with persistent memory and structured state.
- **Emulated agents**: individual agent personas with their own roles, goals, and behaviors.
- **Collective intelligence**: coordination, shared memory, and self-improvement loops across many agents.
- **Journal, heartbeat, and watchdog systems**: the record-keeping and liveness layer. The journal records agent activity, the heartbeat signals that an agent is alive and connected, and the watchdog detects dropped connections and restores them.

## Repository layout

| Path | Purpose |
| --- | --- |
| `core/` | Core runtime: the journal engine, schema, and heartbeat/watchdog logic |
| `blueprints/` | Agent and mind blueprints: personas, roles, and configuration templates |
| `scripts/` | Utility and maintenance scripts |
| `docs/` | Design notes and documentation |
| `journals/` | Local journal data. **Gitignored** and never committed |

## Data policy

Journals, databases, secrets, and local artifacts stay on the machine that produced them and are excluded by `.gitignore`. This repository holds only code, schemas, blueprints, and documentation.
