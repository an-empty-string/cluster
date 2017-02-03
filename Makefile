test:
	coverage run --include="cluster/*" --omit="cluster/test/*" -m pytest --fulltrace
	coverage report
	coverage html

devdependencies:
	pip install --user coverage pytest
