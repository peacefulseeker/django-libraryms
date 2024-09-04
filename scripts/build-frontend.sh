cd frontend
pnpm install --frozen-lockfile
pnpm run build

rm -rf ../src/core/assets/frontend/
mkdir -p ../src/core/assets/
cp -r dist/ ../src/core/assets/frontend/
