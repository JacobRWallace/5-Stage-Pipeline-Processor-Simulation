"""Extension 4: real workloads (C -> RISC-V -> simulator).
Unlocks when pipeline_sim/riscv.py exists.

Convention: parse_riscv() maps x0..x31 and ABI names (a0, sp, t0, zero, ...)
onto R0..R31, so the core runs RISC-V code unchanged. Directives (.text, .globl,
...) are ignored. Supports the pseudo-ops li, mv, nop.

Drop gcc output (riscv64-unknown-elf-gcc -S) into tests/workloads/*.s and
each file gets its own test automatically.
"""
from pathlib import Path

import pytest

riscv = pytest.importorskip("pipeline_sim.riscv", reason="extension 4 not started")
parse_riscv = riscv.parse_riscv

from pipeline_sim import Config, Pipeline  # noqa: E402

WORKLOADS = sorted((Path(__file__).parent / "workloads").glob("*.s"))


def test_register_mapping():
    lw, add, sw = parse_riscv("lw a0, 8(sp)\nadd t0, a0, a1\nsw t0, -4(sp)")
    assert (lw.op, lw.dest, lw.srcs, lw.imm) == ("LW", "R10", ("R2",), 8)
    assert (add.op, add.dest, add.srcs) == ("ADD", "R5", ("R10", "R11"))
    assert (sw.op, sw.dest, sw.srcs, sw.imm) == ("SW", None, ("R5", "R2"), -4)


def test_directives_labels_and_pseudo_ops():
    src = """
        .text
        .globl main
    main:
        li   a0, 5
        mv   a1, a0
        nop
    """
    prog = parse_riscv(src)
    assert prog[0].label == "main"
    assert (prog[0].op, prog[0].dest, prog[0].srcs, prog[0].imm) == ("ADDI", "R10", ("R0",), 5)
    assert (prog[1].op, prog[1].dest, prog[1].srcs, prog[1].imm) == ("ADDI", "R11", ("R10",), 0)
    assert len(prog) == 3


def test_unsupported_instruction_reports_line():
    with pytest.raises(ValueError, match="line 2"):
        parse_riscv("add a0, a0, a0\nfence")


@pytest.mark.parametrize("path", WORKLOADS, ids=lambda p: p.name)
def test_workload_parses_and_runs(path):
    prog = parse_riscv(path.read_text())
    r = Pipeline(prog, Config()).run()
    assert r.instructions > 0
    assert r.cycles >= r.instructions + 4
