# core

Core runtime for the Eve Brain Lab journal.

| File | Purpose |
| --- | --- |
| `msvm_journal.py` | SQLite journal: `entries` (id, timestamp, topic, content, tags) and `metadata` tables |
| `heartbeat.py` | Records `last_heartbeat` and `heartbeat_count` in metadata |
| `watchdog.py` | Recreates a missing or broken database and flags a stale heartbeat |
| `test_journal.py` | Round-trip test on a temporary database |

All scripts read the database path from `EVE_JOURNAL_DB`, defaulting to `./journals/msvm_journal.db`. The `journals/` folder is gitignored.

```bash
python3 core/msvm_journal.py add "topic" "content" --tags "a,b"
python3 core/msvm_journal.py list
python3 core/heartbeat.py --interval 60
python3 core/watchdog.py --interval 300
python3 core/test_journal.py
```
