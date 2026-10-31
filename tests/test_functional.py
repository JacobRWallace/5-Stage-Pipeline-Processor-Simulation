"""Extension 5: functional execution (real values) + multi-cycle ops.
Unlocks when pipeline_sim/functional.py exists.

Convention: one EX unit. A multi-cycle op occupies EX for its whole latency,
so anything behind it waits (RAW or structural).
"""
import pytest

pytest.importorskip("pipeline_sim.functional", reason="extension 5 not started")


def test_alu_values(sim):
    r = sim("ADD R3, R1, R2\nSUB R4, R3, R1\nAND R5, R3, R2", regs={"R1": 6, "R2": 3})
    assert (r.regs["R3"], r.regs["R4"], r.regs["R5"]) == (9, 3, 1)


def test_load_store(sim):
    r = sim("LW R1, 0(R2)\nADD R1, R1, R1\nSW R1, 4(R2)", regs={"R2": 100}, mem={100: 42})
    assert r.regs["R1"] == 84
    assert r.mem[104] == 84


def test_addi_negative(sim):
    assert sim("ADDI R1, R0, -7").regs["R1"] == -7


def test_r0_hardwired_zero(sim):
    r = sim("ADDI R0, R0, 5\nADD R1, R0, R0")
    assert r.regs.get("R0", 0) == 0 and r.regs["R1"] == 0


def test_uninitialized_registers_read_zero(sim):
    assert sim("ADD R1, R2, R3").regs["R1"] == 0


def test_forwarding_never_changes_results(sim):
    src = "LW R1, 0(R2)\nADD R3, R1, R1\nSUB R4, R3, R1\nSW R4, 8(R2)\nLW R5, 8(R2)"
    kw = dict(regs={"R2": 16}, mem={16: 5})
    off, on = sim(src, forwarding=False, **kw), sim(src, forwarding=True, **kw)
    assert off.regs == on.regs and off.mem == on.mem


def test_mul_and_div_values(sim):
    r = sim("MUL R3, R1, R2\nDIV R4, R1, R2\nDIV R5, R6, R2", regs={"R1": 7, "R2": 2, "R6": -7})
    assert r.regs["R3"] == 14
    assert r.regs["R4"] == 3
    assert r.regs["R5"] == -3, "DIV truncates toward zero, like C"


def test_mul_latency_raw(sim):
    r = sim("MUL R3, R1, R2\nADD R4, R3, R1", forwarding=True, latencies={"MUL": 4})
    assert r.stalls == 3
    assert r.cycles == 9


def test_mul_latency_structural(sim):
    r = sim("MUL R3, R1, R2\nADD R4, R1, R1", forwarding=True, latencies={"MUL": 4})
    assert r.stalls == 3
    assert any(s.reason == "structural" for s in r.stall_log)
