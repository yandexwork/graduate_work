up:
	docker compose -f ./auth/docker-compose.yml up -d --build; \
	docker compose up -d --build

down:
	docker compose -f ./auth/docker-compose.yml down; \
	docker compose down