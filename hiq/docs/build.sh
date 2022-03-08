#!/bin/bash
set -e

GIT_ROOT=$(git rev-parse --show-toplevel)
cd "$GIT_ROOT"/hiq/docs

#make clean
make html
cp -Rf build/html/* html/
#sudo docker run --rm --name nginx -v /home/opc/hiq/hiq/docs/html:/usr/share/nginx/html:ro -p 8080:80 -d nginx
