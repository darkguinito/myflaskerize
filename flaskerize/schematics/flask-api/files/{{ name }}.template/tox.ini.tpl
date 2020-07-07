[flake8]
ignore=E501,E221

[bdist_wheels]
universal = True

[tool:pytest]
log_print = True
junit_family = True

[coverage:run]
branch = True
source = app

[coverage:report]
ignore_errors = True
show_missing = True

[coverage:xml]
output = coverage/coverage.xml

[coverage:html]
directory = coverage/htmlcov
title = "Coverage {{ name }} report"

