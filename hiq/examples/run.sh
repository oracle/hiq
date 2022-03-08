#!/bin/bash

for i in $(find . -name main_driver*.py); do
  echo $i
  python $i
done
