# PhysRetime
Physical-aware Retiming with VPR and ABC

## Key Features

### 1. Path Node Extraction
- `extract_path_nodes(report_path, top_n)`  
  Extracts all unique `.names` nodes (main name only) from the top N critical paths in STA reports (e.g., `report_timing.setup.rpt`). Used for guiding retiming.

### 2. Latch Parameter Extraction and Insertion
- `extract_first_latch_params(blif_path)`  
  Extracts the last three parameters (e.g., `re pclk 2`) from the first `.latch` line in a blif file, for use in clock insertion.
- `optimize_latch_lines_inplace(blif_path, latch_params)`  
  Replaces the last three parameters of all `.latch` lines in the blif file with the extracted values, in-place.

### 3. Iterative VPR/ABC Flow
- `top.py`  
  Automates multiple rounds of VPR routing, timing analysis, path extraction, ABC retiming, and latch parameter insertion. Each round is stored in a separate subdirectory for easy tracking.

### 4. Statistics and Analysis
- `extract_delay_fmax_from_log(log_path)`  
  Extracts the final critical path delay and Fmax from VPR logs.
- `stat_all_iters(bench_dir)`  
  Collects and prints delay and Fmax for all iterations in a summary table.

## Physical-aware Retiming with Modified ABC

> **Note:**  
> This project uses a customized version of ABC, which has been modified to support retiming based on physical (post-routing) delay information. This enables more accurate and practical retiming for real-world FPGA back-end flows.

## Requirements

- Python 3.6+
- VTR toolchain (VPR, ABC, etc.; ABC must be the modified version supporting physical delays)
- Linux environment is recommended

## Typical Usage

1. **Prepare blif and architecture files**  
   Place your target blif and architecture XML files in the specified locations.

2. **Run the main flow**  
   ```bash
   python top.py
   ```
   This will automatically perform multiple rounds of optimization, with all intermediate results saved in `diffeq_test/iter*/`.

3. **Path extraction/statistics**  
   You can also run `retime_prep.py` independently for path extraction, blif latch optimization, or statistics:
   ```bash
   python retime_prep.py
   ```

## Output

- Each iteration's VPR logs, timing reports, and optimized blif files are stored in their respective `iter*` subdirectories.
- Path node information is output to `cpdInfo.txt`.
- Statistics are printed to the terminal.

## Notes

- You can customize path extraction, latch parameter insertion, and other rules by editing the relevant functions in `retime_prep.py`.
- For new requirements or issues, feel free to extend or improve this project.
