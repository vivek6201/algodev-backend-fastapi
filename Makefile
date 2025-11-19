gen_migrations:
	alembic revision --autogenerate -m "$(msg)"

alembic-upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1


