docker-compose-dev:
	docker compose -f docker-compose.dev.yml up --build

docker-compose-prod:
	docker build -t fastapi-app:latest . \
	&& docker compose -f docker-compose.prod.yml up -d

check-ip:
	docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' fastapi_app
	#docker inspect fastapi_app