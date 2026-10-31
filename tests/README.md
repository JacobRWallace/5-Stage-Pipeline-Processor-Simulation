# Test suite

Tests come first. Each team owns one file, and the shared contract lives in
`pipeline_sim/core.py`.

```bash
pip install pytest
pytest            # everything
pytest tests/test_cache.py -v
```

## How gating works

- `test_core.py` is always active. It starts red (the core is a stub) and must
  go green in week 1 before anything else merges.
- Every extension file starts with `pytest.importorskip("pipeline_sim.<module>")`.
  The tests show as **skipped** until that team creates its module, then they
  switch on automatically.
- Integration tests that need real register values also skip until
  `pipeline_sim/functional.py` exists.

## Ownership

| File | Extension | Module that unlocks it | People |
|---|---|---|---:|
| `test_core.py` | Core pipeline + parser | (always on) | 1 |
| `test_branch.py` | 1. Branches + prediction | `branch.py` | 2 |
| `test_cache.py` | 2. Cache hierarchy | `cache.py` | 2 |
| `test_ooo.py` | 3a. Out-of-order (Tomasulo) | `ooo.py` | 2 |
| `test_superscalar.py` | 3b. Dual issue (fallback for 3a) | `superscalar.py` | (same 2) |
| `test_workloads.py` | 4. C -> RISC-V workloads | `riscv.py` | 1 |
| `test_functional.py` | 5. Real values + multi-cycle ops | `functional.py` | 1 |
| `test_experiments.py` | 6. Experiment runner | `experiments.py` | core lead |

## Timing conventions (everyone codes to these)

- Classic 5-stage MIPS: IF, ID, EX, MEM, WB. Cycles are 1-indexed.
- Register file writes in the first half of WB, reads in the second half of ID.
- Forwarding paths: EX/MEM -> EX and MEM/WB -> EX. No MEM -> MEM path.
- Hazards are detected in ID. One stall = one bubble cycle, logged in `stall_log`.
- Branches and jumps resolve in EX. A mispredict costs 2 bubbles (`flushes`).
- One EX unit. Multi-cycle ops (MUL/DIV) occupy it for their full latency.
- `MemoryModel.access()` returns **extra** cycles: hit = 0, miss = penalty.
- R0 is hardwired to zero. Uninitialized registers and memory read as 0.
- DIV truncates toward zero.

## Rules

- New opcodes go into the core parser's op table, with a parser test.
- Changing a convention above means changing the tests in the same PR, and the
  whole team signs off.
- Never edit someone else's test to make your code pass. Ask first.
