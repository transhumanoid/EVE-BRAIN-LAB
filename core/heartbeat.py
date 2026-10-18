"""Heartbeat: records that the journal is alive and writable.

Each tick writes last_heartbeat and increments heartbeat_count in the
metadata table. Run once, or with --interval N to tick every N seconds.
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msvm_journal as j  # noqa: E402


def tick(path=None):
    j.init_db(path)
    count = int(j.get_meta("heartbeat_count", path) or 0) + 1
    ts = j.now_iso()
    j.set_meta("last_heartbeat", ts, path)
    j.set_meta("heartbeat_count", count, path)
    return ts, count


def main():
    p = argparse.ArgumentParser(description="Journal heartbeat")
    p.add_argument("--interval", type=int, default=0,
                   help="seconds between ticks; 0 = tick once")
    args = p.parse_args()
    while True:
        ts, count = tick()
        print(f"heartbeat #{count} at {ts} -> {j.db_path()}", flush=True)
        if not args.interval:
            break
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
