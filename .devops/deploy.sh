#!/bin/bash
set -e
if [[ "$1" == "" ]]; then
  echo "ERROR: env not provided."
  exit 1
fi
ENVDIR=$1
VERSION="$(cat ~/.version)"
VERSION_SIMPLE=$(cat ~/.version | xargs | cut -f1 -d"+")
VERSION_PEP440=$(cat ~/.version440)
export TIMESTAMP="$(date --rfc-3339=seconds | sed 's/ /T/')"
if [[ "$ENVDIR" == "production" ]]; then
  echo 'Deploying to PyPI...'
  # Update setuptools so we have a version that supports Markdown READMEs.
  # twine is also required.
  pip install -U setuptools twine
  # Make and upload the distribution.
  python setup.py sdist
  twine upload dist/*
fi
