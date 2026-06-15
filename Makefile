# Configurable variables
PYTHON     ?= python
PIP        ?= pip
DATA        = data/Flegrei.txt
IROW        = 75
ICOL        = 101
METHOD      = cubic
OUTPUT_NPZ  = results/flegrei.npz
OUTPUT_TXT  = results/flegrei_table.txt
PLOT_FILE   = images/flegrei_maps.png

.PHONY: help install install-dev test lint run docs clean


# help : display available targets
help:
   @echo ""
        @echo "fem4grav — Makefile"
        @echo "==================="
        @echo ""
        @echo "  make install       Install the package (user mode)"
        @echo "  make install-dev   Install in developer mode (with tools)"
        @echo "  make test          Run unit tests (pytest)"
        @echo "  make lint          Check Python syntax (flake8)"
        @echo "  make run           Run FEM separation on Flegrei.txt"
        @echo "  make docs          Build HTML documentation (Sphinx)"
        @echo "  make clean         Remove generated files"
        @echo ""


# install : standard installation
install:
 		$(PIP) install --upgrade pip
        $(PIP) install -r requirements.txt
        $(PIP) install .


# install-dev : developer installation with all tools
install-dev:
        $(PIP) install --upgrade pip
        $(PIP) install -r requirements.txt
        $(PIP) install -e ".[dev]"

# test : run tests with code coverage
test:
        $(PYTHON) -m pytest tests/ -v --cov=fem4grav --cov-report=term-missing

# lint : check Python syntax errors
lint:
        $(PYTHON) -m flake8 fem4grav/ tests/ \
            --count --select=E9,F63,F7,F82 \
            --show-source --statistics

# run : FEM separation on real Campi Flegrei data
run: results images
        $(PYTHON) -m fem4grav $(DATA) \
            --irow $(IROW) \
            --icol $(ICOL) \
            --method $(METHOD) \
            --output $(OUTPUT_NPZ) \
            --table $(OUTPUT_TXT) \
            --save-plot $(PLOT_FILE) \
            --no-plot

# docs : build Sphinx documentation
docs:
		$(PIP) install -r docs/requirements.txt
        cd docs && $(MAKE) html

# Create output folders if missing
results:
        mkdir -p results

images:
        @rem The images/ folder already exists (contains fem4grav.png)

# clean : clean generated files
clean:
        rm -rf results/
        rm -rf docs/_build/
        rm -rf __pycache__/ fem4grav/__pycache__/ tests/__pycache__/
        rm -rf *.egg-info/ .pytest_cache/ .coverage htmlcov/
        find . -name "*.pyc" -delete
        find . -name "*.pyo" -delete
