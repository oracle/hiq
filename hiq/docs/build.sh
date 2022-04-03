#!/bin/bash
set -e

GIT_ROOT=$(git rev-parse --show-toplevel)
cd "$GIT_ROOT"/hiq/docs

make clean
make latexpdf

if [ -e "$GIT_ROOT/hiq/docs/build/latex/hiq-amodernobservabilitysystem.pdf" ]; then
    mv "$GIT_ROOT/hiq/docs/build/latex/hiq-amodernobservabilitysystem.pdf" "$GIT_ROOT/hiq/docs/hiq.pdf"
fi
