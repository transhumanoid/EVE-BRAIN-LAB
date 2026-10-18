"""Watchdog: makes sure the journal database exists and is healthy.

If the file is missing or its tables are gone, it recreates the schema
(never deletes existing data) and logs the recovery in the journal.
It also reports when the heartbeat has gone stale.
Run once, or with --interval N to check every N seconds.
"""
import argparse
import os
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msvm_journal as j  # noqa: E402


def check(path=None, stale_after=600):
    path = path or j.db_path()
    status = {"path": path, "recreated": False, "heartbeat_stale": None}
    if not j.schema_ok(path):
        existed = os.path.exists(path)
        j.init_db(path)
        status["recreated"] = True
        j.add_entry(
            "watchdog",
            f"Journal database {'repaired' if existed else 'missing'}; schema recreated at {path}.",
            ["watchdog", "recovery"],
            path=path,
        )
        j.set_meta("watchdog_last_recovery", j.now_iso(), path)
    last = j.get_meta("last_heartbeat", path)
    if last:
        age = (datetime.now(timezone.utc) - datetime.fromisoformat(last)).total_seconds()
        status["heartbeat_stale"] = age > stale_after
        status["heartbeat_age_s"] = int(age)
    j.set_meta("watchdog_last_check", j.now_iso(), path)
    status["ok"] = j.schema_ok(path)
    return status


def main():
    p = argparse.ArgumentParser(description="Journal watchdog")
    p.add_argument("--interval", type=int, default=0,
                   help="seconds between checks; 0 = check once")
    p.add_argument("--stale-after", type=int, default=600)
    args = p.parse_args()
    while True:
        print(check(stale_after=args.stale_after), flush=True)
        if not args.interval:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
