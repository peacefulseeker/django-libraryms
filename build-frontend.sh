#!/usr/bin/env bash


cd frontend
pnpm install --frozen-lockfile
pnpm run build

cp dist/index.html ../src/core/templates/index.html
