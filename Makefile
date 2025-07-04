.PHONY: build up down restart logs install

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d --build

logs:
	docker compose logs -f

install:
	python -m venv venv && source venv/bin/activate && pip install -r backend/requirements.txt
