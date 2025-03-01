all: README.md

.PHONY: venv
venv:  # make venv and install requirements
	if [ ! -d .venv ]; then python3 -m venv .venv; fi
	.venv/bin/python -m pip install jinja2==3.1.5 seaborn==0.13.2

.PHONY: parsed.json
parsed.json: results/parsed.json

results/parsed.json: scripts/convert_results_to_json.py results/*.txt results/*.log  # parse results
	.venv/bin/python scripts/convert_results_to_json.py results --output=results/parsed.json

README.md: scripts/generate_readme.py README.jinja2 results/parsed.json  # generate readme
	.venv/bin/python scripts/generate_readme.py --results_file=results/parsed.json

.PHONY: lint
lint:  # lint the code
	pre-commit run --all-files
