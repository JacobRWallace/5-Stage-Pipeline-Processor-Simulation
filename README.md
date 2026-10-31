# 5-Stage Pipeline Processor Simulation

A Python-based simulation of a 5-stage CPU instruction pipeline demonstrating **Read After Write (RAW) data hazards, pipeline stalls, data forwarding, and performance analysis**.

Developed for **CS5365: Principles of Multiple-Processor Systems** at Texas Tech University, Summer 2026.

## Overview

The project simulates how instructions move through a 5-stage processor pipeline, detects register dependencies, and inserts stalls when required.

It compares execution with **forwarding enabled and disabled**, measuring how data hazards affect total execution cycles, stall counts, and Cycles Per Instruction (CPI).

### Pipeline Architecture

| Stage | Name | Purpose |
|---|---|---|
| IF | Instruction Fetch | Retrieves the next instruction |
| ID | Instruction Decode | Identifies registers and checks for data hazards |
| EX | Execute | Processes the instruction |
| MEM | Memory Access | Represents the memory access stage |
| WB | Write Back | Represents the register write-back stage |

## Features

- **5-Stage Pipeline Simulation:** Tracks instructions cycle-by-cycle through IF, ID, EX, MEM, and WB.
- **RAW Hazard Detection:** Identifies instructions dependent on unfinished register writes.
- **Automatic Stall Insertion:** Delays dependent instructions until their required registers become available.
- **Data Forwarding:** Models earlier availability of instruction results to reduce stalls.
- **Multiple Test Programs:** Simulates three different dependency scenarios.
- **Performance Analysis:** Calculates total cycles, stalls, and CPI.
- **Execution Visualization:** Prints cycle-by-cycle pipeline tables and hazard explanations.

### Supported Instructions

| Instruction | Operation |
|---|---|
| `LW` | Load Word |
| `SW` | Store Word |
| `ADD` | Addition |
| `SUB` | Subtraction |
| `AND` | Bitwise AND |

The simulator models instruction timing and dependencies rather than actual arithmetic or memory values.

## Installation

### Requirements

- Python 3
- Windows, macOS, or Linux
- No external Python dependencies

### 1. Clone the Repository

```bash
git clone https://github.com/JacobRWallace/5-Stage-Pipeline-Processor-Simulation.git
```

### 2. Navigate to the Project

```bash
cd 5-Stage-Pipeline-Processor-Simulation
```

### 3. Run the Simulator

**Windows:**

```powershell
python src/processor.py
```

**macOS / Linux:**

```bash
python3 src/processor.py
```

No installation of additional packages is required.

## Simulation Process

The simulator performs the following operations:

1. **Initialize Test Programs:** Define three instruction sequences containing different register dependencies.
2. **Configure Forwarding:** Execute each program with forwarding OFF and ON.
3. **Initialize Pipeline:** Create tracking structures for IF, ID, EX, MEM, and WB.
4. **Advance Clock Cycles:** Move instructions between pipeline stages.
5. **Detect RAW Hazards:** Check whether source registers depend on unfinished instructions.
6. **Insert Stalls:** Hold instructions in ID until required data becomes available.
7. **Apply Forwarding:** Reduce register availability delays when forwarding is enabled.
8. **Calculate Performance:** Report total clock cycles, stalls, and CPI.

Each program executes twice, producing **six simulation runs**.

## Test Scenarios

### 1. No Data Hazards

Instructions operate independently without requiring results from preceding instructions.

**Expected behavior:** No stalls occur, regardless of forwarding configuration.

### 2. Data Hazards

Instructions depend on register values produced by previous instructions.

**Expected behavior:** RAW hazards introduce stalls, while forwarding reduces the waiting time.

### 3. Load-Use Hazards

An instruction immediately depends on data loaded by a preceding `LW` instruction.

**Expected behavior:** A load-use dependency may still require a stall even when forwarding is enabled.

## Results

The following results were recorded during the project simulations.

> **Note:** these numbers include two known timing bugs in `processor.py` (it fetches only every other cycle and counts one extra empty cycle at the end). Textbook values are 9/9, 17/10 and 18/11 cycles with 0/0, 8/1 and 8/1 stalls; `tests/test_core.py` checks against those.

| Test Program | Forwarding OFF Cycles | Forwarding ON Cycles | OFF Stalls | ON Stalls |
|---|---:|---:|---:|---:|
| No Hazards | 14 | 14 | 0 | 0 |
| Data Hazards | 18 | 14 | 7 | 1 |
| Load-Use Hazards | 19 | 16 | 7 | 1 |

### Performance Measurements

The simulator calculates:

**Cycles Per Instruction (CPI):**

\[
CPI = \frac{\text{Total Clock Cycles}}{\text{Total Instructions}}
\]

Lower CPI indicates fewer average clock cycles per instruction in the simulated workload.

### Key Findings

- Forwarding does not improve programs without register dependencies.
- Forwarding reduces stalls from **7 to 1** in both hazard test programs.
- Data hazard test cycles decrease from **18 to 14**.
- Load-use hazard test cycles decrease from **19 to 16**.
- Reducing pipeline stalls improves overall simulated instruction throughput.

## Output

Running `src/processor.py` produces:

- Instruction listings for each test program
- Cycle-by-cycle pipeline execution tables
- Forwarding ON/OFF configurations
- Stall explanations identifying unavailable registers
- Instruction counts, total cycles, stall counts, and CPI
- Final comparison of all three test scenarios

## Running the Tests

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pytest
.venv/bin/python -m pytest
```

Tests import the `pipeline_sim` package (`src/pipeline_sim/`), a thin adapter that parses assembly text, runs `processor.run()`, and returns cycles, stalls, CPI, a per-instruction timeline, and a stall log. `tests/test_core.py` is always on and currently fails where `processor.py` deviates from textbook timing. See [`tests/README.md`](tests/README.md) for the full conventions.

## Extensions

The project is planned to grow in six extensions. Each one has its own test file that is **skipped** until the matching module exists in `src/pipeline_sim/`, then switches on automatically.

| # | Extension | Module | Tests | What it adds |
|---|---|---|---|---|
| 0 | Core pipeline + parser | `core.py` | `test_core.py` | Correct 5-stage timing, hazard rules, forwarding, assembly parser. Must be green before anything else merges. |
| 1 | Branches + prediction | `branch.py` | `test_branch.py` | Control hazards resolved in EX (2-cycle flush on mispredict) and `AlwaysNotTaken`, `AlwaysTaken`, `OneBit`, `TwoBit` predictors. |
| 2 | Cache hierarchy | `cache.py` | `test_cache.py` | Set-associative `Cache(size, block, assoc, miss_penalty)` with LRU and write-allocate; misses stall the MEM stage. |
| 3a | Out-of-order execution | `ooo.py` | `test_ooo.py` | Tomasulo with a reorder buffer: register renaming (WAR/WAW), in-order commit, independent work passes stalled instructions. |
| 3b | Dual issue (fallback for 3a) | `superscalar.py` | `test_superscalar.py` | In-order 2-wide issue; dependent pairs are not co-issued. |
| 4 | Real workloads | `riscv.py` | `test_workloads.py` | `parse_riscv()` maps RISC-V registers/ABI names onto R0–R31, ignores directives, supports `li`, `mv`, `nop`. Drop `gcc -S` output into `tests/workloads/*.s`. |
| 5 | Functional execution | `functional.py` | `test_functional.py` | Real register/memory values, `ADDI`, `MUL`/`DIV` (truncating), R0 hardwired to zero, multi-cycle latencies with structural stalls. |
| 6 | Experiment runner | `experiments.py` | `test_experiments.py` | `sweep(programs, configs)` over every program × config, with CSV export. |

### Shared timing conventions

- Cycles are 1-indexed. Register file writes in the first half of WB, reads in the second half of ID.
- Forwarding paths: EX/MEM → EX and MEM/WB → EX. No MEM → MEM path.
- Hazards are detected in ID; one stall is one bubble cycle.
- Branches and jumps resolve in EX; a mispredict costs 2 bubbles.
- One EX unit; multi-cycle ops occupy it for their full latency.
- `access()` on a cache returns **extra** cycles: hit = 0, miss = penalty.

## Project Files

```text
5-Stage-Pipeline-Processor-Simulation/
├── src/
│   ├── processor.py          # original simulator, now exposes run(program, forwarding)
│   └── pipeline_sim/         # test-facing API (core.py + future extension modules)
├── tests/                    # pytest suite, one file per extension
├── docs/
│   ├── 5-Stage Pipeline Processor Simulation with Data Hazard Detection and Forwarding.pdf
│   ├── CS5365_Pipeline_Processor_Simulation_Jacob_Wallace.pptx
│   └── Project guidelines.pdf
├── pytest.ini
└── README.md
```

| File | Description |
|---|---|
| `src/processor.py` | Main Python implementation of the pipeline simulator |
| `src/pipeline_sim/` | Parser and adapter used by the tests and extensions |
| `tests/` | Test suite; see `tests/README.md` |
| Project Report (PDF) | Written project documentation and simulation results |
| Presentation (PPTX) | Project overview, pipeline architecture, and experimental results |
| Project Guidelines (PDF) | Original course project requirements |

## Academic Information

**Author:** Jacob Wallace  
**Institution:** Texas Tech University  
**Course:** CS5365 — Principles of Multiple-Processor Systems  
**Semester:** Summer 2026  
**Instructor:** Dr. B. I. Morshed


<!-- EXTENSTION FALL 2026 -->

