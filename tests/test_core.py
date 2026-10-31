"""Core in-order pipeline. Owner: core lead. Must be green before any extension merges.

Timing convention (classic 5-stage MIPS):
- Register file writes in the first half of WB and reads in the second half of ID.
- Forwarding paths: EX/MEM -> EX and MEM/WB -> EX. There is NO MEM -> MEM path.
- Hazards are detected in ID; one stall = one bubble cycle.
- Total cycles = instructions + 4 + stalls (single issue, no branches, no caches).
"""
import pytest

from pipeline_sim import parse_program

NO_HAZARDS = """
LW  R1, 0(R2)
ADD R3, R4, R5
SUB R6, R7, R8
AND R9, R10, R11
SW  R12, 4(R2)
"""

DATA_HAZARDS = """
LW  R1, 0(R2)
ADD R3, R1, R4
SUB R5, R3, R6
AND R7, R5, R8
SW  R7, 4(R2)
"""

LOAD_USE = """
LW  R1, 0(R2)
ADD R3, R1, R4
ADD R5, R3, R6
SUB R7, R5, R8
SW  R7, 8(R2)
ADD R9, R1, R10
"""

PROGRAMS = [NO_HAZARDS, DATA_HAZARDS, LOAD_USE]


# ---------- the original project's three programs, with textbook numbers ----------

@pytest.mark.parametrize("src, fwd, cycles, stalls", [
    pytest.param(NO_HAZARDS, False, 9, 0, id="no-hazards-off"),
    pytest.param(NO_HAZARDS, True, 9, 0, id="no-hazards-on"),
    pytest.param(DATA_HAZARDS, False, 17, 8, id="data-off"),
    pytest.param(DATA_HAZARDS, True, 10, 1, id="data-on"),
    pytest.param(LOAD_USE, False, 18, 8, id="load-use-off"),
    pytest.param(LOAD_USE, True, 11, 1, id="load-use-on"),
])
def test_textbook_programs(sim, src, fwd, cycles, stalls):
    r = sim(src, forwarding=fwd)
    assert (r.cycles, r.stalls) == (cycles, stalls)


# ---------- hazard rules, one at a time ----------

ALU_D1 = "ADD R1, R2, R3\nADD R4, R1, R5"
ALU_D2 = "ADD R1, R2, R3\nADD R9, R2, R3\nADD R4, R1, R5"
ALU_D3 = "ADD R1, R2, R3\nADD R9, R2, R3\nADD R8, R2, R3\nADD R4, R1, R5"
LOAD_D1 = "LW R1, 0(R2)\nADD R4, R1, R5"
LOAD_D2 = "LW R1, 0(R2)\nADD R9, R2, R3\nADD R4, R1, R5"


@pytest.mark.parametrize("src, fwd, stalls", [
    pytest.param(ALU_D1, False, 2, id="alu-dist1-off"),
    pytest.param(ALU_D1, True, 0, id="alu-dist1-on"),
    pytest.param(ALU_D2, False, 1, id="alu-dist2-off"),
    pytest.param(ALU_D2, True, 0, id="alu-dist2-on"),
    pytest.param(ALU_D3, False, 0, id="alu-dist3-off"),
    pytest.param(LOAD_D1, False, 2, id="load-use-dist1-off"),
    pytest.param(LOAD_D1, True, 1, id="load-use-dist1-on"),
    pytest.param(LOAD_D2, False, 1, id="load-use-dist2-off"),
    pytest.param(LOAD_D2, True, 0, id="load-use-dist2-on"),
    pytest.param("ADD R1, R2, R3\nADD R4, R5, R1", False, 2, id="second-operand"),
    pytest.param("ADD R1, R2, R3\nSW R1, 0(R2)", False, 2, id="store-data-off"),
    pytest.param("ADD R1, R2, R3\nSW R1, 0(R2)", True, 0, id="store-data-on"),
    pytest.param("ADD R2, R3, R4\nSW R1, 0(R2)", True, 0, id="store-base-on"),
    pytest.param("LW R1, 0(R2)\nSW R1, 4(R2)", True, 1, id="load-store-no-mem-mem-path"),
    pytest.param("ADD R0, R2, R3\nADD R4, R0, R5", False, 0, id="r0-never-hazard"),
    pytest.param("SW R1, 0(R2)\nADD R4, R1, R5", False, 0, id="store-writes-nothing"),
    pytest.param("ADD R1, R2, R3\nADD R2, R4, R5", False, 0, id="war-not-a-hazard"),
    pytest.param("ADD R1, R2, R3\nADD R1, R4, R5", False, 0, id="waw-not-a-hazard"),
])
def test_hazard_rules(sim, src, fwd, stalls):
    assert sim(src, forwarding=fwd).stalls == stalls


# ---------- regressions for bugs in the original processor.py ----------

def test_full_throughput_one_fetch_per_cycle(sim):
    """Original fetched every other cycle. 20 independent instructions = 24 cycles."""
    src = "\n".join(f"ADD R{i % 30 + 1}, R0, R0" for i in range(20))
    r = sim(src)
    assert r.cycles == 24


def test_no_trailing_empty_cycle(sim):
    """Original counted one extra empty cycle at the end."""
    r = sim(NO_HAZARDS)
    assert r.timeline[-1]["WB"] == r.cycles


def test_single_instruction(sim):
    """Original raised IndexError for a one-instruction program."""
    r = sim("ADD R1, R2, R3")
    assert r.cycles == 5


def test_empty_program(sim):
    r = sim("")
    assert (r.cycles, r.instructions, r.cpi) == (0, 0, 0.0)


def test_long_dependency_chain(sim):
    """Original sized arrays as count*6; long chains must not overflow."""
    src = "\n".join("ADD R1, R1, R2" for _ in range(300))
    r = sim(src, forwarding=False)
    assert r.stalls == 2 * 299
    assert r.cycles == 300 + 4 + 2 * 299


# ---------- structural invariants ----------

@pytest.mark.parametrize("fwd", [False, True], ids=["off", "on"])
@pytest.mark.parametrize("src", PROGRAMS, ids=["no-hazards", "data", "load-use"])
def test_cycle_identity(sim, src, fwd):
    r = sim(src, forwarding=fwd)
    assert r.cycles == r.instructions + 4 + r.stalls
    assert r.cpi == pytest.approx(r.cycles / r.instructions)


def test_timeline_shape(sim):
    r = sim(DATA_HAZARDS, forwarding=False)
    stalls_per_instr = {}
    for s in r.stall_log:
        stalls_per_instr[s.instr] = stalls_per_instr.get(s.instr, 0) + 1

    fetches = [t["IF"] for t in r.timeline]
    assert fetches == sorted(set(fetches)), "fetch order must be strictly increasing"
    for i, t in enumerate(r.timeline):
        assert t["IF"] < t["ID"] < t["EX"]
        assert t["EX"] - t["ID"] - 1 == stalls_per_instr.get(i, 0)
        assert t["MEM"] == t["EX"] + 1 and t["WB"] == t["MEM"] + 1


def test_stall_log_entry(sim):
    r = sim(LOAD_D1, forwarding=True)
    assert len(r.stall_log) == 1
    s = r.stall_log[0]
    assert (s.cycle, s.instr, s.reason, s.reg) == (4, 1, "RAW", "R1")
    assert r.timeline[1] == {"IF": 2, "ID": 3, "EX": 5, "MEM": 6, "WB": 7}


# ---------- parser ----------

def test_parse_fields():
    lw, add, sw = parse_program("LW R1, 8(R2)\nADD R3, R1, R4\nSW R3, -4(R2)")
    assert (lw.op, lw.dest, lw.srcs, lw.imm) == ("LW", "R1", ("R2",), 8)
    assert (add.op, add.dest, add.srcs) == ("ADD", "R3", ("R1", "R4"))
    assert (sw.op, sw.dest, sw.srcs, sw.imm) == ("SW", None, ("R3", "R2"), -4)


def test_parse_comments_blanks_and_case():
    prog = parse_program("  # header comment\n\nlw r1, 0(r2)   ; trailing\n")
    assert len(prog) == 1
    assert (prog[0].op, prog[0].dest) == ("LW", "R1")


def test_parse_labels():
    prog = parse_program("start: ADD R1, R2, R3")
    assert prog[0].label == "start"


def test_parse_rejects_unknown_op():
    with pytest.raises(ValueError, match="line 2"):
        parse_program("ADD R1, R2, R3\nFOO R1")


def test_parse_rejects_bad_operands():
    with pytest.raises(ValueError, match="line 1"):
        parse_program("ADD R1, R2")
