import unittest
import math

from check import measured_stats, summarize


class HealthSummaryTests(unittest.TestCase):
    def test_missing_measurement_stays_unknown(self):
        self.assertEqual(measured_stats([None, None]), {
            "measured_samples": 0, "min": None, "mean": None, "max": None,
        })
        self.assertEqual(measured_stats([None, 0])["measured_samples"], 1)
        self.assertEqual(measured_stats([None, 0])["mean"], 0)

    def test_non_finite_measurements_are_unknown(self):
        self.assertEqual(measured_stats([math.nan, math.inf, -math.inf]), {
            "measured_samples": 0, "min": None, "mean": None, "max": None,
        })

    def test_child_program_is_not_attributed_to_parent_app(self):
        sample = {
            "schema_version": 1, "unix_ms": 1, "gpu": None,
            "memory": {"pressure": "nominal"}, "verdict": {"kind": "normal"},
            "processes": [
                {"pid": 1, "ppid": 0, "name": "Codex", "mem_bytes": 100},
                {"pid": 2, "ppid": 1, "name": "cli.js", "mem_bytes": 200},
                {"pid": 3, "ppid": 1, "name": "restricted", "mem_bytes": None},
            ],
        }
        result = summarize([sample], {1: "/Applications/ChatGPT.app/Contents/MacOS/codex", 2: "/usr/bin/node"})
        apps = {app["name"]: app for app in result["applications"]}
        self.assertEqual(apps["ChatGPT.app"]["footprint_bytes"], 100)
        self.assertEqual(apps["cli.js"]["footprint_bytes"], 200)
        self.assertIsNone(apps["restricted"]["footprint_bytes"])
        self.assertEqual(result["metrics"]["gpu.usage"]["measured_samples"], 0)


if __name__ == "__main__":
    unittest.main()
