gen_migrations:
	uv run alembic revision --autogenerate -m "$(msg)"

alembic_upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1

# Docker commands
docker_gen_migrations:
	docker compose -f docker-compose.dev.yml exec algorithmicdev-backend uv run alembic revision --autogenerate -m "$(msg)"

docker_alembic_upgrade:
	docker compose -f docker-compose.dev.yml exec algorithmicdev-backend uv run alembic upgrade head

docker_downgrade:
	docker compose -f docker-compose.dev.yml exec algorithmicdev-backend uv run alembic downgrade -1
