# Pipeline graphs notebook

`graphs.ipynb` runs `processor.py` and draws 3 graphs about stalls, clock cycles and CPI, with forwarding OFF and ON.
All numbers come from the simulator.

## Requirements
- Python 3
- matplotlib, numpy and Jupyter

```bash
python3 -m pip install matplotlib numpy jupyter
```

## How to run

### Option A: Google Colab
1. Open https://colab.research.google.com and choose File, then Upload notebook, and pick `graphs.ipynb`.
2. Click the folder icon on the left and upload `processor.py` next to the notebook.
3. Click Runtime, then Run all.

### Option B: on your computer
Open a terminal in the folder that has `graphs.ipynb` and `processor.py`:

```bash
python3 -m pip install matplotlib numpy jupyter
jupyter notebook graphs.ipynb
```

Then click Run, then Run All Cells. The PNGs are saved in `images/`.

## What you'll see
- **Graph 1, pipeline diagram:** the Data Hazards program cycle by cycle, forwarding OFF and ON. Stage names are IM, REG, ALU, DM, REG as in class, and a stall shows as `nop`.
- **Graph 2, total clock cycles:** every program, forwarding OFF vs ON.
- **Graph 3, CPI vs ideal:** CPI = (CC - 4) / N for every program against the ideal 1.0.

## Notes
- It needs the `processor.py` from PR #2 (5 programs and the timing fixes). On the old `main` the numbers are different.
- The simulator counts one empty cycle at the end, so the notebook uses `cycleCount - 1`.
- Branch Hazard is left out: the simulator stops the whole run at the branch.
- If PR #1 is merged, `processor.py` moves to `src/`. Keep the notebook next to `processor.py` or change the import.
