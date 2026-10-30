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
python processor.py
```

**macOS / Linux:**

```bash
python3 processor.py
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

Running `processor.py` produces:

- Instruction listings for each test program
- Cycle-by-cycle pipeline execution tables
- Forwarding ON/OFF configurations
- Stall explanations identifying unavailable registers
- Instruction counts, total cycles, stall counts, and CPI
- Final comparison of all three test scenarios

## Project Files

```text
5-Stage-Pipeline-Processor-Simulation/
├── processor.py
├── README.md
├── 5-Stage Pipeline Processor Simulation with Data Hazard Detection and Forwarding.pdf
├── CS5365_Pipeline_Processor_Simulation_Jacob_Wallace.pptx
└── Project guidelines.pdf
```

| File | Description |
|---|---|
| `processor.py` | Main Python implementation of the pipeline simulator |
| Project Report (PDF) | Written project documentation and simulation results |
| Presentation (PPTX) | Project overview, pipeline architecture, and experimental results |
| Project Guidelines (PDF) | Original course project requirements |

## Limitations

This project is an educational simulation of pipeline timing and dependency handling, not a complete CPU emulator.

It does not implement actual instruction execution, physical register storage, memory operations, or a complete processor instruction set.

## Academic Information

**Author:** Jacob Wallace  
**Institution:** Texas Tech University  
**Course:** CS5365 — Principles of Multiple-Processor Systems  
**Semester:** Summer 2026  
**Instructor:** Dr. B. I. Morshed
