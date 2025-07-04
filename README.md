# MarathonBet Parser

Full-stack app for scraping and viewing finished sports events from marathonbet.com.

> Frontend and Backend are intentionally kept in a single repository for demonstration purposes.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, aiohttp, Redis, Hypercorn
- **Frontend:** React, TypeScript
- **DevOps:** Docker, Docker Compose, Makefile

## Features

- Async scraper with Redis storage
- FastAPI endpoints to fetch events by time, sport, and keyword
- React UI with filtering and results table
- Dev endpoints for managing background services

## Usage

### Run with Docker

```bash
make build    # Build all images
make run      # Start backend, frontend, Redis
```



### URLs

- Frontend: http://localhost:3000
- API: http://localhost:8080/v1/get_results


### Query example:

- GET /v1/get_results?hours=24&sport=Football&keyword=juventus


## Dev without Docker

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```








