# One image per service. Build from the repository root:
#   docker build -f services/service-template/Dockerfile -t service-template .
# Base images come from ECR Public (anonymous pulls); the tag follows .node-version.
FROM public.ecr.aws/docker/library/node:24.21.0-bookworm-slim AS build
WORKDIR /repo
RUN corepack enable
COPY . .
RUN pnpm install --frozen-lockfile --filter "service-template..." \
  && pnpm --filter service-template run build \
  && pnpm --filter service-template deploy --legacy --prod /out

FROM public.ecr.aws/docker/library/node:24.21.0-bookworm-slim
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build /out /app
USER node
EXPOSE 8080
CMD ["node", "dist/index.js"]
