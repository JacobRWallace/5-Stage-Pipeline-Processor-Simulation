"""Extension 1: control hazards + branch prediction.
Unlocks when pipeline_sim/branch.py exists.

Convention: all branches and jumps resolve in EX. A misprediction flushes the
2 younger instructions (2 bubble cycles). No predictor = predict not taken.
Predictors index by pc = instruction index, table slot = pc % entries.
TwoBit counters start at 1 (weakly not taken), saturate at 0 and 3.
"""
import pytest

branch = pytest.importorskip("pipeline_sim.branch", reason="extension 1 not started")
AlwaysNotTaken, AlwaysTaken = branch.AlwaysNotTaken, branch.AlwaysTaken
OneBit, TwoBit = branch.OneBit, branch.TwoBit

LOOP_TWICE = [True, True, True, False] * 2


def mispredicts(pred, outcomes, pc=3):
    miss = 0
    for taken in outcomes:
        miss += pred.predict(pc) != taken
        pred.update(pc, taken)
    return miss


@pytest.mark.parametrize("make, expected", [
    pytest.param(AlwaysNotTaken, 6, id="not-taken"),
    pytest.param(AlwaysTaken, 2, id="taken"),
    pytest.param(OneBit, 4, id="one-bit"),
    pytest.param(TwoBit, 3, id="two-bit"),
])
def test_predictor_on_repeated_loop(make, expected):
    assert mispredicts(make(), LOOP_TWICE) == expected


def test_two_bit_saturates():
    p = TwoBit()
    assert p.counter(0) == 1
    for _ in range(5):
        p.update(0, True)
    assert p.counter(0) == 3
    for _ in range(5):
        p.update(0, False)
    assert p.counter(0) == 0


def test_separate_pcs_and_aliasing():
    p = TwoBit(entries=4)
    for _ in range(3):
        p.update(1, True)
    assert p.predict(1) is True
    assert p.predict(2) is False, "different slot is untouched"
    assert p.predict(5) is True, "5 % 4 == 1 aliases with pc 1"


# ---------- integration: needs real register values ----------

LOOP = """
      ADDI R1, R0, 3
loop: ADDI R1, R1, -1
      BNE  R1, R0, loop
      ADD  R2, R1, R1
"""


@pytest.fixture
def functional():
    pytest.importorskip("pipeline_sim.functional", reason="needs extension 5 for values")


def test_loop_runs_correctly(sim, functional):
    r = sim(LOOP, forwarding=True, branch_predictor=AlwaysNotTaken())
    assert r.regs["R1"] == 0 and r.regs["R2"] == 0
    assert r.instructions == 8          # ADDI + 3 x (ADDI, BNE) + ADD
    assert r.flushes == 2               # two taken BNEs
    assert r.cycles == 8 + 4 + 2 * 2


def test_default_is_predict_not_taken(sim, functional):
    assert sim(LOOP).cycles == sim(LOOP, branch_predictor=AlwaysNotTaken()).cycles


def test_branch_not_taken_costs_nothing(sim, functional):
    r = sim("BEQ R1, R0, skip\nADDI R2, R0, 1\nskip: ADDI R3, R0, 1", regs={"R1": 1})
    assert (r.flushes, r.cycles, r.regs["R2"]) == (0, 7, 1)


def test_unconditional_jump(sim, functional):
    r = sim("J end\nADDI R1, R0, 1\nend: ADDI R2, R0, 2")
    assert r.regs.get("R1", 0) == 0 and r.regs["R2"] == 2
    assert (r.instructions, r.flushes, r.cycles) == (2, 1, 8)
