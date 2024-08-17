cd frontend
pnpm install --frozen-lockfile
pnpm run build

cp -r dist/ ../src/core/assets/frontend/
cp ../src/core/assets/frontend/index.html ../src/core/templates/vue-index.html
