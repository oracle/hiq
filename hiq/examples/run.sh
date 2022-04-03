#!/bin/bash

python -m pip install -r ../requirements-int.txt

for i in $(find . -name main_driver*.py); do
  echo $i
  python $i
done
