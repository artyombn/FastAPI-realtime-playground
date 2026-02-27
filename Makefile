app:
	docker compose -f docker-compose.dev.yml up --build

users-postgres:
	docker compose -f docker-compose.dev.yml up users_postgres

products-redis:
	docker compose -f docker-compose.dev.yml up products_redis

test-users-docker:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test_users_app
	docker compose -f docker-compose.test.yml down -v

test-users-postgres:
	docker compose -f docker-compose.test.yml up test_users_db

test-users-local:
	#cd users && pytest -s -vv --tb=long --maxfail=5
	cd users && pytest --maxfail=5

check-ip:
	docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fastapi_app
	#docker inspect fastapi_app

fixtures:
	pytest --fixtures

postgres_env:
	docker inspect postgres_test | grep -E "DB_(USER|PASSWORD|HOST_LOCAL|PORT|NAME)"

#startapp-prod:
#	docker build -t fastapi-app:latest . \
#	&& docker compose -f docker-compose.prod.yml up -d