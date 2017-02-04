localtest:
	coverage run --include="cluster/*" --omit="cluster/test/*" -m pytest --fulltrace
	coverage report
	coverage html

test:
	coverage run --include="cluster/*" --omit="cluster/test/*" -m pytest --fulltrace
	coverage report
	codeclimate-test-reporter

devdependencies:
	pip install coverage pytest codeclimate-test-reporter
	python setup.py develop
