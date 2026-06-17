| **Project** | **Documentation** | **Build Status** | **Code Quality** | **Coverage** |
|:-----------:|:-----------------:|:----------------:|:----------------:|:------------:|
| **fem4grav** | [![ReadTheDocs](https://readthedocs.org/projects/fem4grav1/badge/?version=latest)](https://fem4grav1.readthedocs.io/en/latest/?badge=latest) | [![fem4grav CI](https://github.com/TagniAyissi/fem4grav1/actions/workflows/python.yml/badge.svg)](https://github.com/TagniAyissi/fem4grav1/actions/workflows/python.yml) | [![Codacy Badge](https://app.codacy.com/project/badge/Grade/1d8921d71d55486591c1ee9b7d065690)](https://app.codacy.com/gh/TagniAyissi/fem4grav1/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade) | [![codecov](https://codecov.io/github/TagniAyissi/fem4grav1/graph/badge.svg?token=ES25ABNV76)](https://codecov.io/github/TagniAyissi/fem4grav1) |

<br>

<p align="left">
  <a href="https://github.com/TagniAyissi/fem4grav1/pulls"><img src="https://img.shields.io/github/issues-pr/TagniAyissi/fem4grav1.svg?style=flat" alt="GitHub pull-requests"></a>
  <a href="https://github.com/TagniAyissi/fem4grav1/issues"><img src="https://img.shields.io/github/issues/TagniAyissi/fem4grav1.svg?style=flat" alt="GitHub issues"></a>
</p>

<p align="left">
  <a href="https://github.com/TagniAyissi/fem4grav1/stargazers"><img src="https://img.shields.io/github/stars/TagniAyissi/fem4grav1.svg?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/TagniAyissi/fem4grav1/watchers"><img src="https://img.shields.io/github/watchers/TagniAyissi/fem4grav1.svg?style=social" alt="GitHub watchers"></a>
</p>

<p align="left">
  <img src="images/fem4grav1_logo.png" alt="Logo fem4grav1" width="360">
</p>

# fem4grav v0.0.1

## Table of Contents
- [Overview](#overview)
- [Theory](#theory)
- [Workflow](#workflow)
- [Installation](#installation)
- [Usage](#usage)
- [Tests](#tests)
- [Contributing](#contributing)
- [License](#license)

## Overview

**fem4grav** is a geophysical processing tool designed for the regional-residual separation of gravity anomalies. Based on the Finite Element Method (FEM) using 8-node serendipity elements, this package allows for the isolation of local anomalies of geological interest from regional gravity data.


## Theory

The Bouguer anomaly observed in the field is the sum of two components:

> **Observed Anomaly = Regional Anomaly + Residual Anomaly**

- **The regional anomaly** is a long-wavelength background field caused by deep geological structures.
- **The residual anomaly** is a short-wavelength signal (local signal), often caused by shallow, superficial geological structures of direct interest for exploration.

The regional field is estimated through interpolation of boundary conditions using eight-node serendipity finite elements. The residual anomaly is then obtained by simple subtraction of this regional field from the observed Bouguer anomaly.

## Workflow

```mermaid
graph LR;

A["Input Data<br><br>Longitude<br>Latitude<br>Bouguer anomaly"]

-->B["Spatial Interpolation<br><br>Cubic grid reconstruction"]

-->C["Boundary Extraction<br><br>FEM constraints"]

-->D["8-Node FEM<br><br>Serendipity shape functions"]

-->E["Regional Field<br><br>Field reconstruction"]

-->F["Residual Computation<br><br>Observed − Regional"]

-->G["Output Results<br><br>Observed / Regional / Residual maps"]

style A fill:#dff2ff
style B fill:#e8f5e9
style C fill:#fff3e0
style D fill:#f3e5f5
style E fill:#ede7f6
style F fill:#ffebee
style G fill:#e0f2f1

```



## Installation

**Python version supported:** ![Python version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)

To install the project and all required dependencies (`numpy`, `scipy`, `matplotlib`), navigate to the root of the repository and run the appropriate command for your operating system:

**With Make (Linux / macOS)**
```bash
make install
```
**For Windows users (or alternative developer mode)**
```bash
pip install -e .[dev]
```
## Usage

To run the calculation on the provided Campi Flegrei dataset:

**Automated method (Linux / macOS)**
```bash
make run
```
This will automatically create the `results/` directory, execute fem4grav on the Flegrei.txt data, and save all generated maps into the `images/` folder.

**Command Line method (Windows / Any OS)**

If you want to apply fem4grav to your own Bouguer anomaly text files, you can use the direct CLI command. Your text file must contain exactly three columns (Longitude, Latitude, Anomaly).
Ensure that the destination folders (`results/` and `images/`) exist before running the command, or create them manually.

Example of a manual execution:
```bash
fem4grav data/Flegrei.txt --irow 101 --icol 101 --output results/flegrei.npz --table results/flegrei_table.txt --save-plot images/flegrei_maps.png
```
**To view all available options and help**
```bash
fem4grav --help
```

**Execution with Snakemake**

To automate your calculations and easily reproduce them when modifying a parameter, you can use the Snakemake workflow manager.

**Step A:** Install Snakemake:
```bash
pip install snakemake
```
**Step B:** Modify the project parameters by opening and editing the [config.yaml](https://github.com/TagniAyissi/fem4grav1/blob/main/config.yaml) file.

**Step C:** Launch the automated analysis pipeline with a specified number of CPU cores:

```bash
snakemake --cores 1
```
## Tests

To verify that the installation was successful and the computations are accurate, run the unit test suite:

**For Linux / macOS users**
```bash
make test
```
**For Windows users**
```bash
python -m pytest tests/ -v --cov=fem4grav --cov-report=term-missing
```

## Contributing

The project is open to contributions and suggestions, Just fill an issue or a pull request.
## License

The `fem4grav` package is licensed under the MIT [License](https://github.com/TagniAyissi/fem4grav1/blob/main/LICENSE).