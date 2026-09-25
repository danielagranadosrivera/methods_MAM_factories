# Methods used for “Drone-enhanced offshore spare part fulfilment using mobile additive manufacturing factories and multi-modal delivery”

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![DOI](https://img.shields.io/badge/DOI-10.1080%2F00207543.2025.2540454-blue)](https://doi.org/10.1080/00207543.2025.2540454)

## Overview

This repository contains the implementation of a **Two-stage Matheuristic** and a **Adaptive Large Neighborhood Search (ALNS)**. Both methods were employed in the study **“Drone-enhanced offshore spare part fulfilment using mobile additive manufacturing factories and multi-modal delivery”**, published in the *International Journal of Production Research*.

> **Associated Paper**
>
> Granados-Rivera, D., Silva, D. F., Smith, A. E., Sgarbossa, F., & Knofius, N. (2025). *Drone-enhanced offshore spare part fulfilment using mobile additive manufacturing factories and multi-modal delivery*. International Journal of Production Research, 1–26. https://doi.org/10.1080/00207543.2025.2540454

---
## Problem Description

---

## Repository Structure

```
offshore-mam-factories-dataset-main/
│
├── README.md
├── LICENSE
├── CITATION.cff
│
└── data/
    ├── case_study/
    │   ├── demand_distribution_1/
    │   ├── demand_distribution_2/
    │   ├── demand_distribution_3/
    │   └── demand_distribution_4/
    │
    └── numerical_experiments/
        ├── small_instance_1/
        ├── small_instance_2/
        ├── medium_instance_1/
        └── medium_instance_2/
```


Each instance directory contains a complete set of CSV files describing the parameters required to run the optimization model and the proposed heuristics.

---

## Dataset Description

Each dataset instance includes the following files:

| File | Description |
|-----|-------------|
| `alpha.csv` | Cross-sectional area of each part in square millimetres. Each row corresponds to one part. This file contains a header. |
| `beta.csv` | Binary parameter indicating the availability of ships sailing from each harbour to each customer on each day. Each row represents a specific combination, and the column `Availability` indicates whether the connection is available (0 or 1). This file contains a header. |
| `customers.csv` | Coordinates of each offshore customer location considered in the instance. Each row represents a location. `X` corresponds to longitude and `Y` corresponds to latitude. This file contains a header. Locations were obtained from [The Ministry of Petroleum and Energy – Oil and Gas (2018)](https://www.regjeringen.no/en/topics/energy/oil-and-gas/id1003/). |
| `eta.csv` | Weight of each part in kilograms. Each row corresponds to one part. This file contains a header. |
| `harbors.csv` | Coordinates of each harbour location considered in the instance. Each row represents a location. `X` corresponds to longitude and `Y` corresponds to latitude. This file contains a header. |
| `lambda.csv` | Demand for each part for each customer on each day. Each row represents a combination, and the column `Value` indicates the number of units required. This file contains a header. |
| `locations.csv` | Coordinates of potential locations for mobile additive manufacturing (MAM) factories considered in the instance. Each row represents a location. `X` corresponds to longitude and `Y` corresponds to latitude. This file contains a header. |
| `parameters.csv` | Collection of different parameters required for each instance. Definitions of the parameters are provided below. This file contains a header. |
| `theta.csv` | Binary matrix indicating whether each MAM factory has the capability to produce each part. Columns represent parts and rows represent factories. This file contains a header. |

These files collectively define the input data required to solve the optimization problem studied in the research.

## Parameters.csv content

This file collects several parameters required for each instance. Each row contains the name of the parameter in column A and its value in column B. The parameters are defined as follows:

- *Number of drones*: Number of drones available in the instance.
- *Periods*: Total number of periods in the planning horizon.
- *CR_f*: Fixed relocation cost for moving a MAM factory (USD).
- *CR_v*: Variable relocation cost per kilometre for moving a MAM factory (USD).
- *CP_f*: Setup cost to produce a part per unit of cross-sectional area at any MAM factory on any day (USD).
- *CT*: Transportation cost per kilometre for drone delivery (USD).
- *CT1*: Transportation cost per kilometre for land transport (truck) (USD).
- *CT2*: Fixed handling cost for shipping by ship per one part in any period (USD).
- *CT3*: Transportation cost per unit for drone delivery (USD).
- *CT4*: Transportation cost per unit for land transport (truck) (USD).
- *V_average*: Average relocation speed of a MAM factory (km/h).
- *r_estimation*: Setup time required at a new location when relocating a MAM factory (hours).
- *M*: Sufficiently large constant used in the optimization model.
- *MA*: Maximum cross-sectional area available for batching in a build (square millimetres).
- *tau*: Weight capacity of a drone (kg).
- *gamma*: Flying speed of drones (km/h).
- *MT*: Maximum allowed drone route time per day (hours).
- *delta*: Maximum distance a drone can travel without battery replacement (km). Based on drones developed by [NU Flight Services (2020)](https://www.nordicunmanned.com/solutions#cargo) and [Skyports Drone Services (2023)](https://skyportsdroneservices.com/delivery).
- *Speed ship*: Average speed of ships (knots).
- *Demand days*: Number of days with due dates considered when scheduling demand in the decomposition of the second stage of the matheuristic.
- *Overlap_final*: Number of overlapping days used in the rolling horizon procedure of the matheuristic.
- *Rolling horizon*: Number of days without demand in the decomposition of the planning horizon. These days are considered demand-free.
- *Overlap_ini*: Number of overlapping days used during the warm-up phase of the matheuristic.
- *CB*: Base cost for the quadratic penalty function that depends on the number of late units and the number of delayed days.

---

## Case Study Data

The `case_study` folder contains datasets derived from a real-world inspired scenario.

Four demand distributions are considered:

- `demand_distribution_1`
- `demand_distribution_2`
- `demand_distribution_3`
- `demand_distribution_4`

Each directory represents a different demand scenario used to evaluate the robustness of the model. The demand distributions are generated by randomly allocating the total demand of 400 units across parts, customers, and days.

---

## Numerical Experiments

The `numerical_experiments` folder contains synthetic benchmark instances designed to evaluate the scalability and computational performance of the optimization model and the proposed matheuristic.

Two instance sizes are provided:

### Small instances
- `small_instance_1`
- `small_instance_2`

### Medium instances
- `medium_instance_1`
- `medium_instance_2`

These datasets enable controlled evaluation of algorithmic performance under different problem sizes.

---

## Data Format

All datasets are provided as **comma-separated values (CSV)** files.

The files can be loaded using most scientific computing tools, including:

- Python (pandas)
- R
- MATLAB
- Julia
- Excel

---

## Reproducibility

The dataset is structured such that each instance folder contains all necessary parameters required to reproduce the computational experiments described in the associated [article](https://doi.org/10.1080/00207543.2025.2540454).

Users can select any instance directory and directly load the CSV files as input to their implementation of the model.

---

## License

This dataset is distributed under the terms specified in the `LICENSE` file.

---

## Citation

If you use this dataset in your research, please cite it using the information provided in `CITATION.cff`.

---

## Contact

For questions or issues related to the dataset, please open a GitHub issue in this repository. For further information about the research, please refer to the associated [article](https://doi.org/10.1080/00207543.2025.2540454).
