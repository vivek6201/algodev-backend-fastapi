gen_migrations:
	alembic revision --autogenerate -m "$(msg)"

alembic_upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1
