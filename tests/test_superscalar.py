"""Extension 3b (fallback for 3a): in-order dual issue.
Unlocks when pipeline_sim/superscalar.py exists.

Convention: Config(issue_width=2). Fetches up to 2 per cycle; a dependent
pair cannot issue together.
"""
import pytest

pytest.importorskip("pipeline_sim.superscalar", reason="extension 3b not started")

from test_core import PROGRAMS  # noqa: E402


def test_independent_pairs_dual_issue(sim):
    src = "\n".join(f"ADD R{i + 1}, R20, R21" for i in range(10))
    r = sim(src, issue_width=2)
    assert r.cycles == 9
    assert r.cpi < 1


def test_dependent_pair_not_coissued(sim):
    r = sim("ADD R1, R2, R3\nADD R4, R1, R5", issue_width=2)
    assert r.timeline[1]["EX"] > r.timeline[0]["EX"]


@pytest.mark.parametrize("src", PROGRAMS, ids=["no-hazards", "data", "load-use"])
def test_width_one_matches_core(sim, src):
    a, b = sim(src, issue_width=1), sim(src)
    assert (a.cycles, a.stalls) == (b.cycles, b.stalls)
