# Dockerfile for institutional (Vue + Vite)
FROM node:20-alpine AS base

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
COPY apps/institutional/package.json ./apps/institutional/
COPY packages/*/package.json ./packages/*/

# Install dependencies
RUN pnpm install --frozen-lockfile --filter=@lq/institutional...

# ========================================
# Stage 2: Build the application
# ========================================
FROM base AS builder

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/apps/institutional/node_modules ./apps/institutional/node_modules
COPY --from=deps /app/packages ./packages

# Copy source code
COPY turbo.json ./
COPY apps/institutional ./apps/institutional

# Build the application
RUN pnpm turbo run build --filter=@lq/institutional

# ========================================
# Stage 3: Production with Nginx
# ========================================
FROM nginx:alpine AS runner

# Copy built static files
COPY --from=builder /app/apps/institutional/dist /usr/share/nginx/html

# Copy nginx configuration
COPY apps/institutional/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
