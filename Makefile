.PHONY: venv
venv:  # make venv and install requirements
	if [ ! -d .venv ]; then python3 -m venv .venv; fi
	.venv/bin/python -m pip install jinja2==3.1.5 seaborn==0.13.2

.PHONY: parse-results
parse-results:  # parse results
	.venv/bin/python scripts/convert_results_to_json.py results --output=results/parsed.json

.PHONY: generate-report
generate-readme:  # generate readme
	.venv/bin/python
