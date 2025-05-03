.PHONY: dev cli fmt test db-init migrations run vrun vtest
dev: ; poetry run uvicorn app.main:app --reload
cli: ; poetry run python -m app.cli.main
fmt: ; poetry run black . && poetry run isort .
test:; poetry run pytest -q
db-init: ; ./scripts/init_db.sh
migrations: ; poetry run alembic revision --autogenerate -m "$(m)" 
run: ; poetry run python -m app.cli
vrun: ; poetry run python -m app.cli.run_mode_voice
vtest:
	poetry run python -c "import asyncio, sys; from app.services.voice import speak; asyncio.run(speak(sys.argv[1] if len(sys.argv)>1 else 'test'))" $(filter-out $@,$(MAKECMDGOALS)) 