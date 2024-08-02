#!/usr/bin/env bash
# Exit on error
set -o errexit

./scripts/build-frontend.sh
./scripts/build-backend.sh
