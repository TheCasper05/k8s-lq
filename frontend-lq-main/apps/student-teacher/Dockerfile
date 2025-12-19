# Dockerfile for student-teacher (Nuxt 4)
FROM node:24-alpine AS base

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Set working directory
WORKDIR /app

# ========================================
# Stage 1: Install dependencies
# ========================================
FROM base AS deps

# Copy package files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/student-teacher/package.json ./apps/student-teacher/
COPY packages ./packages

# Install dependencies
RUN pnpm install --frozen-lockfile --filter=@lq/student-teacher...

# ========================================
# Stage 2: Build the application
# ========================================
FROM base AS builder

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/student-teacher/node_modules ./apps/student-teacher/node_modules
COPY --from=deps /app/packages ./packages
COPY --from=deps /app/package.json ./package.json
COPY --from=deps /app/pnpm-lock.yaml ./pnpm-lock.yaml
COPY --from=deps /app/pnpm-workspace.yaml ./pnpm-workspace.yaml

# Copy source code
COPY turbo.json tsconfig.json ./
COPY apps/student-teacher ./apps/student-teacher

# Build the application
RUN pnpm turbo run build --filter=@lq/student-teacher

# ========================================
# Stage 3: Production runtime
# ========================================
FROM base AS runner

# Set NODE_ENV
ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nuxtjs

# Copy built application
COPY --from=builder --chown=nuxtjs:nodejs /app/apps/student-teacher/.output ./apps/student-teacher/.output

# Switch to non-root user
USER nuxtjs

# Expose port
EXPOSE 3000

# Set working directory to the app
WORKDIR /app/apps/student-teacher

# Start the application
CMD ["node", ".output/server/index.mjs"]