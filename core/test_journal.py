"""Round-trip test: write, read, heartbeat, watchdog recovery.

Uses a temporary database so the real journal is never touched.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msvm_journal as j  # noqa: E402
import heartbeat  # noqa: E402
import watchdog  # noqa: E402


def main():
    tmp = tempfile.mkdtemp(prefix="eve_journal_test_")
    path = os.path.join(tmp, "test_journal.db")
    os.environ["EVE_JOURNAL_DB"] = path

    eid = j.add_entry("test", "round-trip check", ["test"])
    got = j.get_entry(eid)
    assert got and got["content"] == "round-trip check", got
    print(f"PASS write/read: entry {eid} read back")

    ts, count = heartbeat.tick()
    assert j.get_meta("last_heartbeat") == ts and count == 1
    print(f"PASS heartbeat: tick #{count} at {ts}")

    s = watchdog.check()
    assert s["ok"] and not s["recreated"] and s["heartbeat_stale"] is False, s
    print("PASS watchdog: healthy database left alone")

    os.remove(path)
    assert not os.path.exists(path)
    s = watchdog.check()
    assert s["ok"] and s["recreated"] and os.path.exists(path), s
    assert j.get_entries(topic="watchdog"), "recovery entry missing"
    print("PASS watchdog: missing database detected and recreated")

    os.remove(path)
    os.rmdir(tmp)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
