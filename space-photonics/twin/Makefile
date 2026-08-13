# Space Photonics Digital Twin - Makefile

.PHONY: help install test demo benchmark clean lint format

help:
	@echo "Space Photonics Digital Twin"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install package and dependencies"
	@echo "  install-dev  Install with development dependencies"
	@echo "  test         Run test suite"
	@echo "  demo         Run demonstration simulation"
	@echo "  benchmark    Run performance benchmarks"
	@echo "  validate     Validate against standalone calculator"
	@echo "  sweep        Run parameter sweep"
	@echo "  monte-carlo  Run Monte Carlo analysis"
	@echo "  clean        Clean generated files"
	@echo "  lint         Run linter (flake8)"
	@echo "  format       Format code (black)"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

demo:
	python demo.py

benchmark:
	python benchmark.py --scenarios

validate:
	python validate.py

sweep:
	python parameter_sweep.py

monte-carlo:
	python monte_carlo.py --runs 100

clean:
	rm -rf __pycache__ *.pyc .pytest_cache
	rm -rf results/ plots/ sweep_results/ monte_carlo_results/
	rm -f *.jsonl *.csv

lint:
	flake8 *.py tests/

format:
	black *.py tests/
