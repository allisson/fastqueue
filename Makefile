test:
	FASTQUEUE_TESTING='true' poetry run pytest -v

lint:
	poetry run pre-commit run --all-files

run-db:
	docker run --name postgres-fastqueue \
		--restart unless-stopped \
		-e POSTGRES_USER=fastqueue \
		-e POSTGRES_PASSWORD=fastqueue \
		-e POSTGRES_DB=fastqueue \
		-p 5432:5432 \
		-d postgres:14-alpine

rm-db:
	docker kill $$(docker ps -aqf name=postgres-fastqueue)
	docker container rm $$(docker ps -aqf name=postgres-fastqueue)

build-image:
	docker build --rm -t fastqueue .

run-server:
	poetry run python fastqueue/main.py server

run-db-migrate:
	poetry run python fastqueue/main.py db-migrate

create-auto-migration:
	poetry run alembic revision --autogenerate -m "Auto generated"

.PHONY: test lint run-db rm-db build-image run-server run-db-migrate create-auto-migration
