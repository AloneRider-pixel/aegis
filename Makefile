.PHONY: dev test lint docker-build clean

dev:
	docker compose up -d

dev-down:
	docker compose down

test:
	docker compose exec backend pytest tests/ -v

lint:
	docker compose exec backend ruff check app/

migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m scripts.seed_knowledge

demo:
	@echo "Triggering demo scenario..."
	@curl -s -X POST http://localhost:8000/api/simulator/scenarios/db-connection-exhaustion/trigger \
		-H "Authorization: Bearer $$(curl -s -X POST http://localhost:8000/api/auth/login \
		-H 'Content-Type: application/json' \
		-d '{"email":"admin@aegis.io","password":"admin123"}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')" | python3 -m json.tool

eval:
	docker compose exec backend python -m scripts.run_evaluation

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/**/__pycache__
