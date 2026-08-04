#!/bin/sh

poetry run alembic upgrade head

#Starts the application
poetry run uvicorn --host 0.0.0.0 --port 8000 lucro_admin.api.app:app