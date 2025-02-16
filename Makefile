.PHONY: venv
venv:  # make venv and install requirements
	if [ ! -d .venv ]; then python3 -m venv .venv; fi
	.venv/bin/python -m pip install jinja2==3.1.5 seaborn==0.13.2

.PHONY: parse-results
parse-results: scripts/convert_results_to_json.py results/*.txt results/*.log    # parse results
	.venv/bin/python scripts/convert_results_to_json.py results --output=results/parsed.json

.PHONY: readme
readme: scripts/generate_readme.py README.jinja2 parse-results  # generate readme
	.venv/bin/python scripts/generate_readme.py --results_file=results/parsed.json
