"""
Development and debugging API endpoints.

This router provides internal tools for:
- Toggling full logging
- Starting/stopping/cleaning the Converter and Storage services
- Viewing internal debug info from Converter, Storage, and Scraper loop
"""

from fastapi import APIRouter
from starlette.responses import RedirectResponse

from app.common.logger import log
from app.common.settings import settings
from app.services import converter, storage, scraper_update_loop

dev_router = APIRouter(prefix="/v1/dev")


@dev_router.get("/logs", tags=["Dev"])
async def get_logs_status():
    """
    Returns the current status of FULL_LOGS setting.

    Returns:
        dict: {"FULL_LOGS": bool}
    """
    return {"FULL_LOGS": settings.FULL_LOGS}


@dev_router.patch("/logs", tags=["Dev"])
async def update_logs_status():
    """
    Toggles the FULL_LOGS setting at runtime.

    Returns:
        dict: {"full_logs": bool}
    """
    settings.FULL_LOGS = not settings.FULL_LOGS
    log("Update logs status to: " + str(settings.FULL_LOGS), force=True)
    return {"full_logs": settings.FULL_LOGS}


@dev_router.get("/converter", tags=["Dev"])
async def get_converter():
    """
    Returns debug info from the Converter service.

    Returns:
        dict: Current state of the converter queue and last update time.
    """
    return converter.debug_info()


@dev_router.get("/converter/stop", tags=["Dev"])
async def stop_converter():
    """
    Stops the converter loop.

    Returns:
        Redirect to the /converter debug info view.
    """
    converter.stop_processing()
    return RedirectResponse(url="/v1/dev/converter")


@dev_router.get("/converter/start", tags=["Dev"])
async def start_converter():
    """
    Starts the converter loop.

    Returns:
        Redirect to the /converter debug info view.
    """
    converter.start_processing()
    return RedirectResponse(url="/v1/dev/converter")


@dev_router.get("/converter/clean", tags=["Dev"])
async def clean_converter():
    """
    Clears the converter queue and resets state.

    Returns:
        Redirect to the /converter debug info view.
    """
    converter.clean()
    return RedirectResponse(url="/v1/dev/converter")


@dev_router.get("/storage", tags=["Dev"])
async def get_storage():
    """
    Returns debug info from the Storage service.

    Returns:
        dict: Current state of the storage queue and last update time.
    """
    return storage.debug_info()


@dev_router.get("/storage/stop", tags=["Dev"])
async def stop_storage():
    """
    Stops the storage loop.

    Returns:
        Redirect to the /storage debug info view.
    """
    storage.stop_processing()
    return RedirectResponse(url="/v1/dev/storage")


@dev_router.get("/storage/start", tags=["Dev"])
async def start_storage():
    """
    Starts the storage loop.

    Returns:
        Redirect to the /storage debug info view.
    """
    storage.start_processing()
    return RedirectResponse(url="/v1/dev/storage")


@dev_router.get("/storage/clean", tags=["Dev"])
async def clean_storage():
    """
    Clears the storage queue and resets state.

    Returns:
        Redirect to the /storage debug info view.
    """
    storage.clean()
    return RedirectResponse(url="/v1/dev/storage")


@dev_router.get("/scraper", tags=["Dev"])
async def get_scraper_info():
    """
    Returns debug info from the scraper loop manager.

    Returns:
        dict: Contains status, retry interval, and last iteration timestamp.
    """
    return scraper_update_loop.debug_info()
