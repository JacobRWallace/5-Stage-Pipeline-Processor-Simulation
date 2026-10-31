"""Extension 6: experiment runner. Unlocks when pipeline_sim/experiments.py exists.

Convention: sweep() deep-copies each Config per run, so stateful predictors and
caches never leak between runs.
"""
import csv

import pytest

exp = pytest.importorskip("pipeline_sim.experiments", reason="extension 6 not started")

from pipeline_sim import Config, Pipeline, parse_program  # noqa: E402

PROGRAMS = {"chain": "ADD R1, R2, R3\nADD R4, R1, R5", "load": "LW R1, 0(R2)\nADD R4, R1, R5"}
CONFIGS = {"fwd": Config(forwarding=True), "nofwd": Config(forwarding=False)}
KEYS = {"program", "config", "instructions", "cycles", "stalls", "cpi"}


def test_sweep_is_cartesian():
    rows = exp.sweep(PROGRAMS, CONFIGS)
    assert len(rows) == 4
    assert {(r["program"], r["config"]) for r in rows} == {
        (p, c) for p in PROGRAMS for c in CONFIGS}
    assert all(set(r) >= KEYS for r in rows)


def test_sweep_matches_direct_run():
    rows = exp.sweep(PROGRAMS, CONFIGS)
    for r in rows:
        direct = Pipeline(parse_program(PROGRAMS[r["program"]]), CONFIGS[r["config"]]).run()
        assert r["cycles"] == direct.cycles and r["stalls"] == direct.stalls


def test_to_csv(tmp_path):
    out = tmp_path / "results.csv"
    exp.to_csv(exp.sweep(PROGRAMS, CONFIGS), out)
    with out.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 4 and set(rows[0]) >= KEYS
