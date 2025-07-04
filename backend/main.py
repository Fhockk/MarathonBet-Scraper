"""
Entry point for the MarathonBet service.

This module:
- Initializes and configures the FastAPI app
- Sets up CORS middleware
- Includes routers for API versioning
- Runs both the API server and background services concurrently
"""

import asyncio
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from hypercorn.asyncio import serve

from app.api.v1.dev_routers import dev_router
from app.api.v1.events import events_router
from app.common.settings import settings
from app.services import run_services

# Create the FastAPI app instance
app = FastAPI(title="MarathonBet Service")

# CORS middleware configuration (dev mode: allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # that`s for dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes (v1)
app.include_router(events_router)
app.include_router(dev_router)


async def main():
    tasks = [
        serve(app, settings.hypercorn_config),    # Starts the ASGI server
        run_services()                            # Starts background async services
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # Compatibility fix for Windows event loop policy
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the main async function
    asyncio.run(main())
