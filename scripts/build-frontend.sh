cd frontend
pnpm install --frozen-lockfile
pnpm run build

cp -a dist/. ../src/core/assets/frontend/
cp dist/index.html ../src/core/templates/vue-index.html
