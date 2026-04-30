FROM node:20-alpine
WORKDIR /app
COPY frontend/package.json frontend/pnpm-workspace.yaml ./
COPY frontend/tsconfig.base.json ./tsconfig.base.json
COPY frontend/packages ./packages
COPY frontend/apps/portal-shell ./apps/portal-shell
RUN corepack enable && pnpm install
CMD ["pnpm", "--filter", "@astraflow/portal-shell", "dev"]
