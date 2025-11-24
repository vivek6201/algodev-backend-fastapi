gen_migrations:
	uv run alembic revision --autogenerate -m "$(msg)"

alembic_upgrade:
	uv run alembic upgrade head

downgrade:
	uv run alembic downgrade -1
