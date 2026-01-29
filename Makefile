.PHONY: dev-deps dev-down

dev-deps:
	cd infra && docker compose up -d

dev-down:
	cd infra && docker compose down
