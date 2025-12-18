.PHONY: help dev build test lint format clean install

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)LingoQuesto Frontend - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Development
dev: ## Run all apps in development mode
	pnpm dev

dev-student: ## Run student-teacher app in development mode
	pnpm dev:student-teacher

dev-institutional: ## Run institutional app in development mode
	pnpm dev:institutional

# Build
build: ## Build all apps
	pnpm build

build-student: ## Build student-teacher app
	pnpm build:student-teacher

build-institutional: ## Build institutional app
	pnpm build:institutional

# Testing
test: ## Run all tests
	pnpm test

test-unit: ## Run unit tests
	pnpm test:unit

test-e2e: ## Run e2e tests
	pnpm test:e2e

# Linting & Formatting
lint: ## Run linter
	pnpm lint

lint-fix: ## Fix linting issues
	pnpm lint:fix

format: ## Format code with Prettier
	pnpm format

format-check: ## Check code formatting
	pnpm format:check

typecheck: ## Run TypeScript type checking
	pnpm typecheck

# GraphQL
graphql-codegen: ## Generate GraphQL types
	pnpm graphql:codegen

graphql-watch: ## Watch and generate GraphQL types
	pnpm graphql:watch

# i18n
i18n-validate: ## Validate translations
	pnpm i18n:validate

i18n-extract: ## Extract translation keys
	pnpm i18n:extract

i18n-types: ## Generate i18n types
	pnpm i18n:types

i18n-scan: ## Scan for hardcoded strings
	pnpm i18n:scan

i18n-replace: ## Replace hardcoded strings
	pnpm i18n:replace

# Installation & Cleanup
install: ## Install dependencies
	pnpm install

clean: ## Clean build artifacts (turbo cache)
	pnpm clean

clean-deps: ## Remove all node_modules
	@echo "$(YELLOW)Removing node_modules...$(NC)"
	find . -name "node_modules" -type d -prune -exec rm -rf '{}' +
	@rm -rf ./test-results
	@rm -rf ./playwright-report
	@rm -rf ./.turbo
	@echo "$(GREEN)✓ node_modules removed$(NC)"

clean-build: ## Remove all build artifacts
	@echo "$(YELLOW)Removing build artifacts...$(NC)"
	find . -name ".nuxt" -type d -prune -exec rm -rf '{}' +
	find . -name ".output" -type d -prune -exec rm -rf '{}' +
	find . -name "dist" -type d -prune -exec rm -rf '{}' +
	find . -name ".turbo" -type d -prune -exec rm -rf '{}' +
	find . -name "coverage" -type d -prune -exec rm -rf '{}' +
	find . -name ".vite" -type d -prune -exec rm -rf '{}' +
	@echo "$(GREEN)✓ Build artifacts removed$(NC)"

clean-cache: ## Remove all cache files
	@echo "$(YELLOW)Removing cache files...$(NC)"
	find . -name ".cache" -type d -prune -exec rm -rf '{}' +
	find . -name ".eslintcache" -type f -delete
	pnpm store prune
	@echo "$(GREEN)✓ Cache files removed$(NC)"

clean-all: clean-build clean-deps clean-cache ## Remove everything (node_modules, build, cache)
	@echo "$(GREEN)✓ Complete cleanup finished$(NC)"

clean-install: clean-all install ## Clean everything and reinstall dependencies
	@echo "$(GREEN)✓ Clean install completed$(NC)"

reset: clean-all install graphql-codegen ## Complete reset: clean, install, and setup
	@echo "$(GREEN)✓ Project reset completed$(NC)"

# Shortcuts
ci: lint typecheck test ## Run CI checks (lint, typecheck, test)
	@echo "$(GREEN)✓ All CI checks passed$(NC)"

pre-commit: lint-fix format typecheck ## Run pre-commit checks
	@echo "$(GREEN)✓ Pre-commit checks completed$(NC)"

setup: install graphql-codegen i18n-types ## Initial project setup
	@echo "$(GREEN)✓ Project setup completed$(NC)"
