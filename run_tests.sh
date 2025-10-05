#!/bin/bash
poetry run coverage run -m pytest
poetry run coverage report --fail-under=100