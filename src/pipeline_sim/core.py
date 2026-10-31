"""Shared contract the tests code against, backed by processor.run().

parse_program() turns assembly text into Instructions; Pipeline converts them
to processor.py's dict format, runs the original simulator, and reshapes its
stage table into a Result (timeline, stall_log, cycles, CPI).
"""
import re
from dataclasses import dataclass, field

import processor

REG = r"[Rr](\d+)"

# op -> operand format. New opcodes go here (with a parser test).
OPS = {
    "ADD": "rrr",
    "SUB": "rrr",
    "AND": "rrr",
    "LW": "mem",
    "SW": "mem",
}


@dataclass(frozen=True)
class Instruction:
    op: str
    dest: str | None
    srcs: tuple
    imm: int | None = None
    label: str | None = None


def _reg(text, lineno):
    m = re.fullmatch(REG, text.strip())
    if not m:
        raise ValueError(f"line {lineno}: bad register {text.strip()!r}")
    return f"R{int(m.group(1))}"


def parse_program(src):
    prog = []
    for lineno, raw in enumerate(src.splitlines(), 1):
        line = re.split(r"[#;]", raw, maxsplit=1)[0].strip()
        label = None
        if ":" in line:
            label, line = (part.strip() for part in line.split(":", 1))
        if not line:
            continue
        op, _, rest = line.partition(" ")
        op = op.upper()
        if op not in OPS:
            raise ValueError(f"line {lineno}: unknown op {op!r}")
        args = [a.strip() for a in rest.split(",")] if rest.strip() else []
        if OPS[op] == "rrr":
            if len(args) != 3:
                raise ValueError(f"line {lineno}: {op} needs 3 registers")
            d, s1, s2 = (_reg(a, lineno) for a in args)
            prog.append(Instruction(op, d, (s1, s2), label=label))
        else:
            m = re.fullmatch(r"(-?\d+)\((.+)\)", args[1]) if len(args) == 2 else None
            if not m:
                raise ValueError(f"line {lineno}: {op} needs 'reg, imm(base)'")
            r, imm, base = _reg(args[0], lineno), int(m.group(1)), _reg(m.group(2), lineno)
            if op == "LW":
                prog.append(Instruction(op, r, (base,), imm, label))
            else:
                prog.append(Instruction(op, None, (r, base), imm, label))
    return prog


@dataclass
class Config:
    forwarding: bool = True


@dataclass(frozen=True)
class Stall:
    cycle: int
    instr: int
    reason: str
    reg: str


@dataclass
class Result:
    cycles: int
    instructions: int
    stalls: int
    stall_log: list
    timeline: list
    regs: dict = field(default_factory=dict)
    mem: dict = field(default_factory=dict)

    @property
    def cpi(self):
        return self.cycles / self.instructions if self.instructions else 0.0


def _to_processor(instr):
    if instr.op == "LW":
        return {"op": "LW", "dest": instr.dest, "offset": instr.imm, "base": instr.srcs[0]}
    if instr.op == "SW":
        return {"op": "SW", "src1": instr.srcs[0], "offset": instr.imm, "base": instr.srcs[1]}
    return {"op": instr.op, "dest": instr.dest, "src1": instr.srcs[0], "src2": instr.srcs[1]}


class Pipeline:
    def __init__(self, program, config=None, regs=None, mem=None):
        self.program = list(program)
        self.config = config or Config()
        self.regs = dict(regs or {})
        self.mem = dict(mem or {})

    def run(self):
        out = processor.run([_to_processor(i) for i in self.program], self.config.forwarding)
        timeline = [{} for _ in self.program]
        for name, slots in out["stage"].items():
            for cycle, idx in enumerate(slots):
                if idx is not None:
                    timeline[idx].setdefault(name, cycle)
        stall_log = [Stall(c, i, "RAW", r) for c, i, r in out["stalls"]]
        return Result(
            cycles=out["cycleCount"],
            instructions=len(self.program),
            stalls=len(stall_log),
            stall_log=stall_log,
            timeline=timeline,
            regs=self.regs,
            mem=self.mem,
        )
