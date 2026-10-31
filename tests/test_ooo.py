"""Extension 3a: out-of-order (Tomasulo + ROB). Unlocks when pipeline_sim/ooo.py exists.
Needs extension 5 so results can be checked.

Convention: Config(out_of_order=True). Timeline entries gain a "COMMIT" key.
Commit is in program order, one per cycle.
"""
import pytest

pytest.importorskip("pipeline_sim.ooo", reason="extension 3a not started")
pytest.importorskip("pipeline_sim.functional", reason="needs extension 5 for values")

MIXED = """
LW  R1, 0(R2)
ADD R3, R1, R4
MUL R5, R3, R3
ADD R6, R7, R8
SUB R9, R6, R4
SW  R5, 8(R2)
"""
REGS = {"R2": 32, "R4": 3, "R7": 10, "R8": 20}
MEM = {32: 4}


@pytest.mark.parametrize("src", [MIXED, "LW R1, 0(R2)\nADD R3, R1, R1\nADD R5, R4, R4"])
def test_same_results_as_in_order(sim, src):
    kw = dict(regs=REGS, mem=MEM, latencies={"MUL": 4})
    ino, ooo = sim(src, **kw), sim(src, out_of_order=True, **kw)
    assert ooo.regs == ino.regs and ooo.mem == ino.mem


def test_independent_work_passes_stalled_instruction(sim):
    r = sim("LW R1, 0(R2)\nADD R3, R1, R4\nADD R5, R6, R7",
            out_of_order=True, regs=REGS, mem=MEM)
    assert r.timeline[2]["EX"] < r.timeline[1]["EX"]


def test_commits_in_program_order(sim):
    r = sim(MIXED, out_of_order=True, regs=REGS, mem=MEM, latencies={"MUL": 4})
    commits = [t["COMMIT"] for t in r.timeline]
    assert all(a < b for a, b in zip(commits, commits[1:]))


def test_renaming_handles_war_and_waw(sim):
    r = sim("MUL R1, R2, R3\nADD R2, R4, R5\nADD R1, R4, R4",
            out_of_order=True, latencies={"MUL": 6}, regs={"R2": 2, "R3": 3, "R4": 1, "R5": 5})
    assert r.regs["R1"] == 2, "WAW: the later ADD must win"
    assert r.regs["R2"] == 6, "WAR: MUL must have read the old R2"


def test_beats_in_order_on_long_latency(sim):
    src = "MUL R1, R2, R3\nADD R4, R1, R1\n" + "\n".join(f"ADD R{10 + i}, R2, R3" for i in range(6))
    kw = dict(latencies={"MUL": 6}, regs={"R2": 2, "R3": 3})
    assert sim(src, out_of_order=True, **kw).cycles < sim(src, **kw).cycles
