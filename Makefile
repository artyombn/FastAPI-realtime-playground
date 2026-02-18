startapp-dev:
	docker compose -f docker-compose.dev.yml up --build

startapp-prod:
	docker build -t fastapi-app:latest . \
	&& docker compose -f docker-compose.prod.yml up -d

check-ip:
	docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fastapi_app
	#docker inspect fastapi_app

start-postgres:
	docker compose -f docker-compose.dev.yml up postgres

test:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test_web
	docker compose -f docker-compose.test.yml down -v

test-postgres:
	docker compose -f docker-compose.test.yml up test_db

test-local:
	pytest -vv --maxfail=5

fixtures:
	pytest --fixtures

postgres_env:
	docker inspect postgres_test | grep -E "DB_(USER|PASSWORD|HOST_LOCAL|PORT|NAME)"