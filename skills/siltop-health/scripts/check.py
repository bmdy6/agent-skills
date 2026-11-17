#!/usr/bin/env python3
"""Read siltop snapshots and summarize measured values without changing the host."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import statistics
import subprocess


def measured_stats(values):
    measured = [
        v for v in values
        if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
    ]
    return {
        "measured_samples": len(measured),
        "min": min(measured) if measured else None,
        "mean": statistics.mean(measured) if measured else None,
        "max": max(measured) if measured else None,
    }


def app_name(process, paths):
    path = paths.get(process["pid"], "")
    bundle = re.search(r"/Applications/([^/]+\.app)(?:/|$)", path)
    return bundle.group(1) if bundle else process["name"]


def summarize(snapshots, paths):
    if not snapshots:
        raise ValueError("No complete siltop samples")
    if any(s.get("schema_version") != 1 for s in snapshots):
        raise ValueError("Unsupported siltop schema; check its JSON contract")
    last = snapshots[-1]
    metrics = {}
    for section, field in [
        ("cpu", "usage"), ("gpu", "usage"), ("temp", "cpu_temp_avg"),
        ("memory", "ram_usage"), ("memory", "swap_usage"),
        ("memory", "swap_in_bps"), ("memory", "swap_out_bps"),
    ]:
        metrics[f"{section}.{field}"] = measured_stats(
            [(s.get(section) or {}).get(field) for s in snapshots]
        )
    metrics["sys_power"] = measured_stats([s.get("sys_power") for s in snapshots])
    groups = defaultdict(lambda: {"process_count": 0, "footprint_bytes": 0, "measured_processes": 0})
    for process in last["processes"]:
        group = groups[app_name(process, paths)]
        group["process_count"] += 1
        if process.get("mem_bytes") is not None:
            group["footprint_bytes"] += process["mem_bytes"]
            group["measured_processes"] += 1
    for group in groups.values():
        if group["measured_processes"] == 0:
            group["footprint_bytes"] = None
    ranked = sorted(groups.items(), key=lambda item: item[1]["footprint_bytes"] or 0, reverse=True)
    return {
        "sample_count": len(snapshots),
        "first_unix_ms": snapshots[0]["unix_ms"],
        "last_unix_ms": last["unix_ms"],
        "memory_pressure": dict(Counter(s["memory"].get("pressure", "unknown") for s in snapshots)),
        "thermal_pressure": dict(Counter(s.get("thermal_pressure", "unknown") for s in snapshots)),
        "verdicts": dict(Counter(s["verdict"]["kind"] for s in snapshots)),
        "metrics": metrics,
        "last_health": last.get("health", {}),
        "last_memory": last["memory"],
        "processes_returned": len(last["processes"]),
        "process_limit_may_be_reached": len(last["processes"]) >= 1500,
        "application_attribution": "live executable paths" if paths else "process names only",
        "applications": [{"name": name, **group} for name, group in ranked[:15]],
        "top_processes": sorted(last["processes"], key=lambda p: p.get("mem_bytes") or 0, reverse=True)[:12],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=20)
    parser.add_argument("--input", type=Path, help="Replay existing NDJSON without consulting current processes")
    args = parser.parse_args()
    if not 1 <= args.samples <= 60:
        parser.error("--samples must be between 1 and 60")
    paths = {}
    if args.input:
        raw = args.input.read_text()
    else:
        raw = subprocess.run(
            ["siltop", "--json-stream", "--count", str(args.samples), "-i", "1s", "--procs", "1500"],
            text=True, capture_output=True, check=True, timeout=args.samples + 30,
        ).stdout
        output = subprocess.run(
            ["ps", "-axo", "pid=,comm="], text=True, capture_output=True, check=True, timeout=10,
        ).stdout
        for line in output.splitlines():
            fields = line.strip().split(None, 1)
            if len(fields) == 2:
                paths[int(fields[0])] = fields[1]
    result = summarize([json.loads(line) for line in raw.splitlines() if line.strip()], paths)
    result["reported_at"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
