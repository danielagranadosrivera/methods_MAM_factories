# Methods used for “Drone-enhanced offshore spare part fulfilment using mobile additive manufacturing factories and multi-modal delivery”

[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6](https://img.shields.io/badge/python-3.6-yellow.svg)](https://www.python.org/downloads/release/python-360/)
[![DOI](https://img.shields.io/badge/DOI-10.1080%2F00207543.2025.2540454-blue)](https://doi.org/10.1080/00207543.2025.2540454)

## Overview

This repository contains the implementation of a **Two-stage Matheuristic** and a **Adaptive Large Neighborhood Search (ALNS)**. Both methods were employed in the study **“Drone-enhanced offshore spare part fulfilment using mobile additive manufacturing factories and multi-modal delivery”**, published in the *International Journal of Production Research*.

> **Associated Paper**
>
> Granados-Rivera, D., Silva, D. F., Smith, A. E., Sgarbossa, F., & Knofius, N. (2025). *Drone-enhanced offshore spare part fulfilment using mobile additive manufacturing factories and multi-modal delivery*. International Journal of Production Research, 1–26. https://doi.org/10.1080/00207543.2025.2540454

---
## Problem Description

This work addresses the integrated optimization of:
- **Mobile Additive Manufacturing (MAM) factory relocation**: Decisions of when and where to move MAM factories along the planning horizon.
- **Production Planning**: Definition of which spare parts to produce at each MAM factory and when to produce them.
- **Multimodal distribution**: Selection of the transportation model to ship the spare parts. The modes include drone or a two-echelon structure of truck and ship.
- **Drone routing**: Design of the optimal drone routes to ship the spare parts to the offshore oil platforms.

The objective is to minimize total cost including relocation cost, production cost, transportation cost, and late delivery penalties across a multi-period planning horizon.

---

## Repository Structure

```
methods_MAM_factories/
│
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
│
├── matheuristic/                                 # Two stage matheuristic implementation
│   ├── MobileFactories_MultipleCB_Warmup.py      # Main file
│   ├── First_Stage.py                            # First stage: relocation and production decisions
│   ├── warmup_firstpart.py                       # Warmup procedure to generate initial feasible solutions
│   ├── Second_Stage_Ini_Warmup.py                # Second stage initialization for the first rolling horizon window
│   ├── Second_Stage_Decomposition.py             # Rolling horizon decomposition for the second stage
│   ├── functions.py                              # Utility functions (distances, costs, data formatting)
│   └── data/
│       ├── input/                                # Place input CSV files here
│       ├── models/                               # OPL model files (.mod and .ops)
│       │   ├── MFLP_No_Routing.mod
│       │   ├── MFLP_No_Routing.ops
│       │   ├── Routing_drones_Warmup.mod
│       │   ├── Routing_drones_Warmup.ops
│       │   ├── Routing_drones_Decomposition.mod
│       │   └── Routing_drones_Decomposition.ops
│       └── output/                               # Results generated here automatically
│
├── alns/                                         # ALNS implementation
│   ├── ALNS_main.py                              # Main file
│   ├── functions_ALNS.py                         # ALNS class, solution class, operators
│   ├── main_greedy_MF.py                         # Greedy initial solution
│   ├── functions_greedy_MF.py                    # Utility functions for greedy heuristics
│   ├── initialization_routes.py                  # Routes initialization utilities
│   └── data/
│       ├── input/                                # Place input CSV files here
│       └── output/                               # Results generated here automatically
└── sample_data/
    └── small_instance_1/                         # Sample instance for testing
    
```

## Solution Methods

### Two-Stage Matheuristic

**Stage 1: Strategic planning (exact MILP via CPLEX/OPL):**
Solves relocation and production decisions or the entire planning horizon. Uses estimated transportation costs to avoid routing complexity. Runs in under one minute for realistic instances.

**Stage 2: Operational planning (rolling horizon decomposition):**
Given fixed relocation and production decisions from Stage 1, optimizes distribution mode selection and drone routing week-by-week using a rolling horizon approach. Each weekly subproblem is solved exactly.

**Performance (published results):**
- Up to **60x faster** than solving the complete integrated MILP for small and medium instances.
- Less than **6% optimality gap** on small and medium instances.
- Outperforms ALNS by up to **15x** in solution quality within the same computational time for small and medium instances.

### Adaptive Large Neighborhood Search (ALNS)

A metaheuristic benchmark implementing:
- **Greedy initialization**: Uses a score function based on demand coverage and drone accessibility.
- **3 destroy operators**: Penalty-based deallocation, random drone shipment removal, random truck/ship removal.
- **2 repair operators**: Drone-priority reassignment, ship-priority reassigments.
- **Simulated annealing**: Acceptance criterion with adaptive operator weights.

---

## Dependencies and Installation

### Requirements

- Python 3.6.13 (required for doopl compatibility).
- IBM CPLEX 12.10 with a valid license (required for matheuristic only).
- Conda package manager (recommended).

### Step 1 — Create conda environment with Python 3.6

```bash
conda create -n mam_env python=3.6.13
conda activate mam_env
```

### Step 2 — Install IBM doopl (matheuristic only)

doopl requires IBM CPLEX to be installed on your system. Once CPLEX is installed:

```bash
conda install -c ibmdecisionoptimization doopl=12.10.0.26
```

### Step 3 — Install remaining dependencies

```bash
pip install -r requirements.txt
```

> **Note:** The ALNS does **not** require CPLEX or doopl. It can be run with only the pip dependencies.

---

## Data

### Sample Data

A sample instance is provided in `sample_data/small_instance_1/` for testing. Copy these files into the appropriate `data/input/` folder before running.

**For the matheuristic:**
```bash
cp sample_data/small_instance_1/* matheuristic/data/input/
```

**For the ALNS:**
```bash
cp sample_data/small_instance_1/* alns/data/input/
```

### Full Dataset

The complete dataset used in the paper — including small, medium, and case study instances — is available in a separate repository:

**Dataset Repository:** [https://github.com/danielagranadosrivera/offshore-mam-factories-dataset](https://github.com/danielagranadosrivera/offshore-mam-factories-dataset)

### Input File Format

| File | Description |
|------|-------------|
| `parameters.csv` | Model parameters (costs, speeds, planning horizon, etc.) |
| `locations.csv` | Coordinates of potential MAM factory locations (latitude, longitude) |
| `customers.csv` | Coordinates of offshore customer locations (latitude, longitude) |
| `harbors.csv` | Coordinates of harbor locations (latitude, longitude) |
| `beta.csv` | Ship sailing schedule (harbor, customer, cluster, period, availability) |
| `lambda.csv` | Demand data (product, customer, cluster, period, quantity) |
| `eta.csv` | Part weights in kilograms |
| `theta.csv` | Factory capability matrix (factory × part) |
| `alpha.csv` | Part cross-sectional areas in mm² |

For detailed documentation of each file format see the [dataset repository](https://github.com/danielagranadosrivera/offshore-mam-factories-dataset).

---

## Running the Code

### Running the Matheuristic

```bash
cd matheuristic
python MobileFactories_MultipleCB_Warmup.py
```

The matheuristic runs for all penalty cost values defined in `CB_values` (default: `[50, 275, 500]`). To run a single value, edit line 14 of the main file:

```python
CB_values = [275]  # run only for CB = 275 USD
```

**Output:** Results are saved in `matheuristic/data/output/CB_{value}/` for each penalty cost value, including:
- `x.csv`: relocation decisions
- `y_hat.csv`: production decisions
- `z_hat.csv`: drone shipment decisions
- `s.csv`: drone routes
- `w_hat.csv`: truck shipments to harbors
- `u.csv`: ship shipments to customers
- `f.csv`: late delivery units
- `Summary.txt`: cost breakdown and key metrics
- `Summary_decisions.csv`: period-by-period decision log

### Running the ALNS

```bash
cd alns
python ALNS_main.py
```

The ALNS reads the penalty cost directly from `parameters.csv` (row 23). To change it, update the parameters file.

**Key ALNS parameters** (configurable in `ALNS_main.py`):
```python
seed = 872971           # random seed for reproducibility
updating_period = 5     # operator weight update frequency
max_time_alns = 300     # stopping criterion in seconds
T_0 = 1000              # initial simulated annealing temperature
alpha_sa = 0.99         # cooling rate
```

**Output:** Results are saved in `alns/data/output/` with the same file structure as the matheuristic.

---

## Reproducing Paper Results

To reproduce the results from Table 2 and Table 3 of the paper:

1. Download the small and medium instances from the [dataset repository](https://github.com/danielagranadosrivera/offshore-mam-factories-dataset).
2. Copy each instance into `matheuristic/data/input/.`
3. Run the matheuristic with `CB_values = [50, 275, 500].`
4. Copy the same instance into `alns/data/input/`.
5. Run the ALNS with matching CB value in `parameters.csv`.
6. Compare results from the respective `Summary.txt` files.

For the case study results (Tables 4-6 and Figures 5-10), use the case study instance from the dataset repository with all 72 experimental configurations described in Section 2.5.2 of the paper.

---

## Case Study

The case study models spare parts supply to offshore oil platforms in the Norwegian, Barents, and North Seas, conducted in collaboration with [Fieldmade](https://fieldmade.no/), a Norwegian company implementing MAM factory solutions for offshore environments.

**Network:** 10 potential MAM factory locations, 30 offshore customer locations, 5 harbor locations along the Norwegian coastline.

**Planning horizon:** 30 days with weekly ship schedules.

---

## Citation

If you use this code in your research, please cite it using the information provided in `CITATION.cff`.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or issues related to the code, please open a GitHub issue in this repository. For further information about the research, please refer to the associated [article](https://doi.org/10.1080/00207543.2025.2540454).
