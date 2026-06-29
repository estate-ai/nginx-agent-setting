FROM node:22-alpine AS base

RUN apk add --no-cache libc6-compat

FROM base AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ARG BETTER_AUTH_URL
ENV BETTER_AUTH_URL=${BETTER_AUTH_URL}

ARG BETTER_AUTH_SECRET
ENV BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}

ARG AUTHENTIK_CLIENT_ID
ENV AUTHENTIK_CLIENT_ID=${AUTHENTIK_CLIENT_ID}

ARG AUTHENTIK_CLIENT_SECRET
ENV AUTHENTIK_CLIENT_SECRET=${AUTHENTIK_CLIENT_SECRET}

ARG AUTHENTIK_DISCOVERY_URL
ENV AUTHENTIK_DISCOVERY_URL=${AUTHENTIK_DISCOVERY_URL}

ARG NEXT_PUBLIC_API_ORIGIN
ENV NEXT_PUBLIC_API_ORIGIN=${NEXT_PUBLIC_API_ORIGIN}

ARG AGENT_ASSISTANT_ID
ENV AGENT_ASSISTANT_ID=${AGENT_ASSISTANT_ID}

RUN npm run build

FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

RUN addgroup --system --gid 1001 nodejs \
  && adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

CMD ["node", "server.js"]
